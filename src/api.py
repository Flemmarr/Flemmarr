from __future__ import annotations

import logging
from json import JSONDecodeError
from typing import Optional, Union

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from requests.models import Response
from urllib3.util import Retry

from constants import API_BASES, Service, UNWANTED_CFG_FIELDS
from utils import remove_keys


class Api:
    def __init__(self, service: Service, address: str, port: int, api_key: Optional[str] = None, **kwargs):
        """Wrapper for an *arr api."""
        self.session = None
        self.service = service.value
        self.address = address if address.startswith('http') else 'http://' + address
        self.port = port
        self.api_key = api_key
        self._logger = logging.getLogger(f"Flemmarr.{self.__class__.__name__}")

    @property
    def base_url(self) -> str:
        """Convenience property to get the full application endpoint including api version."""
        return f"{self.address}:{self.port}{API_BASES[self.service]}"

    def initialize(self) -> Api:
        """Make actual API connection."""
        if self.session:  # check if already initialized
            return self

        self._logger.info(f"Initializing connection to {self.service}")
        adapter = HTTPAdapter(max_retries=Retry(total=10, backoff_factor=0.1))
        self.session = requests.Session()
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        if not self.api_key:
            self._logger.info("No api key in config, fetching api key instead.")
            response = self.session.get(f"{self.address}:{self.port}/initialize.js")
            bits = response.text.split("'")
            self.api_key = bits[3]

        self.session.headers.update({'X-Api-Key': self.api_key})

        self._raise_for_status_and_log(self.session.get(f"{self.base_url}/health"))  # Test connection
        self._logger.info('Successfully connected to the server.')
        return self

    def _raise_for_status_and_log(self, response: Response):
        try:
            response.raise_for_status()
        except HTTPError:
            self._logger.error(f"ERROR code {response.status_code} on: {response.request.method} {response.url}")
            self._try_log_request_and_response(response)
            raise

    def _try_log_request_and_response(self, response: Response):
        try:
            self._logger.debug(f"Request: {response.request.body}")
            self._logger.debug(f"Response: {response.json()}")
        except JSONDecodeError:
            self._logger.debug(f"Response: {response.text}")

    def get(self, resource: str) -> Union[dict, list]:
        """Perform a get request on resource."""
        req = f"{self.base_url}{resource}"
        self._logger.info(f"Fetching {req}")
        response = self.session.get(req)
        self._raise_for_status_and_log(response)
        # Filter unwanted response fields and guarantee result sorting
        return remove_keys(response.json(), UNWANTED_CFG_FIELDS)

    def create(self, resource: str, body: dict) -> None:
        """Create a new resource."""
        response = self.session.post(f"{self.base_url}{resource}", json=body, timeout=40)
        self._raise_for_status_and_log(response)
        self._logger.info(f"Created (one of) {self.base_url}{resource}")

    def update(self, resource: str, id: int, body: dict) -> None:
        """Update an existing resource."""
        response = self.session.put(f"{self.base_url}{resource}/{id}", json=body)
        if response.status_code == 400:
            # e.g. lidarr metadataprofile 'None' (default)
            self._logger.warning("Cannot update, likely a 'reserved' config item.")
            self._try_log_request_and_response(response)
        elif response.status_code == 405:
            # Resource does not have a PUT method, 'updating' the hard way
            # e.g. 'rootfolder' does not have this.
            self.delete(resource, id)
            del body['id']
            self.create(resource, body)
        else:
            self._raise_for_status_and_log(response)
        self._logger.info(f"Updated {self.base_url}{resource}/{id}")

    def delete(self, resource: str, id: int) -> None:
        """Delete existing resource with specified id."""
        req = f"{self.base_url}{resource}/{id}"
        self._logger.info(f"Deleting {req}")
        response = self.session.delete(req)
        if response.status_code == 405:
            # Some configs cannot be deleted, e.g. when a default must always exist.
            self._logger.warning("Delete method not allowed.")
            self._try_log_request_and_response(response)
            # Encountering this means config is not reflecting system state.
        elif response.status_code in [400, 500] and "in use" in response.json()['message']:
            # e.g. Readarr metadataprofile gave 400 when in use, and prowlarr appprofile gives 500
            self._logger.warning("Cannot delete resource that is still in use.")
            self._try_log_request_and_response(response)
        else:
            self._raise_for_status_and_log(response)
