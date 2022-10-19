import json
from enum import Enum

CONFIG_DEFAULT_LOCATION = './config/config.yml'
BACKUP_DEFAULT_LOCATION = './config/config_backup.yml'
API_PATHS_LOCATION = 'routes.json'

API_BASES = {
    "readarr": "/api/v1",
    "radarr": "/api/v3",
    "sonarr": "/api/v3",
    "prowlarr": "/api/v1",
    "lidarr": "/api/v1"
}

with open(API_PATHS_LOCATION) as f:
    PATHS = json.load(f)


class Service(Enum):
    READARR = "readarr"
    RADARR = "radarr"
    SONARR = "sonarr"
    PROWLARR = "prowlarr"
    LIDARR = "lidarr"


UNWANTED_CFG_FIELDS = [
    "label",
    "helpText",
    "advanced",
    "type",
    "placeholder",
    "infoLink",
    "hint",
    "selectOptions",
    "order"
]
