import json
from collections import UserDict

import yaml
from pyaml_env import parse_config

from api import Api
from constants import Service, API_PATHS_LOCATION, BACKUP_DEFAULT_LOCATION, CONFIG_DEFAULT_LOCATION
from models import AppSetting
from utils import ComplexEncoder


class Config(UserDict):
    def __init__(self, data: dict, services: dict):
        base_cfg = parse_config(API_PATHS_LOCATION, default_value='')
        for service, location in services.items():
            api = Api(Service(service), address=location["address"], port=location["port"])
            base_cfg[service] = self._deep_update(base_cfg[service], data[service], api=api)
        super().__init__(base_cfg)

    @classmethod
    def from_yaml(cls, services: dict, filename: str = CONFIG_DEFAULT_LOCATION):
        new_config = parse_config(filename)
        return cls(new_config, services)

    @staticmethod
    def _deep_update(mapping: dict, updating_mapping: dict, api: Api, prefix: str = '') -> dict:
        for k, v in mapping.items():
            if k in updating_mapping and isinstance(v, dict):  # Nested settings (e.g. config/ui)
                mapping[k] = Config._deep_update(mapping[k], updating_mapping[k], api, prefix=f"/{k}")
            elif k in updating_mapping:  # key is in new config, and either list or dict
                if isinstance(updating_mapping[k], list):
                    mapping[k] = AppSetting(updating_mapping[k], resource=f"{prefix}/{k}", api=api)
                elif isinstance(updating_mapping[k], dict):
                    mapping[k] = AppSetting(resource=f"{prefix}/{k}", api=api, **updating_mapping[k])
            else:  # key is not configured in new config, empty AppSetting
                mapping[k] = AppSetting(resource=f"{prefix}/{k}", api=api)
        return mapping

    def apply(self):
        """Apply a Config to running services."""
        for app in self.values():
            for item in app.values():
                if isinstance(item, AppSetting):
                    item.apply()
                elif isinstance(item, dict):
                    for cfg_item in item.values():
                        cfg_item.apply()  # AppSetting only ever nested max 2 deep

    def to_json(self, filename: str):
        # TODO: remove 'id'
        with open(filename, 'w') as file:
            json.dump(self.data, file, cls=ComplexEncoder)

    def to_yaml(self, filename: str = BACKUP_DEFAULT_LOCATION):
        with open(filename, 'w') as file:
            yaml.dump(self.data, file, default_flow_style=False)
