from collections import UserDict
from typing import Optional

from collections import Container

import yaml
from pyaml_env import parse_config
from utils import get_nested_value
from models import AppSetting
from api import Api
from constants import Service, CONFIG_DEFAULT_LOCATION, PATHS
# from utils import recursive_delete_dict_keys_from_obj


class Config(UserDict):
    def __init__(self, services: dict, data: Optional[dict] = None):
        super().__init__(self._create_appsettings(services, cfg=data))

    def test(self):
        res = {}
        for service, settings in self.items():
            l = {}
            for setting in settings:
                l[setting.resource] = setting.current_config
            res[service] = l
        return res

    @classmethod
    def from_yaml(cls, services: dict, filename: str = CONFIG_DEFAULT_LOCATION):
        """Create a Config from yaml."""
        cfg = parse_config(filename, default_value='')
        return cls(services, data=cfg)

    @classmethod
    def from_current(cls, services):
        return cls(services)

    @staticmethod
    def _create_appsettings(services: dict, cfg: Optional[dict] = None):
        """Get a Config from existing running services."""
        if not cfg:  # No config passed: initialize empty
            cfg = {k.value: {} for k in Service}

        def get_current_cfg(service: str, cfg: dict, address: str, port: int):
            api = Api(Service(service), address=address, port=port)
            return {path: AppSetting(get_nested_value(cfg[service], path), resource=path, api=api) for path in PATHS[service]}
            # for path in PATHS[service]:
            #     settings.append(AppSetting(get_nested_value(cfg[service], path), resource=path, api=api))
            # return settings

        config = {}
        for service, addr in services.items():
            print(f"{service=}")
            print(f"{addr=}")
            config[service] = get_current_cfg(service, cfg, addr['address'], addr['port'])

        return config

    # def apply(self, services: dict):
    #     """Apply a Config to running services."""
    #     for app in services:
    #         api = Api(Service(app), **services[app]).initialize()
    #         self._triage_and_apply(self[app], api)

    def to_file(self, filename: str = CONFIG_DEFAULT_LOCATION):
        """Dump the Config to a YAML file."""
        with open(filename, 'w') as file:
            yaml.dump(self.data, file)

