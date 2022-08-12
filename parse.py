import json
# from openapi_core import create_spec
import re


# spec = create_spec(data)

def parse_swagger(file):
    with open(file) as f:
        data = json.load(f)

    paths = list({k: v for k, v in data['paths'].items() if 'get' in v}.keys())
    filtered = [p for p in paths if not any(x in p for x in ['{', 'login', 'logout', 'routes', 'schema', 'initialize.js', 'health', 'calendar'])]
    remove_prefix = [re.sub(r'/api/v[0-9]', '', p) for p in filtered]
    return remove_prefix

