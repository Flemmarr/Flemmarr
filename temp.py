from src.config import Config


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


a = Config.from_current(services=addresses)






res = {}
for service in a.keys():
    l = {}
    for u in a[service]:
        u.current_config
    res[service] = l

for u in i['readarr']:
    u.apply()

