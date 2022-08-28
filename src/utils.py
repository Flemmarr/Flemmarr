from contextlib import suppress
from typing import Union


def delete_dict_keys_from_obj(obj: Union[dict, list], keys: list) -> None:
    if isinstance(obj, dict):
        for key in keys:
            with suppress(KeyError):
                del obj[key]
        for value in obj.values():
            if isinstance(value, dict):
                delete_dict_keys_from_obj(value, keys)
            if isinstance(value, list):
                [delete_dict_keys_from_obj(v, keys) for v in value]
    if isinstance(obj, list):
        [delete_dict_keys_from_obj(v, keys) for v in obj]
