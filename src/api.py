import requests
from urllib3.util import Retry


class Api:
    def __init__(self, address: str, port: int):
        self.path = ''
        self.port = port
        self.address = address if address.startswith('http') else 'http://' + address

        adapter = requests.adapters.HTTPAdapter(max_retries=Retry(total=10, backoff_factor=0.1))

        self.r = requests.Session()
        self.r.mount('http://', adapter)
        self.r.mount('https://', adapter)

    @property
    def base_url(self) -> str:
        return f"{self.address}:{self.port}{self.path}"

    def initialize(self):
        response = self.r.get(f"{self.address}:{self.port}/initialize.js")

        bits = response.text.split("'")
        api_root = bits[1]
        api_key = bits[3]

        self.path = api_root
        self.r.headers.update({'X-Api-Key': api_key})

        print('Successfully connected to the server and fetched the API key and path')

    def get(self, resource, id = None) -> dict:
        print(f"Fetching: {self.base_url}/{resource}{'/' + id if id else ''}")
        response = self.r.get(f"{self.base_url}/{resource}{'/' + id if id else ''}")
        response.raise_for_status()
        return response.json()

    def create(self, resource, body):
        print(f"Creating: {self.base_url}/{resource}")
        response = self.r.post(f"{self.base_url}/{resource}", json=body)
        response.raise_for_status()

    def edit(self, resource, body, id = None):
        print("Editing: {self.base_url}/{resource}/{id}")
        old_version = self.get(resource, id)
        old_version.update(body)

        response = self.r.put(f"{self.base_url}/{resource}/{id}", json=old_version)
        response.raise_for_status()

    def delete(self, resource, id):
        print(f"Deleting: {self.base_url}{resource}/{id}")
        response = self.r.delete(f"{self.base_url}{resource}/{id}")
        response.raise_for_status()
