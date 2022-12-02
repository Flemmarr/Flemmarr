from contextlib import suppress
import json


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        else:
            return json.JSONEncoder.default(self, obj)


def delete_dict_keys(obj: dict, keys: list) -> dict:
    """Delete keys from a nested dict in-place."""
    for key in keys:
        with suppress(KeyError):
            del obj[key]
    return obj


def nest_dict(flat_dict: dict, sep='_', sep_idx=0) -> dict:
    """Transform a dict to a nested dict, by splitting keys on a seperator.
    e.g. {"SONARR_ADDRESS": "192.168.0.1", "SONARR_PORT": 8989}
     -> {"sonarr": {"address": "192.168.0.1", "port": 8989"}} """
    result = {}
    for key, value in flat_dict.items():
        try:
            app, setting = key.split(sep)[sep_idx:]
            print(app, setting)
            try:
                result.setdefault(app.lower(), {})[setting.lower()] = value
            except TypeError:  # key already exists with empty string value
                result[app.lower()] = {setting.lower(): value}
        except ValueError:
            result[key[sep_idx:]] = value
    return result
