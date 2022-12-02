from __future__ import annotations
from typing import Optional, Union
from json import JSONDecodeError
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from urllib3.util import Retry
from utils import delete_dict_keys
from constants import API_BASES, Service, UNWANTED_CFG_FIELDS


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
        if self.session:  # check if already initialized
            return self

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

        self.session.get(f"{self.base_url}/health")  # Test connection
        print('Successfully connected to the server.')
        return self

    @staticmethod
    def _raise_for_status_and_log(response):
        try:
            response.raise_for_status()
        except HTTPError:
            print(f"ERROR on: {response.url}")
            try:
                print(response.json())
            except JSONDecodeError:
                pass
            raise

    def get(self, resource: str) -> Union[dict, list]:
        """Perform a get request on resource."""
        req = f"{self.base_url}{resource}"
        print(f"Fetching: {req}")
        response = self.session.get(req)
        self._raise_for_status_and_log(response)
        # Filter unwanted response fields and guarantee result sorting
        if isinstance(response.json(), list):
            sorted_response = sorted(response.json(), key=lambda x: x['id'])
            return [delete_dict_keys(v, UNWANTED_CFG_FIELDS) for v in sorted_response]
        if isinstance(response.json(), dict):
            return delete_dict_keys(response.json(), UNWANTED_CFG_FIELDS)

    def create(self, resource: str, body: dict) -> None:
        """Create a new resource."""
        response = self.session.post(f"{self.base_url}{resource}", json=body, timeout=40)
        self._raise_for_status_and_log(response)
        print(f"Created (one of): {self.base_url}{resource}")

    def update(self, resource: str, id: int, body: dict) -> None:
        """Update an existing resource."""
        response = self.session.put(f"{self.base_url}{resource}/{id}", json=body)
        self._raise_for_status_and_log(response)
        print(f"Updated: {self.base_url}{resource}/{id}")

    def delete(self, resource: str, id: int) -> None:
        """Delete existing resource with specified id."""
        req = f"{self.base_url}{resource}/{id}"
        print(f"Deleting: {req}")
        response = self.session.delete(req)
        self._raise_for_status_and_log(response)
