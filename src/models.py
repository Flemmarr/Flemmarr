from functools import cached_property
from itertools import zip_longest
from typing import Union

import yaml
from requests import HTTPError

from api import Api


class AppSetting(yaml.YAMLObject):
    yaml_tag = u''

    def __init__(self, *args, resource, api: Api, **kwargs):
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
        for current, new in zip_longest(self._current_config, self._new_config):
            if current and new:
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
                        print("Skipping unconfigured item that cannot be deleted.")
