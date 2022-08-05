import requests
from urllib3.util import Retry
from constants import API_BASES, Service


class Api:
    def __init__(self, service: Service, address: str, port: int, api_key: str):
        self.path = API_BASES[service.value]
        self.port = port
        self.address = address if address.startswith('http') else 'http://' + address

        adapter = requests.adapters.HTTPAdapter(max_retries=Retry(total=10, backoff_factor=0.1))

        self.r = requests.Session()
        self.r.headers.update({'X-Api-Key': api_key})
        self.r.mount('http://', adapter)
        self.r.mount('https://', adapter)

    @property
    def base_url(self) -> str:
        return f"{self.address}:{self.port}{self.path}"

    def get(self, resource, id=None) -> dict:
        req = f"{self.base_url}{resource}{'/' + id if id else ''}"
        print(f"Fetching: {req}")
        response = self.r.get(req)
        response.raise_for_status()
        return response.json()

    def create(self, resource, body) -> None:
        req = f"{self.base_url}{resource}"
        print(f"Creating: {req}")
        response = self.r.post(req, json=body)
        response.raise_for_status()

    def edit(self, resource, body, id=None) -> None:
        req = f"{self.base_url}{resource}{'/' + id if id else ''}"
        print(f"Editing: {req}")
        settings = self.get(resource, id)
        settings.update(body)
        response = self.r.put(req, json=settings)
        response.raise_for_status()

    def delete(self, resource, id) -> None:
        req = f"{self.base_url}{resource}/{id}"
        print(f"Deleting: {req}")
        response = self.r.delete(req)
        response.raise_for_status()
