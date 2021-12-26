from unittest import TestCase
import pandas as pd
import geopandas as gpd
from shapely import wkt

from app.src.postgis import init_sqlalchemy, insert_geodataframe_to_postgis, truncate_db, query_employees_from_postgis

geojsonfile = "../data/geodataframe.csv"  # This file has been removed, please re-create it.


class TestWritingToPostGIS(TestCase):

    def setUp(self) -> None:
        df = pd.read_csv(geojsonfile)
        df['geometry'] = df['geometry'].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df, crs='epsg:4326')
        self.gdf = gdf
        self.engine = init_sqlalchemy()

    def test_insert_geodataframe(self):
        try:
            insert_geodataframe_to_postgis(self.engine, self.gdf, pid='test')
        except Exception as e:
            self.fail(f"get_point_from_address() raised {e} unexpectedly!")

    def tearDown(self) -> None:
        # truncate_db(self.engine)
        pass

