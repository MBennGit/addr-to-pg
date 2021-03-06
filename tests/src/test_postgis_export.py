from unittest import TestCase
import pandas as pd
import geopandas as gpd
from shapely import wkt

from app.src.postgis import (init_sqlalchemy,
                             insert_geodataframe_to_postgis,
                             truncate_db,
                             query_employees_from_postgis,
                             query_closest_from_postgis,
                             geopy_within_radius)

geojsonfile = "../data/fullgdf.csv" # This file has been removed, please re-create it.


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
        sample = pd.concat([self.gdf.sample() for _ in range(10)])
        for indx, row in sample.iterrows():
            x = round(row['geometry'].x, 4)
            y = round(row['geometry'].y, 4)
            res = query_closest_from_postgis(self.engine, pid='test', coords=(y, x))
            self.assertEqual(res.iloc[0]['name'], row['Name'])

    def test_geopy_within_radius(self):
        gdf = query_employees_from_postgis(self.engine, pid='test')
        sample = pd.concat([self.gdf.sample() for _ in range(10)])
        for indx, row in sample.iterrows():
            x = round(row['geometry'].x, 4)
            y = round(row['geometry'].y, 4)
            res = geopy_within_radius(gdf, coords=(x, y), radius=0.1)
            self.assertIn(row['Name'], res['name'].unique())

    def tearDown(self) -> None:
        # truncate_db(self.engine)
        pass




