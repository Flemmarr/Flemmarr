import yaml
from pyaml_env import parse_config

from api import Api
from constants import Service, CONFIG_DEFAULT_LOCATION
from routes import PATHS


class Config:
    def __init__(self, cfg: dict):
        self._cfg = cfg
        self._api = None

    @classmethod
    def from_yaml(cls, file: str = CONFIG_DEFAULT_LOCATION):
        # TODO: add keys for unconfigured list items, such that they can get deleted
        cfg = parse_config(file, default_value='')
        return cls(cfg)

    @classmethod
    def from_current(cls, service: str, address: str, port: int):
        api = Api(Service(service), address=address, port=port).initialize()
        res = {}
        for path in PATHS[service]:
            value = api.get(path)
            for key in reversed(path[1:].split('/')):
                value = {key: value}
            res.update(value)

        res['server'] = {'address': api.address, 'port': api.port}
        return cls({api.service: res})

    def apply(self):
        for app in self._cfg:
            self._api = Api(Service(app), **self._cfg[app].pop('server')).initialize()
            self._triage_and_apply(self._cfg[app])

    def to_file(self, filename):
        with open(filename, 'w') as file:
            yaml.dump(self._cfg, file)

    def _triage_and_apply(self, obj, resource: str = ''):
        if isinstance(obj, dict):
            if any(isinstance(obj[key], (dict, list)) for key in obj):
                for key in obj:
                    self._triage_and_apply(obj[key], f"{resource}/{key}")
            else:
                self._api.edit(resource, obj, obj['id'])  # even non-list item has id (like config/ui)
        elif isinstance(obj, list):
            for item in obj:
                if 'id' not in item:  # all list items should have id's
                    raise
                self._api.edit(resource, item, item['id'])
            self._delete_excess_items(resource, obj)

    def _delete_excess_items(self, resource, obj):
        max_config_id = max((item['id'] for item in obj), default=0)
        max_actual_id = max((item['id'] for item in self._api.get(resource)), default=-1)
        if max_actual_id > max_config_id:
            for id in range(max_config_id+1, max_actual_id+1):  # excluding start and including end
                self._api.delete(resource, id)
