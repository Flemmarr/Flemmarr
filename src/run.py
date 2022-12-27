import os
import sys
import logging
from config import Config
from constants import CONFIG_DEFAULT_LOCATION, BACKUP_DEFAULT_FOLDER
from utils import nest_dict


logger = logging.getLogger("Flemmarr")
logger.setLevel(os.environ.get("LOG_LEVEL", logging.DEBUG))
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
logger.addHandler(stdout_handler)


def main():
    params = nest_dict(
        {k: v for k, v in os.environ.items() if k.lower().startswith(
            ("sonarr", "radarr", "lidarr", "prowlarr", "readarr"))
         }
    )

    if cfg_file := os.environ.get("CONFIG_FILE"):
        cfg = Config.from_yaml(services=params, filename=cfg_file)
    elif os.path.exists(CONFIG_DEFAULT_LOCATION):
        cfg = Config.from_yaml(services=params)
    else:
        cfg = Config(services=params)
    cfg.to_yaml(os.environ.get("BACKUP_FOLDER", BACKUP_DEFAULT_FOLDER))

    cfg.apply()


if __name__ == "__main__":
    main()
