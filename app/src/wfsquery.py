# based on https://gis.stackexchange.com/a/302346

from fiona.errors import DriverError
from requests import Request
import geopandas as gpd
from owslib.wfs import WebFeatureService
import logging

log = logging.getLogger(__name__)
url = "https://geo.stat.fi/geoserver/postialue/wfs"
wfs = WebFeatureService(url=url)

layer = 'postialue:pno_tilasto_2021'
WFS_GEOJSON = '../../data/geostatfi_wfs.json'
COLS = ['id', 'namn', 'nimi', 'tr_mtu', 'geometry']


def get_wfs_data():
    gdf = check_for_preloaded_wfs_data()
    if len(gdf) == 0:
        gdf = download_data_from_wfs()
        gdf.to_file(WFS_GEOJSON, driver='GeoJSON')
    return gdf


def download_data_from_wfs():
    log.info('Downloading WFS data.')
    params = dict(service='WFS', version="1.0.0", request='GetFeature',
                  typeName=layer, outputFormat='json')
    # TODO: ErrorHandling here (timeout etc)
    q = Request('GET', url, params=params).prepare().url
    gdf = gpd.read_file(q)
    gdf = gdf[COLS]
    return gdf


def check_for_preloaded_wfs_data(file_path: str = WFS_GEOJSON) -> gpd.GeoDataFrame:
    try:
        gdf = gpd.read_file(file_path)
        gdf = gdf[COLS]
        log.info('Found local WFS data.')
        return gdf
    except (FileNotFoundError, DriverError) as e:
        log.info('No preloaded WFS data found.')
        return gpd.GeoDataFrame()


if __name__ == "__main__":
    wfsdata = get_wfs_data()
    print(wfsdata)
