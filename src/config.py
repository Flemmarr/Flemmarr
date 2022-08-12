from api import Api
from pyaml_env import parse_config
from constants import Service, CONFIG_DEFAULT_LOCATION
import yaml
from routes import PATHS


class Config:
    def __init__(self, cfg: dict):
        self._cfg = cfg
        self._api = None

    @classmethod
    def from_yaml(cls, file: str = CONFIG_DEFAULT_LOCATION):
        cfg = parse_config(file, default_value='')
        return cls(cfg)

    def apply(self):
        for app in self._cfg:
            self._api = Api(Service(app), **self._cfg[app].pop('server'))
            self._api.initialize()
            self._triage_and_apply(self._cfg[app])

    @classmethod
    def from_current(cls, service, address, port):
        api = Api(Service(service), address=address, port=port)
        api.initialize()
        res = {}
        for path in PATHS[service]:
            value = api.get(path)
            for key in reversed(path[1:].split('/')):
                value = {key: value}
            res.update(value)

        res['server'] = {'address': api.address, 'port': api.port}
        return cls({api.service: res})

    def to_file(self, filename):
        with open(filename, 'w') as file:
            yaml.dump(self._cfg, file)

    def _triage_and_apply(self, object, resource: str = ''):
        if isinstance(object, dict):
            if any(isinstance(object[key], (dict, list)) for key in object):
                for key in object:
                    self._triage_and_apply(object[key], f"{resource}/{key}")
            else:
                print(f"calling edit: {resource=}")
                self._api.edit(resource, object, object['id'])  # even non-list item has id (like config/ui)
        elif isinstance(object, list):
            for body in object:
                if 'id' not in body:  # all list items should have id's
                    raise
                print(f"calling edit with id: {resource=}")
                self._api.edit(resource, body, body['id'])
