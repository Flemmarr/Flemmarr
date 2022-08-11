import json
from src.api import Api
from src.constants import Service
import requests
from openapi_core import create_spec
from readarr_routes import PATHS
import yaml


with open('readarr-swagger.json') as f:
    data = json.load(f)

spec = create_spec(data)




paths = list({k: v for k, v in data['paths'].items() if 'get' in v}.keys())

api = Api(Service.READARR, "192.168.178.47", 8787)
api.initialize()

for path in list(paths):
    if not any(x in path for x in ['{', 'login', 'logout', 'editor', 'author', 'book', 'parse', 'routes']):
        try:
            print(path)
            api.get(path.replace('api/v1/', ''))
        except requests.exceptions.HTTPError:
            pass

import collections.abc

def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


paths = [p.replace('api/v1/', '') for p in PATHS]
res = {}
for path in paths:
    value = api.get(path)
    for key in reversed(path[1:].split('/')):
        value = {key: value}
    res.update(value)


with open(r'test-cfg.yml', 'w') as file:
    documents = yaml.dump(res, file)