import os

from config import Config
from constants import BACKUP_DEFAULT_LOCATION, CONFIG_DEFAULT_LOCATION
from utils import env_vars_to_nested_dict


def main():
    params = env_vars_to_nested_dict(os.environ)
    current_config = Config.from_existing(params)
    current_config.to_file(BACKUP_DEFAULT_LOCATION)
    print('Backed-up current configurations')
    if os.path.exists(CONFIG_DEFAULT_LOCATION):
        cfg = Config.from_yaml()
        cfg.apply(params)
        print('Finished applying configurations')


if __name__ == "__main__":
    main()
