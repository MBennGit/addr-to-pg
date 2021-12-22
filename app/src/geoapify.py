import requests
from requests.structures import CaseInsensitiveDict
from shapely.geometry import Point, shape

from config import GEOAPIFYKEY, VALID_MATCH_TYPES


class LowConfidence(Exception):
    pass


class NoResultsReturned(Exception):
    pass


baseurl = "https://api.geoapify.com/v1/geocode/search"

headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"


def get_point_from_address(address: str = '', api_key: str = GEOAPIFYKEY, url: str = baseurl) -> Point:
    payload = {'text': address, 'apiKey': api_key}
    resp = requests.get(url, headers=headers, params=payload)
    d = resp.json()
    if len(d['features']) == 0:
        raise NoResultsReturned
    f1 = d['features'][0]
    match_type = f1['properties']['rank']['match_type']
    if f1['properties']['rank']['match_type'] not in VALID_MATCH_TYPES:
        raise LowConfidence(f"{match_type}: {address}")
    return shape(resp.json()['features'][0]['geometry'])
