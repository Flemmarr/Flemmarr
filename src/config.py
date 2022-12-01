import json
from collections import UserDict
from typing import Optional

import yaml
from pyaml_env import parse_config

from api import Api
from constants import Service, CONFIG_DEFAULT_LOCATION, API_PATHS_LOCATION
from models import AppSetting
from utils import ComplexEncoder


class Config(UserDict):
    def __init__(self, data: Optional[dict] = None):
        super().__init__(data)

    @classmethod
    def from_yaml(cls, services: dict, filename: str):
        base_cfg = parse_config(API_PATHS_LOCATION, default_value='')
        new_config = parse_config(filename)

        for service, location in services.items():
            api = Api(Service(service), address=location["address"], port=location["port"])
            base_cfg[service] = cls._deep_update(base_cfg[service], new_config[service], api=api)
        return cls(new_config)

    @staticmethod
    def _deep_update(mapping: dict, updating_mapping: dict, api: Api) -> dict:
        updated_mapping = mapping.copy()
        for k, v in updated_mapping.items():
            if k in updating_mapping and isinstance(v, dict):
                for k2 in updated_mapping[k]:
                    if k2 in updating_mapping[k]:
                        if isinstance(updating_mapping[k][k2], list):
                            updated_mapping[k][k2] = AppSetting(updating_mapping[k][k2], resource=f"/{k}/{k2}", api=api)
                        elif isinstance(updating_mapping[k][k2], dict):
                            updated_mapping[k][k2] = AppSetting(resource=f"/{k}/{k2}", api=api,
                                                                **updating_mapping[k][k2])
                    else:
                        updated_mapping[k][k2] = AppSetting(resource=f"/{k}/{k2}", api=api)
            elif k in updating_mapping:
                if isinstance(updating_mapping[k], list):
                    updated_mapping[k] = AppSetting(updating_mapping[k], resource=f"/{k}", api=api)
                elif isinstance(updating_mapping[k], dict):
                    updated_mapping[k] = AppSetting(resource=f"/{k}", api=api, **updating_mapping[k])
            else:
                updated_mapping[k] = AppSetting(resource=f"/{k}", api=api)
        return updated_mapping

    # def apply(self, services: dict):
    #     """Apply a Config to running services."""
    #     for app in services:
    #         api = Api(Service(app), **services[app]).initialize()
    #         self._triage_and_apply(self[app], api)

    def to_json(self, filename: str):
        with open(filename, 'w') as file:
            json.dump(self.data, file, cls=ComplexEncoder)

    def to_yaml(self, filename: str = CONFIG_DEFAULT_LOCATION):
        with open(filename, 'w') as file:
            yaml.dump(self.data, file, default_flow_style=False)
