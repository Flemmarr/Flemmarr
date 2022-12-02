from functools import cached_property
from itertools import zip_longest
from typing import Union

import yaml
from requests import HTTPError

from api import Api


class AppSetting(yaml.YAMLObject):
    yaml_tag = u''

    def __init__(self, *args, resource: str, api: Api, **kwargs):
        self.api = api
        self.resource = resource
        if args:
            self._new_config = args[0]  # single list
        elif kwargs:
            self._new_config = [kwargs]
        else:
            self._new_config = [None]

    def __repr__(self):
        return f"{self._current_config}"

    def __json__(self):
        """Facilitate json serialization using ComplexEncoder"""
        return self._current_config

    @classmethod
    def to_yaml(cls, dumper, data):
        """Facilitate yaml serialization"""
        if isinstance(data._current_config, dict):
            return dumper.represent_mapping("tag:yaml.org,2002:map", data._current_config)
        if isinstance(data._current_config, list):
            return dumper.represent_sequence("tag:yaml.org,2002:seq", data._current_config)

    @cached_property
    def _current_config(self) -> Union[dict, list]:
        self.api.initialize()
        return self.api.get(self.resource)

    def apply(self):
        """Loop over two ordered lists, one of the current resource settings (one or more items),
        and second list for the new resource settings (of one or more items). Depending on the existence
        of either, we either update, create, delete or do nothing."""
        print(f"Applying {self.api.service}: {self.resource}")
        current_cfg = self._current_config
        if not isinstance(self._current_config, list):
            current_cfg = [self._current_config]
        for current, new in zip_longest(current_cfg, self._new_config):
            if not current and not new:
                continue  # nothing to be updated
            elif current and new:
                body = current.copy()
                body.update(**new)
                self.api.update(self.resource, id=current['id'], body=body)
            elif not current:
                self.api.create(self.resource, body=new)
            elif not new:
                try:
                    self.api.delete(self.resource, id=current['id'])
                except HTTPError as e:
                    if e.response.status_code == 405:
                        # Some configs cannot be deleted, e.g. when a default must always exist.
                        print("Skipping unconfigured item that cannot be deleted.")

        self.__dict__.pop("_current_config", None)  # invalidate _current_config cache, since we changed it.
