from enum import Enum

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
