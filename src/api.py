from __future__ import annotations
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from urllib3.util import Retry

from constants import API_BASES, Service


class Api:
    def __init__(self, service: Service, address: str, port: int, api_key: Optional[str] = None):
        """Wrapper for an *arr api."""
        self.session = None
        self.service = service.value
        self.address = address if address.startswith('http') else 'http://' + address
        self.port = port
        self.api_key = api_key

    @property
    def base_url(self) -> str:
        """Convenience property to get the full application endpoint including api version."""
        return f"{self.address}:{self.port}{API_BASES[self.service]}"

    def initialize(self) -> Api:
        """Make actual API connection."""
        print(f"Initializing connection to {self.service}")
        adapter = HTTPAdapter(max_retries=Retry(total=10, backoff_factor=0.1))
        self.session = requests.Session()
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        if not self.api_key:
            print("No api key in config, fetching api key instead.")
            response = self.session.get(f"{self.address}:{self.port}/initialize.js")
            bits = response.text.split("'")
            self.api_key = bits[3]

        self.session.headers.update({'X-Api-Key': self.api_key})

        self.get("/health")  # Test connection
        print('Successfully connected to the server.')
        return self

    @staticmethod
    def raise_for_status_and_log(response):
        try:
            response.raise_for_status()
        except HTTPError:
            print(f"ERROR on: {response.url}")
            print(response.json())
            raise

    def get(self, resource: str) -> dict:
        """Perform a get request on resource with optional id."""
        req = f"{self.base_url}{resource}"
        print(f"Fetching: {req}")
        response = self.session.get(req)
        self.raise_for_status_and_log(response)
        return response.json()

    def create(self, resource: str, body: list) -> None:
        """Create a list of resources (while clearing the old)."""
        old_cfg = self.get(resource)
        for old_item in old_cfg:
            try:
                self.delete(resource, old_item["id"])
            except HTTPError as e:
                if e.response.status_code == 405:
                    print("Skipping global config that cannot be deleted.")
        for new_item in body:
            # Some requests can take along time (like setting an indexer in prowlarr).
            print(resource)
            if resource == "delayprofile" and new_item['Tags'] == []:
                self.update(resource, new_item)
            else:
                response = self.session.post(f"{self.base_url}{resource}", json=new_item, timeout=40)
                print(f"Configured (one of): {self.base_url}{resource}")
                self.raise_for_status_and_log(response)

    def update(self, resource: str, body: dict) -> None:
        """Update an existing resource."""
        cfg = self.get(resource)
        cfg.update(**body)
        response = self.session.put(f"{self.base_url}{resource}/{cfg['id']}", json=cfg)
        print(f"Configured: {self.base_url}{resource}/{cfg['id']}")
        self.raise_for_status_and_log(response)

    def delete(self, resource: str, id: int) -> None:
        """Delete existing resource with specified id."""
        req = f"{self.base_url}{resource}/{id}"
        print(f"Deleting: {req}")
        response = self.session.delete(req)
        self.raise_for_status_and_log(response)
