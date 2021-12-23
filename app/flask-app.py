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

from app.src.geocoding import process_csv_file

try:
    logging.config.fileConfig(r'../logging.conf')
except KeyError:
    raise FileNotFoundError(r'../logging.conf')

log = logging.getLogger(__name__)

UPLOAD_FOLDER = '../uploads/'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/map/<csvfile>')
def map_index(csvfile):
    gdf = process_csv_file(os.path.join(app.config['UPLOAD_FOLDER'], csvfile), n_entries=5)
    start_coords = (60.172, 24.941)
    folium_map = folium.Map(location=start_coords, zoom_start=8)
    geojson = gdf.to_crs(epsg='4326').to_json()
    points = folium.features.GeoJson(geojson)
    folium_map.add_child(points)
    return folium_map._repr_html_()


@app.route('/', methods=['GET', 'POST'])
def upload_file():
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
            return redirect(url_for('map_index', csvfile=filename))
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
    app.run(debug=True)