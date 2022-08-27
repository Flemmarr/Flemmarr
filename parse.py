import json
import re

SWAGGER_FILES = ['docs/lidarr-v1.json', 'docs/prowlarr-v1.json', 'docs/radarr-v3.json', 'docs/readarr-v1.json',
                 'docs/sonarr-v3.json']


def parse_swagger(file):
    with open(file) as f:
        data = json.load(f)

    paths = list({k: v for k, v in data['paths'].items() if 'get' in v}.keys())
    # Some recurring irrelevant exclusions
    filtered = [p for p in paths if not any(
        x in p for x in
        ['{', 'log', 'routes', 'schema', 'initialize.js', 'health', 'calendar', 'search', 'update', 'rename', 'wanted',
         'history', 'queue', 'command', 'diskspace', 'parse', 'backup', 'blocklist'])]
    removed_prefix = [re.sub(r'/api/v[0-9]', '', p) for p in filtered]
    return removed_prefix


d = {}
for file in SWAGGER_FILES:
    d[file[file.find('/') + 1:file.find('-')]] = parse_swagger(file)
