from collections import UserDict

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
        # TODO: add ('id'?) keys for unconfigured list items, such that they can get deleted
        cfg = parse_config(filename, default_value='')
        return cls(cfg)

    @classmethod
    def from_current(cls, services: dict):
        def get_current_cfg(service: str, address: str, port: int):
            api = Api(Service(service), address=address, port=port).initialize()
            res = {}
            for path in PATHS[service]:
                value = api.get(path)
                recursive_delete_dict_keys_from_obj(value, UNWANTED_CFG_FIELDS)
                for key in reversed(path[1:].split('/')):
                    value = {key: value}
                res.update(value)
            return {service: res}

        config = {}
        for service, addr in services.items():
            config.update(get_current_cfg(service, addr['address'], addr['port']))
        return cls(config)

    def apply(self, services: dict):
        for app in services:
            api = Api(Service(app), **services[app]).initialize()
            self._triage_and_apply(self[app], api)

    def to_file(self, filename: str = CONFIG_DEFAULT_LOCATION):
        with open(filename, 'w') as file:
            yaml.dump(self.data, file)

    def _triage_and_apply(self, obj, api: Api, resource: str = ''):
        if isinstance(obj, dict):
            if any(isinstance(obj[key], (dict, list)) for key in obj):
                for key in obj:
                    self._triage_and_apply(obj[key], api, f"{resource}/{key}")
            else:
                api.edit(resource, obj, obj['id'])  # even non-list item has id (like config/ui)
        elif isinstance(obj, list):
            for item in obj:
                if 'id' not in item:  # all list items should have id's
                    raise
                api.edit(resource, item, item['id'])
            self._delete_excess_items(resource, obj, api)

    @staticmethod
    def _delete_excess_items(resource, obj, api: Api):
        max_config_id = max((item['id'] for item in obj), default=0)
        max_actual_id = max((item['id'] for item in api.get(resource)), default=-1)
        if max_actual_id > max_config_id:
            for id in range(max_config_id + 1, max_actual_id + 1):  # excluding start and including end
                api.delete(resource, id)
