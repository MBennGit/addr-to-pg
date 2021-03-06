from typing import Tuple

import requests
from requests.structures import CaseInsensitiveDict
from shapely.geometry import Point, shape

from config import GEOAPIFYKEY, VALID_MATCH_TYPES
import logging

log = logging.getLogger(__name__)


class LowConfidence(Exception):
    pass


class NoResultsReturned(Exception):
    pass


baseurl = "https://api.geoapify.com/v1/geocode/search"

headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"


def get_point_from_address(address: str = '',
                           api_key: str = GEOAPIFYKEY,
                           url: str = baseurl) -> Tuple[Point, str]:
    """
    Takes address as a string and used GeoAPIfy to geocode the address.

    :param address: Address in as string
    :param api_key: API KEY from user_config.py
    :param url: GeoAPIfy Endpoint for geocoding.
    :return: Returns Shaply Point object and the match_type.
    """
    payload = {'text': address, 'apiKey': api_key}
    # TODO: Improve Error handling for timeouts, loss of connection etc
    resp = requests.get(url, headers=headers, params=payload)
    d = resp.json()
    if 'error' in d:
        raise Exception(d['message'])
    if len(d['features']) == 0:
        raise NoResultsReturned
    f1 = d['features'][0]
    match_type = f1['properties']['rank']['match_type']
    if match_type not in VALID_MATCH_TYPES:
        raise LowConfidence(f"{match_type}: {address}")
    return shape(resp.json()['features'][0]['geometry']), match_type
