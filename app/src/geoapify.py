import requests
from requests.structures import CaseInsensitiveDict
from shapely.geometry import Point, shape

from config import geoapikey


baseurl = "https://api.geoapify.com/v1/geocode/search"

headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"


def get_point_from_address(address: str = '', api_key: str = geoapikey, url: str = baseurl) -> Point:
    payload = {'text': address, 'apiKey': api_key}
    resp = requests.get(url, headers=headers, params=payload)
    return shape(resp.json()['features'][0]['geometry'])

