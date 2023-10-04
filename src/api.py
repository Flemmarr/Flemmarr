import requests
from urllib3.util import Retry
import json


class Api(object):
    def __init__(self, address, port, baseUrl):
        self.address = address
        self.port = port
        self.path = baseUrl

        adapter = requests.adapters.HTTPAdapter(
            max_retries=Retry(total=5, backoff_factor=0.1)
        )

        self.r = requests.Session()
        self.r.mount("http://", adapter)
        self.r.mount("https://", adapter)

    def __url(self, resource="", id=None):
        address = (
            self.address
            if self.address.startswith("http")
            else "http://" + self.address
        )
        id_path = "/{}".format(id) if id else ""
        return "{}:{}{}{}{}".format(address, self.port, self.path, resource, id_path)

    def __get(self, resource, id=None):
        response = self.r.get(self.__url(resource, id))
        status_code = response.status_code

        if id:
            id_string = " {}".format(id)
        else:
            id_string = ""

        print("Fetching {}{}: {}".format(resource, id_string, status_code))

        if status_code < 300:
            return response.json()

    def __create(self, resource, body):
        response = self.r.post(self.__url(resource), json=body)
        status_code = response.status_code

        if status_code < 300:
            print(
                "Creating {} {}: {}".format(
                    resource, response.json()["id"], status_code
                )
            )
            return response.json()
        else:
            print("Creating {}: {}".format(resource, status_code))

    def __edit(self, resource, body, id=None):
        old_version = self.__get(resource, id)

        for key in body:
            old_version[key] = body[key]

        status_code = self.r.put(self.__url(resource, id), json=old_version).status_code

        if id:
            id_string = " {}".format(id)
        else:
            id_string = ""

        print("Editing {}{}: {}".format(resource, id_string, status_code))

    def __delete(self, resource, id):
        status_code = self.r.delete(self.__url(resource, id)).status_code

        print("Deleting {} {}: {}".format(resource, id, status_code))

    def __triage_and_apply(self, object, resource=""):
        if isinstance(object, dict):
            if any(isinstance(object[key], (dict, list)) for key in object):
                for key in object:
                    self.__triage_and_apply(object[key], "{}/{}".format(resource, key))
            else:
                self.__edit(resource, object)
        else:
            for body in object:
                self.__create(resource, body)

    def initialize(self):
        print("Trying to connect to the server with the v3 method")
        response = self.r.get("{}/initialize.js".format(self.__url()), timeout=5)

        print(json.dumps(response.json(), indent=2))

        if response.status_code == 200:
            print("Successfully connected to the server with the v3 method")
            bits = response.text.split("'")
            api_root = bits[1]
            api_key = bits[3]
        elif response.status_code == 404:
            print(
                "Couldn't conect to the server with the v3 method, trying to connect with the v4 method"
            )

            response = self.r.get("{}/initialize.json".format(self.__url()))

            bits = json.loads(response.text)
            api_root = bits["apiRoot"]
            api_key = bits["apiKey"]

        self.path = api_root
        self.r.headers.update({"X-Api-Key": api_key})

        print("Successfully connected to the server and fetched the API key and path")

    def apply(self, config):
        self.__triage_and_apply(config)
