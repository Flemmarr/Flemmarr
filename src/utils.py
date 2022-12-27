import json
from typing import Union
from datetime import datetime

from deepdiff import DeepDiff, Delta


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)


def remove_keys(obj, keys):
    if isinstance(obj, list) and all(isinstance(i, dict) for i in obj):
        return [remove_keys(item, keys) for item in sorted(obj, key=lambda x: x.get('id', float('inf')))]
    elif isinstance(obj, dict):
        return {k: remove_keys(v, keys) for k, v in obj.items() if k not in keys}
    else:
        return obj


def is_subset(d1: Union[dict, list], d2: Union[dict, list]) -> bool:
    """Check if a nested object is a subset of another nested object.
    In this case we don't care about new dict keys being added, but rather values being changed or
    iterable items being added."""
    delta = Delta(DeepDiff(d1, d2))
    delta.diff.pop("dictionary_item_added")
    return not delta.diff


def add_missing_keys(d1: Union[dict, list], d2: Union[dict, list]) -> Union[dict, list]:
    """Update a nested object using a second nested object, add any (nested) dict keys that are missing.
    Because we don't want to clutter the config file will all keys from the API, we remove some, but have
    to add them back when caling the API again."""
    delta = Delta(DeepDiff(d1, d2))
    [delta.diff.pop(key, None) for key in ['type_changes', 'iterable_item_added', 'values_changed']]
    return d1 + delta


def nest_dict(flat_dict: dict, sep='_', sep_idx=0) -> dict:
    """Transform a dict to a nested dict, by splitting keys on a seperator.
    e.g. {"SONARR_ADDRESS": "192.168.0.1", "SONARR_PORT": 8989}
     -> {"sonarr": {"address": "192.168.0.1", "port": 8989"}} """
    result = {}
    for key, value in flat_dict.items():
        app, setting = key.split(sep, 1)[sep_idx:]  # split on 1st occurrence
        result[app.lower()] = result.get(app.lower(), {})
        result[app.lower()][setting.lower()] = value
    return result


def get_datetime_string():
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")
