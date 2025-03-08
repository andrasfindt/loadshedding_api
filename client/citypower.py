import logging
import socket

import requests


_LOGGER: logging.Logger = logging.getLogger(__package__)

BASE_API_URL = "https://api.citypower.co.za"
REQUEST_TIMEOUT_S = 5


class CityPowerAPI:

    def __init__(self):
        """Initializes class parameters""" 
        self.base_url = BASE_API_URL


    def query_api(self, endpoint: str, payload: dict = None):
        """
        Queries a given endpoint on the API with the specified payload

        Args:
            endpoint (string): The endpoint of the API

        Returns:
            The response object from the request

        """
        query_url = self.base_url + endpoint
        try:
            with requests.get(
                url=query_url, timeout=REQUEST_TIMEOUT_S, verify='/etc/ssl/certs/citypower.co.za.pem'
            ) as resp:
                return resp.json()
        except requests.HTTPError as exception:
            _LOGGER.error(
                "Error fetching information from %s. Response code: %s",
                query_url,
                exception.status,
            )
            raise


    def get_current_active_stage(self):
        stage = self.query_api('/loadshedding-schedule-service/find-current-active-stage')
        current_stage = int(stage)
        return current_stage
