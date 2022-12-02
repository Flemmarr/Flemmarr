import os
from config import Config
from utils import nest_dict


def main():
    params = nest_dict(
        {k: v for k, v in os.environ.items() if k.lower().startswith(
            ("sonarr", "radarr", "lidarr", "prowlarr", "readarr"))
         }
    )

    cfg = Config.from_yaml(services=params, filename='config1.yml')
    cfg.to_yaml('testing.yaml')
    print('Successfully backed-up current configurations.')

    cfg.apply()
    print('Successfully finished applying configurations.')


if __name__ == "__main__":
    main()
