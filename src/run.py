import yaml
import os
from api import Api

config_path = "./config/config.yml"

if "FLEMMARR__CONFIG_PATH" in os.environ:
    config_path = os.environ["FLEMMARR__CONFIG_PATH"]

configs = yaml.safe_load(open(config_path, "r"))

for key in configs:
    config = configs[key]
    server = config["server"]
    config.pop("server")

    baseUrl = ""
    if server["baseUrl"]:
        baseUrl = server["baseUrl"]

    if baseUrl[0] != "/":
        baseUrl = "/" + baseUrl

    api = Api(server["address"], server["port"], baseUrl)

    print("Trying to connect to {}".format(key))
    api.initialize()

    print("Starting to apply configuration")
    api.apply(config)

print("Finished to apply configurations")
