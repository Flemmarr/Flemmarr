import os
from contextlib import suppress
from typing import Union


def recursive_delete_dict_keys_from_obj(obj: Union[dict, list], keys: list) -> None:
    """Delete keys from a nested dict in-place."""
    if isinstance(obj, dict):
        for key in keys:
            with suppress(KeyError):
                del obj[key]
        for value in obj.values():
            if isinstance(value, dict):
                recursive_delete_dict_keys_from_obj(value, keys)
            if isinstance(value, list):
                [recursive_delete_dict_keys_from_obj(v, keys) for v in value]
    if isinstance(obj, list):
        [recursive_delete_dict_keys_from_obj(v, keys) for v in obj]


def env_vars_to_nested_dict(data: os.environ) -> dict:
    """Transform relevant environment variables to more convenient dict.
    e.g. {"SONARR_ADDRESS": "192.168.0.1", "SONARR_PORT": 8989}
     -> {"sonarr": {"address": "192.168.0.1", "port": 8989"}} """
    result = {}
    data = {k: v for k, v in data.items() if
            k.lower().startswith(("sonarr", "radarr", "lidarr", "prowlarr", "readarr"))}
    for key, value in data.items():
        app, setting = key.split("_")
        result.setdefault(app.lower(), {})[setting.lower()] = value
    return result
