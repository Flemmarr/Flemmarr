from functools import cached_property
from itertools import zip_longest
from typing import Union

import yaml
import logging

from api import Api
from utils import remove_keys, is_subset, add_missing_keys


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
        self._logger = logging.getLogger(f"Flemmarr.{self.__class__.__name__}")

    def __repr__(self):
        return f"{self._current_config}"

    def __json__(self):
        """Facilitate json serialization using ComplexEncoder, and don't save 'id' field."""
        return remove_keys(self._current_config, ['id'])

    @classmethod
    def to_yaml(cls, dumper, data):
        """Facilitate yaml serialization, and don't save 'id' field."""
        # TODO: theres still ids in nested settings
        if isinstance(data._current_config, dict):
            return dumper.represent_mapping("tag:yaml.org,2002:map",
                                            remove_keys(data._current_config, ['id']))
        if isinstance(data._current_config, list):
            return dumper.represent_sequence("tag:yaml.org,2002:seq",
                                             remove_keys(data._current_config, ['id']))

    @cached_property
    def _current_config(self) -> Union[dict, list]:
        self.api.initialize()
        return self.api.get(self.resource)

    def apply(self):
        """Loop over two ordered lists, one of the current resource settings (one or more items),
        and second list for the new resource settings (of one or more items). Depending on the existence
        of either, we either update, create, delete or do nothing."""
        current_cfg = self._current_config
        if not isinstance(self._current_config, list):
            current_cfg = [self._current_config]
        for current, new in zip_longest(current_cfg, self._new_config):
            if not current and not new:
                continue  # nothing to be updated
            elif current and new:
                body = current.copy()
                if not is_subset(new, body):  # check for changes
                    update_body = add_missing_keys(new, body)
                    self.api.update(self.resource, id=update_body['id'], body=update_body)
            elif not current:
                self.api.create(self.resource, body=new)
            elif not new:
                # TODO: Should the config be assumed to reflect the entire state of the system?
                #  if so, we should delete resources that are not configured in the config.
                self.api.delete(self.resource, id=current['id'])

        self.__dict__.pop("_current_config", None)  # invalidate _current_config cache, since we changed it.
