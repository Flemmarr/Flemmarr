import json
import re
from src.utils import nest_dict

SWAGGER_FILES = ['docs/lidarr-v1.json', 'docs/prowlarr-v1.json', 'docs/radarr-v3.json', 'docs/readarr-v1.json',
                 'docs/sonarr-v3.json']

EXCLUDED_PATHS = ['{', 'log', 'routes', 'schema', 'initialize.js', 'health', 'calendar', 'search', 'update', 'rename',
                  'wanted', 'history', 'queue', 'command', 'diskspace', 'parse', 'backup', 'blocklist']


def parse_swagger(file):
    with open(file) as f:
        data = json.load(f)

    paths = list({k: v for k, v in data['paths'].items() if 'get' in v}.keys())
    # Exclude some recurring irrelevant paths
    filtered = [p for p in paths if not any(x in p for x in EXCLUDED_PATHS)]
    removed_prefix = [re.sub(r'/api/v[0-9]', '', p) for p in filtered]
    return nest_dict({k: '' for k in removed_prefix}, sep='/', sep_idx=1)

d = {}  # Produce initial list, to be manually filtered later
for f in SWAGGER_FILES:
    d[f[f.find('/') + 1:f.find('-')]] = parse_swagger(f)
