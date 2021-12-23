import pandas as pd
import geopandas as gpd
import logging

log = logging.getLogger(__name__)

from app.src.geoapify import get_point_from_address, LowConfidence


def process_csv_file(csvfile: str, n_entries: int = None):
    df = pd.read_csv(csvfile)
    gc_list = []
    if n_entries:
        df = df[:n_entries]
    for indx, row in df[:n_entries].iterrows():
        addr = "{Street}, {Postal code}, {City}, {Country}".format(**row)
        log.debug(f'Looking up address: {addr}')
        try:
            gc_list.append([*row, *get_point_from_address(addr)])
        except LowConfidence:
            gc_list.append([*row, None, None])
            log.warning(f'No accurate value found for address {addr}')
    gdf = gpd.GeoDataFrame(data=gc_list, columns=[*df.columns, 'geometry', 'match_type'], geometry='geometry', crs="EPSG:4326")
    return gdf