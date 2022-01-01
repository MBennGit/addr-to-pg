"""
Experience with PostGIS, SQLAlchemy, GeoAlchemy2 is pretty basic.
There are certainly better ways to handle this.
"""
import random
import string
from typing import Tuple

from geopy import distance
from geoalchemy2 import Geometry
import geopandas as gpd
from sqlalchemy import create_engine, MetaData, inspect, Table, and_
from sqlalchemy import func, select
from sqlalchemy import Column, String
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base

from config import DB_USER, DB_PWD, DB_SERVER, DB_NAME, DB_PORT

import logging

log = logging.getLogger(__name__)

Base = declarative_base()


class Employees(Base):
    """
    Model for PostGIS Database. This one stores the geocoded employee dataset.

    Issues:
        - QGIS does not show right Coordinate system
    """
    __tablename__ = 'employees'
    globalid = Column(String(20), primary_key=True)
    name = Column(String(50))
    street = Column(String(50))
    postal_code = Column(String(10))
    city = Column(String(50))
    country = Column(String(50))
    match_type = Column(String(50))
    pid = Column(String(50))
    geometry = Column(Geometry('POINT', srid=4326))  # TODO: QGIS does not display correct coordinate system


def init_sqlalchemy(user: str = DB_USER,
                    pwd: str = DB_PWD,
                    server: str = DB_SERVER,
                    port: str = DB_PORT,
                    name: str = DB_NAME, truncate: bool = False) -> Engine:
    """
    Create sqlalchemy engine, truncate the postgis table

    :param user: Postgis User
    :param pwd: Postgis Password
    :param server: Postgis Server
    :param port: Postgis Port
    :param name: Postgis Name
    :param truncate: Boolean, truncate on init or not.
    :return: SQL Alchemy Engine
    """
    log.debug('Create engine.')
    engine_ = create_engine(f"postgresql://{user}:{pwd}@{server}:{port}/{name}")

    log.debug('Create or truncate tables.')
    create_or_truncate_postgis_tables(engine_, truncate=truncate)
    return engine_


def insert_geodataframe_to_postgis(engine_, gdf: gpd.GeoDataFrame, pid: str):
    """
    Add geodataframe to postgis.
    The geodataframe must have the right columns.

    :param engine_: SQLAlchemy Engine
    :param gdf: Geodataframe, must have the correct columns.
    :param pid: Process ID
    :return:
    """
    gdf['pid'] = pid
    gdf['globalid'] = gdf['pid'].apply(lambda x: ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)))
    gdf = gdf.rename(columns={cname: cname.lower().replace(' ', '_') for cname in gdf.columns})
    gdf.to_postgis('employees', engine_, if_exists='append')


def create_or_truncate_postgis_tables(engine_, truncate: bool = False):
    """
    Setup PostGIS database. If exist, truncate. Else create.

    :param engine_: SQLAlchemy Engine
    :param truncate: Boolean to truncate table or leave data inside.
    :return:
    """
    t1 = 'employees'
    insp = inspect(engine_)
    if not insp.has_table(t1):
        Base.metadata.create_all(engine_)
    else:
        if truncate:  # TODO: Truncating not advised here, instead delete data by pid.
            truncate_db(engine_)

    # TODO: change the way this is handled, use metadata
    d = {t1: Employees.__table__}
    return d


def truncate_db(engine_):
    """
    Linked tables are more complex to truncate.
    Source: https://gist.github.com/absent1706/3ccc1722ea3ca23a5cf54821dbc813fb#gistcomment-3107613
    delete all table data (but keep tables)
    we do cleanup before test 'cause if previous test errored,
    DB can contain dust

    :param engine_: SQLAlchemy Engine
    :return:
    """
    # TODO: Not using linked tables, so this is probably overkill. Can be replaced.
    meta = MetaData()
    meta.reflect(bind=engine_)  # https://stackoverflow.com/a/64803347
    con = engine_.connect()
    trans = con.begin()
    for table in meta.sorted_tables:
        con.execute(f'ALTER TABLE "{table.name}" DISABLE TRIGGER ALL;')
        log.debug(f'Deleting data from {table.name}')
        con.execute(table.delete())
        con.execute(f'ALTER TABLE "{table.name}" ENABLE TRIGGER ALL;')
    trans.commit()


def query_employees_from_postgis(engine_, pid: str, q_table=Employees.__table__) -> gpd.GeoDataFrame:
    """
    Get employee data from PostGIS. Read to Geodataframe.

    :param engine_: SQLAlchemy Engine
    :param pid: ProcessID to filter pgtable
    :param q_table: Table Schema
    :return: Geodataframe with results
    """
    s = select([q_table.c.name, q_table.c.geometry.label('geom')]).filter(q_table.c.pid == pid)
    log.debug(str(s).replace('\n', '').replace('\r', ''))

    with engine_.connect() as conn:
        gdf = gpd.read_postgis(sql=s, con=conn)  # TODO: Causing a warning because of coordinate system (see above)
    log.debug(f'Returned {len(gdf)} employees from PostGIS.')
    return gdf


def query_closest_from_postgis(engine_: Engine,
                               pid: str,
                               coords: Tuple[float, float],
                               q_table: Table = Employees.__table__) -> gpd.GeoDataFrame:
    """
    Query closest employee from postgis

    :param engine_: SQLAlchemy Engine
    :param pid: ProcessID to filter pgtable
    :param coords: Tuple of lat, lon (y, x) coords
    :param q_table: Table Schema
    :return: Geodataframe with results
    """

    # after https://gis.stackexchange.com/a/283451
    log.debug(f'Searching closest point for coordinates {coords}')
    s = select([q_table.c.name, q_table.c.geometry.label('geom')]). \
        filter(q_table.c.pid == pid). \
        order_by(func.ST_Distance(q_table.c.geometry.label('geom'),
                                  func.Geometry(func.ST_GeographyFromText(
                                      'POINT({} {})'.format(coords[1], coords[0]))))).limit(1)
    log.debug(str(s).replace('\n', '').replace('\r', ''))

    with engine_.connect() as conn:
        gdf = gpd.read_postgis(sql=s, con=conn)  # TODO: Causing a warning because of coordinate system (see above)
    log.debug(f'Closest employee is {gdf.iloc[0]["name"]}')
    return gdf


def geopy_within_radius(gdf: gpd.GeoDataFrame,
                        coords: Tuple[float, float],
                        radius: float) -> gpd.GeoDataFrame:
    """
    Query within radius from coords from postgis.

    :param gdf: Geodataframe
    :param coords: Tuple of lat, lon (y, x) coords
    :param radius: radius in kilometres
    :return: Geodataframe with results
    """

    # https://geopy.readthedocs.io/en/stable/#module-geopy.distance
    def get_distance(c):
        p1 = (c.x, c.y)
        p2 = coords
        return distance.distance(p1, p2).km

    gdf['distance'] = gdf['geom'].apply(lambda x: get_distance(x))
    return gdf.loc[gdf['distance'] < radius]
