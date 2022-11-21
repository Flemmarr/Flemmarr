from pyaml_env import parse_config
from models import AppSetting
from api import Api
from constants import Service


def deep_update(mapping: dict, updating_mapping: dict, api: Api) -> dict:
    updated_mapping = mapping.copy()
    for k, v in updating_mapping.items():
        if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v, dict):
            for k2, v2 in updating_mapping[k].items():
                if k2 in updated_mapping[k]:
                    if isinstance(v2, list):
                        updated_mapping[k][k2] = AppSetting(v2, resource=f"/{k}/{k2}", api=api)
                    elif isinstance(v2, dict):
                        updated_mapping[k][k2] = AppSetting(resource=f"/{k}/{k2}", api=api, **v2)
                else:
                    raise NotImplementedError(f"Setting: {k}/{k2} is not supported.")
        elif k in updated_mapping:
            if isinstance(v, list):
                updated_mapping[k] = AppSetting(v, resource=f"/{k}", api=api)
            elif isinstance(v, dict):
                updated_mapping[k] = AppSetting(resource=f"/{k}", api=api, **v)
        else:
            raise NotImplementedError(f"Setting: {k} is not supported.")
    return updated_mapping


def deep_update2(mapping: dict, updating_mapping: dict, api: Api) -> dict:
    updated_mapping = mapping.copy()
    for k, v in updated_mapping.items():
        if k in updating_mapping and isinstance(v, dict):
            for k2 in updated_mapping[k]:
                if k2 in updating_mapping[k]:
                    if isinstance(updating_mapping[k][k2], list):
                        updated_mapping[k][k2] = AppSetting(updating_mapping[k][k2], resource=f"/{k}/{k2}", api=api)
                    elif isinstance(updating_mapping[k][k2], dict):
                        updated_mapping[k][k2] = AppSetting(resource=f"/{k}/{k2}", api=api, **updating_mapping[k][k2])
                else:
                    updated_mapping[k][k2] = AppSetting(resource=f"/{k}/{k2}", api=api)
        elif k in updating_mapping:
            if isinstance(updating_mapping[k], list):
                updated_mapping[k] = AppSetting(updating_mapping[k], resource=f"/{k}", api=api)
            elif isinstance(updating_mapping[k], dict):
                updated_mapping[k] = AppSetting(resource=f"/{k}", api=api, **updating_mapping[k])
        else:
            updated_mapping[k] = AppSetting(resource=f"/{k}", api=api)
    return updated_mapping


def main():
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

    cfg = parse_config("test.yml", default_value='')

    new = parse_config("config1.yml")

    for service in cfg:

        api = Api(Service(service), address=addresses[service]["address"], port=addresses[service]["port"])
        cfg[service] = deep_update2(cfg[service], new[service], api=api)

    # tst = deep_update(cfg, new)
    # for key in cfg:
    #     if isinstance(cfg[key], dict):
    #         for key2 in cfg[key]:
    #
    #     else:
    #         pass
    print("a;a;")






if __name__ == "__main__":
    main()