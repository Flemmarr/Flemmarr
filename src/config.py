from collections import UserDict
from typing import Union

import yaml
from pyaml_env import parse_config

from api import Api
from constants import Service, CONFIG_DEFAULT_LOCATION, UNWANTED_CFG_FIELDS, PATHS
from utils import recursive_delete_dict_keys_from_obj


class Config(UserDict):
    def __init__(self, data):
        self.services = [Service(app) for app in data.keys()]
        super().__init__(data)

    @classmethod
    def from_yaml(cls, filename: str = CONFIG_DEFAULT_LOCATION):
        """Create a Config from yaml."""
        # TODO: add ('id'?) keys for unconfigured list items, such that they can get deleted
        cfg = parse_config(filename, default_value='')
        return cls(cfg)

    @classmethod
    def from_existing(cls, services: dict):
        """Get a Config from existing running services."""
        def get_current_cfg(service: str, address: str, port: int):
            api = Api(Service(service), address=address, port=port).initialize()
            res = {}
            for path in PATHS[service]:
                value = api.get(path)
                recursive_delete_dict_keys_from_obj(value, UNWANTED_CFG_FIELDS)  # filter response
                for key in reversed(path[1:].split('/')):  # start turning paths into nested dicts
                    value = {key: value}
                res.update(value)
            return {service: res}

        config = {}
        for service, addr in services.items():
            config.update(get_current_cfg(service, addr['address'], addr['port']))
        return cls(config)

    def apply(self, services: dict):
        """Apply a Config to running services."""
        for app in services:
            api = Api(Service(app), **services[app]).initialize()
            self._triage_and_apply(self[app], api)

    def to_file(self, filename: str = CONFIG_DEFAULT_LOCATION):
        """Dump the Config to a YAML file."""
        with open(filename, 'w') as file:
            yaml.dump(self.data, file)

    def _triage_and_apply(self, obj: Union[dict, list], api: Api, resource: str = '') -> None:
        """Walk over all the (nested) Config items and apply their settings"""
        if isinstance(obj, dict):
            if any(isinstance(obj[key], (dict, list)) for key in obj):
                for key in obj:
                    self._triage_and_apply(obj[key], api, f"{resource}/{key}")
            else:
                api.update(resource, obj, 1)  # even non-list items have an id (e.g. config/ui)
        elif isinstance(obj, list):
            for id, item in enumerate(obj, start=1):  # *arr id's start at 1
                api.update(resource, item, id)
            self._delete_excess_items(resource, obj, api)

    @staticmethod
    def _delete_excess_items(resource: str, obj: list, api: Api) -> None:
        """Delete excess items if more are present than in the Config."""
        n_actual_resources = len(api.get(resource))
        if n_actual_resources > len(obj):
            for id in range(len(obj) + 1, n_actual_resources + 1):  # excluding start and including end
                api.delete(resource, id)
