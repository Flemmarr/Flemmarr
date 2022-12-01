import os
from pyaml_env import parse_config
from config import Config
from constants import BACKUP_DEFAULT_LOCATION, CONFIG_DEFAULT_LOCATION, Service, PATHS
from utils import nest_dict, get_nested_value


def main():
    params = nest_dict(
        {k: v for k, v in os.environ.items() if k.lower().startswith(
            ("sonarr", "radarr", "lidarr", "prowlarr", "readarr"))
         }
    )
    # res = {}
    # for service in params.keys():
    #     l = []
    #     for u in params[service]:
    #         l.append(u.current_config)
    #     res[service] = l
    # if not params:  # local
    addresses = {
        "readarr": {
            "address": "localhost",
            "port": 8787
        },
        "radarr": {
            "address": "localhost",
            "port": 7878
        },
        "sonarr": {
            "address": "localhost",
            "port": 8989
        },
        "lidarr": {
            "address": "localhost",
            "port": 8686
        },
        "prowlarr": {
            "address": "localhost",
            "port": 9696
        }
    }

    # a = Config.from_current(services=addresses)
    b = Config.from_yaml(services=addresses, filename='config1.yml')


    # current_config = Config.from_existing(params)
    current_config.to_file(BACKUP_DEFAULT_LOCATION)
    print('Successfully backed-up current configurations.')
    if os.path.exists(CONFIG_DEFAULT_LOCATION):
        cfg = Config.from_yaml()
        cfg.apply(params)
        print('Successfully finished applying configurations.')


if __name__ == "__main__":
    import json

    # with open('__routes.json') as f:
    #     paths = json.load(f)


    print('laal')
    # main()
