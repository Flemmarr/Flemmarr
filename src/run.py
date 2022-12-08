import os
from config import Config
from constants import CONFIG_DEFAULT_LOCATION
from utils import nest_dict


def main():
    params = nest_dict(
        {k: v for k, v in os.environ.items() if k.lower().startswith(
            ("sonarr", "radarr", "lidarr", "prowlarr", "readarr"))
         }
    )

    if cfg_file := os.environ.get("CONFIG_FILE"):
        cfg = Config.from_yaml(services=params, filename=f"./config/{cfg_file}")
    elif os.path.exists(CONFIG_DEFAULT_LOCATION):
        cfg = Config.from_yaml(services=params)
    else:
        cfg = Config(services=params)
    cfg.to_yaml()

    cfg.apply()


if __name__ == "__main__":
    main()
