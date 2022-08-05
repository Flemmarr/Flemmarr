import yaml
from api import Api


class Config:
    def __init__(self, cfg: dict):
        self.cfg = cfg

    @classmethod
    def from_yaml(cls, file: str = './config/config.yml'):
        with open(file, "r") as f:
            cfg = yaml.safe_load(f)
        return cls(cfg)

    def apply(self):
        for app in self.cfg:
            server = app.pop('server')
            self.api = Api(server['address'], server['port'])
            self.api.initialize()
            self._triage_and_apply(app)

    def _triage_and_apply(self, object, resource=''):
        if isinstance(object, dict):
            if any(isinstance(object[key], (dict, list)) for key in object):
                for key in object:
                    self._triage_and_apply(object[key], '{}/{}'.format(resource, key))
            else:
                self.api.edit(resource, object)
        else:
            for body in object:
                self.api.create(resource, body)
