import json
import re

SWAGGER_FILES = ['lidarr-v1.json', 'prowlarr-v1.json', 'radarr-v3.json', 'readarr-v1.json',
                 'sonarr-v3.json']

EXCLUDED_PATHS = ['{', 'log', 'routes', 'schema', 'initialize.js', 'health', 'calendar', 'search', 'update', 'rename',
                  'wanted', 'history', 'queue', 'command', 'diskspace', 'parse', 'backup', 'blocklist']


def parse_swagger(file):
    with open(file) as f:
        data = json.load(f)

    paths = list({k: v for k, v in data['paths'].items() if 'get' in v}.keys())
    # Exclude some recurring irrelevant paths
    filtered = [p for p in paths if not any(x in p for x in EXCLUDED_PATHS)]
    removed_prefix = [re.sub(r'/api/v[0-9]', '', p) for p in filtered]
    return removed_prefix


d = {}  # Produce initial list, to be manually filtered later
for f in SWAGGER_FILES:
    d[f[f.find('/') + 1:f.find('-')]] = parse_swagger(f)
