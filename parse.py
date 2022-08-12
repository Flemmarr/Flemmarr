import json
from src.api import Api
from src.constants import Service
import requests
# from openapi_core import create_spec
from readarr_routes import PATHS
import yaml
import re


# spec = create_spec(data)

def parse_swagger(file):
    with open(file) as f:
        data = json.load(f)

    paths = list({k: v for k, v in data['paths'].items() if 'get' in v}.keys())
    filtered = [p for p in paths if not any(x in p for x in ['{', 'login', 'logout', 'routes', 'schema', 'initialize.js', 'health', 'calendar'])]
    remove_prefix = [re.sub(r'/api/v[0-9]', '', p) for p in filtered]
    return remove_prefix


api = Api(Service.READARR, "192.168.178.47", 8787)
api.initialize()


def get_current_config(api, paths, output_file='test-cfg2.yml'):
    res = {}
    for path in paths:
        value = api.get(path)
        for key in reversed(path[1:].split('/')):
            value = {key: value}
        res.update(value)

    res['server'] = {'address': api.address, 'port': api.port}
    final = {api.service: res}
    print(f"Writing output to: {output_file}")
    with open(output_file, 'w') as file:
        yaml.dump(final, file)
