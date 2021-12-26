from unittest import TestCase
import pandas as pd
import geopandas as gpd
from shapely import wkt

from app.src.postgis import (init_sqlalchemy,
                             insert_geodataframe_to_postgis,
                             truncate_db,
                             query_employees_from_postgis,
                             query_closest_from_postgis,
                             query_within_from_postgis)

geojsonfile = "../data/geodataframe.csv"


class TestWritingToPostGIS(TestCase):

    def setUp(self) -> None:
        df = pd.read_csv(geojsonfile)
        df['geometry'] = df['geometry'].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df, crs='epsg:4326')
        self.gdf = gdf
        self.engine = init_sqlalchemy(truncate=True)
        insert_geodataframe_to_postgis(self.engine, self.gdf, pid='test')

    def test_query_employees(self):
        gdf = query_employees_from_postgis(self.engine, pid='test')
        print(gdf.head())

    def test_query_closest_employee(self):
        gdf = query_closest_from_postgis(self.engine, pid='test', coords=(23.943, 61.476))
        print(gdf.head())

    def test_query_within_radius(self):
        gdf = query_within_from_postgis(self.engine, pid='test', coords=(23.943, 61.476), radius=1.)
        print(gdf.head())

    def tearDown(self) -> None:
        # truncate_db(self.engine)
        pass




