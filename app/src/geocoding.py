import pandas as pd
import geopandas as gpd
import logging

log = logging.getLogger(__name__)

from app.src.geoapify import get_point_from_address, LowConfidence

class EmptyHeadQuarterAddress(Exception):
    pass


def process_csv_file(csvfile: str, n_entries: int = None) -> gpd.GeoDataFrame:
    """
    Processes CSV file and geocodes every entry. Handles QC for geocoding.

    :param csvfile: path to csv file
    :param n_entries: Optional number of entries to process
    :return:
    """
    df = pd.read_csv(csvfile)
    gc_list = []
    if n_entries:
        df = df[:n_entries]
    for indx, row in df.iterrows():
        addr = "{Street}, {Postal code}, {City}, {Country}".format(**row)
        log.debug(f'Looking up address: {addr}')
        try:
            gc_list.append([*row, *get_point_from_address(addr)])
        except LowConfidence:
            gc_list.append([*row, None, None])
            log.warning(f'No accurate value found for address {addr}')
    gdf = gpd.GeoDataFrame(data=gc_list,
                           columns=[*df.columns, 'geometry', 'match_type'],
                           geometry='geometry',
                           crs="EPSG:4326")
    return gdf


def hq_address_to_coords(hqfile: str):
    """
    Small function to geocode headquarter address

    :param hqfile: location of file containing hq address
    :return:
    """
    try:
        with open(hqfile, 'r') as f:
            l = f.readline()
    except FileNotFoundError:
        raise FileNotFoundError('Please create a file with HQ address. Define the file in the config file.')

    if l == "":
        raise EmptyHeadQuarterAddress('Please add HQ address to file.')

    p1 = get_point_from_address(l)
    return p1[0].y, p1[0].x
