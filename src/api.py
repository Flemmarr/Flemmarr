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

    def get(self, resource: str, id: Optional[int] = None) -> dict:
        """Perform a get request on resource with optional id."""
        req = f"{self.base_url}{resource}{'/' + str(id) if id else ''}"
        print(f"Fetching: {req}")
        response = self.session.get(req)
        response.raise_for_status()
        return response.json()

    def create(self, resource: str, body: dict) -> None:
        """Create a new resource."""
        response = self.session.post(f"{self.base_url}{resource}", json=body)
        response.raise_for_status()

    def update(self, resource: str, body: dict, id: int) -> None:
        """Update an existing resource with specified id.
        -> check if resource already exists
            -> if not: create
            -> if it does: check if settings need to be updated.
                -> if yes: update resource
                -> if not: skip """
        req = f"{self.base_url}{resource}{'/' + str(id) if id else ''}"
        try:
            current_settings = self.get(resource, id)
        except HTTPError as e:
            if e.response.status_code == 404:
                del body['id']  # can't pass an id when creating new resource
                return self.create(resource, body)
            raise
        if not body.items() <= current_settings.items():  # check if not subset
            current_settings.update(body)  # apply changes
            response = self.session.put(req, json=current_settings)
            response.raise_for_status()

    def delete(self, resource: str, id: int) -> None:
        """Delete existing resource with specified id."""
        req = f"{self.base_url}{resource}/{id}"
        print(f"Deleting: {req}")
        response = self.session.delete(req)
        response.raise_for_status()
