from api import Api
from pyaml_env import parse_config
from constants import Service, CONFIG_DEFAULT_LOCATION


class Config:
    def __init__(self, cfg: dict):
        self._cfg = cfg
        self._api = None

    @classmethod
    def from_yaml(cls, file: str = CONFIG_DEFAULT_LOCATION):
        cfg = parse_config(file)
        return cls(cfg)

    def apply(self):
        for app in self._cfg:
            self._api = Api(Service(app), **self._cfg[app].pop('server'))
            self._api.initialize()
            self._triage_and_apply(self._cfg[app])

    def _triage_and_apply(self, object, resource: str = ''):
        if isinstance(object, dict):
            if any(isinstance(object[key], (dict, list)) for key in object):
                for key in object:
                    self._triage_and_apply(object[key], f"{resource}/{key}")
            else:
                self._api.edit(resource, object)
        elif isinstance(object, list):
            for body in object:
                self._api.create(resource, body)  # TODO: Idempotency?
