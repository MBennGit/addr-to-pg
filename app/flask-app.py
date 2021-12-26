"""
based on
https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
and
https://python-visualization.github.io/folium/flask.html
"""

import os
import string
import random

from flask import Flask, flash, request, redirect, url_for
import folium
import logging.config

try:
    logging.config.fileConfig(r'../logging.conf')
except KeyError:
    raise FileNotFoundError(r'../logging.conf')

log = logging.getLogger(__name__)

from app.src.geocoding import process_csv_file
from app.src.postgis import init_sqlalchemy, create_or_truncate_postgis_tables, insert_geodataframe_to_postgis, \
    query_employees_from_postgis, query_closest_from_postgis

UPLOAD_FOLDER = '../uploads/'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/process/<csvfile>')
def process_data(csvfile: str):
    """This does the main work"""
    # TODO: split this into several functions, use celery worker.
    log.debug(f'Loading {csvfile}')
    # Geocode the entries in csv file, returns a gdf back
    gdf = process_csv_file(os.path.join(app.config['UPLOAD_FOLDER'], csvfile), n_entries=10)
    log.debug(f'Read and geocoded {len(gdf)} entries.')

    # remove values that have no geometry (no proper geocoding)
    # TODO: Improve the way this is handled. Warnings etc.
    gdf = gdf.loc[gdf['geometry'].notna()]
    log.debug(f'{len(gdf)} entries are valid.')

    # add all entries to postgis
    insert_geodataframe_to_postgis(engine, gdf, csvfile)

    return redirect(url_for('map_index', csvfile=csvfile))


@app.route('/map/<csvfile>')
def map_index(csvfile: str):
    """
    This function load data (all employees, closest employees) from postgis and displays it on the app.

    :param csvfile: process id / csvfile
    :return:
    """
    employees_gdf = query_employees_from_postgis(engine, pid=csvfile)
    closest_gdf = query_closest_from_postgis(engine, pid=csvfile,
                                             coords=(24.832, 60.181)) # TODO: use hq address + geoapify
    # display things on the map
    start_coords = (60.172, 24.941)
    folium_map = folium.Map(location=start_coords, zoom_start=6)
    # using the geodataframe to display data on the map
    employees_geojson = employees_gdf.to_crs(epsg='4326').to_json()
    closest_geojson = closest_gdf.to_crs(epsg='4326').to_json()
    employees_points = folium.features.GeoJson(employees_geojson)
    closest_points = folium.features.GeoJson(closest_geojson)
    # TODO: add layers, legend, change symbology
    folium_map.add_child(employees_points)
    folium_map.add_child(closest_points) # TODO: change symbology
    return folium_map._repr_html_()


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """Entry point for flask. Simple upload formular. Will redirect to processing. """
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('process_data', csvfile=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == '__main__':
    engine = init_sqlalchemy()
    create_or_truncate_postgis_tables(engine, truncate=True)
    app.run(debug=True)
