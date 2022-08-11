from typing import Optional

import requests
from requests.exceptions import HTTPError
from urllib3.util import Retry

from constants import API_BASES, Service


class Api:
    def __init__(self, service: Service, address: str, port: int, api_key: Optional[str] = None):
        self.r = None
        self.port = port
        self.api_key = api_key
        self.path = API_BASES[service.value]
        self.address = address if address.startswith('http') else 'http://' + address

    @property
    def base_url(self) -> str:
        return f"{self.address}:{self.port}{self.path}"

    def initialize(self):
        adapter = requests.adapters.HTTPAdapter(max_retries=Retry(total=10, backoff_factor=0.1))
        self.r = requests.Session()
        self.r.mount('http://', adapter)
        self.r.mount('https://', adapter)

        if not self.api_key:
            print("No api key in config, fetching api key instead.")
            response = self.r.get(f"{self.address}:{self.port}/initialize.js")
            bits = response.text.split("'")
            self.api_key = bits[3]

        self.r.headers.update({'X-Api-Key': self.api_key})

        self.get("/health")  # Test connection
        print('Successfully connected to the server.')

    def get(self, resource, id=None) -> dict:
        req = f"{self.base_url}{resource}{'/' + str(id) if id else ''}"
        print(f"Fetching: {req}")
        response = self.r.get(req)
        response.raise_for_status()
        return response.json()

    def create(self, resource, body) -> None:
        req = f"{self.base_url}{resource}"
        try:
            response = self.r.post(req, json=body)
            response.raise_for_status()
        except HTTPError as e:
            if e.response.status_code == 400 and 'indexer' in resource:  # temp
                pass
            else:
                raise HTTPError(f"{e.response.status_code} Error for resource: {resource}. Response: {e.response.text}")

    def edit(self, resource, body, id) -> None:
        req = f"{self.base_url}{resource}{'/' + str(id) if id else ''}"
        settings = {}
        try:
            settings = self.get(resource, id)
        except HTTPError as e:
            if e.response.status_code == 404:
                del body['id']  # can't create with existing ID
                return self.create(resource, body)
        if settings != body:  # only if updated / not default
            settings.update(body)
            response = self.r.put(req, json=settings)
            response.raise_for_status()

    def delete(self, resource, id) -> None:
        req = f"{self.base_url}{resource}/{id}"
        print(f"Deleting: {req}")
        response = self.r.delete(req)
        response.raise_for_status()
