import json


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


def nest_dict(flat_dict: dict, sep='_', sep_idx=0) -> dict:
    """Transform a dict to a nested dict, by splitting keys on a seperator.
    e.g. {"SONARR_ADDRESS": "192.168.0.1", "SONARR_PORT": 8989}
     -> {"sonarr": {"address": "192.168.0.1", "port": 8989"}} """
    result = {}
    for key, value in flat_dict.items():
        app, setting = key.split(sep)[sep_idx:]
        result[app.lower()] = result.get(app.lower(), {})
        result[app.lower()][setting.lower()] = value
    return result
