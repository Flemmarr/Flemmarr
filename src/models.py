from functools import cached_property

from requests import HTTPError
from itertools import zip_longest

from api import Api


class AppSetting:
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

    @cached_property
    def _current_config(self):
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


# a = AppSetting([{"uiLanguage": 4}], resource='/config/ui', api=Api(service=Service.READARR, address='localhost', port=8787))