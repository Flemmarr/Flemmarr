from enum import Enum

CONFIG_DEFAULT_LOCATION = './config/config.yml'
BACKUP_DEFAULT_FOLDER = 'config'
API_PATHS_LOCATION = "template.yml"

API_BASES = {
    "readarr": "/api/v1",
    "radarr": "/api/v3",
    "sonarr": "/api/v3",
    "prowlarr": "/api/v1",
    "lidarr": "/api/v1"
}


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
    "order",
    "description",
    "capabilities",
    "added",
    'apiKey',
    'freeSpace',
]
