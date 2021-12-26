# Geocode addresses with Flask and PostGIS

Flask app to geocode CSV-files with GeoAPIfy, do a few processing steps, and display results in the map.

## Quickstart 

**Create docker container with PostGIS** 

```bash
 docker run --name=pgdemo -d -e \
 POSTGRES_USER=pguser -e POSTGRES_PASS=pgpwd -e POSTGRES_DBNAME=ske \
 -e ALLOW_IP_RANGE=0.0.0.0/0 -p5432:5432 -v pg_data:/var/lib/postgresql \
 --restart=always kartoza/postgis
 ```

**Install the requirements.**
```
pip install -r requirements.txt
```


**add address for reference**
```bash
echo "<street>, <postcode>, <city>, <country>" > data/headquarter.txt
```

**create user config** 
```bash
echo """
GEOAPIFYKEY = 'd2d6flob6xxxxxxxxxxx4b4002d1'
DB_USER = 'pguser'
DB_PWD = 'pgpwd'
""" > user_config.py
```


**Run the app**
 ```bash
 python app/flask-app.py
 ```

**Use app in browser**

Navigate to [app](http://127.0.0.1:5000)

1. **Select** and **Upload** CSV file. Make sure the format is correct, see [template.csv](https://github.com/MBennGit/addr-to-pg/blob/main/data/template.csv)
2. **Wait**. for the background process to finish. 
3. **See** the results in the webmap.


## Workflow

When the file is uploaded to the app the following steps are performed:

1. Create a process ID `pid` for the csvfile and save the file to `/uploads`
2. Navigate to endpoint `http://127.0.0.1:5000/process/<pid>`
   1. each row of the csvfile is geocoded with GeoAPIfy (this takes a while)
   2. once all rows are geocoded they are stored to postgis database (tablename: `employees`)
3. Navigate to endpoint `http://127.0.0.1:5000/map/<pid>`
   1. load all the points from postgis database
   2. find the closest point to the headquarter
   3. ~~find points within 10km distance to headquarter~~ (see issue [#13][i13])
   4. ~~get additional statistics~~ (see issue [#14][i14])


## Issues

These are the most pressing issues.

- symbology for results (currently indistinguishable from each other)
- add docker-compose wrapper for project to deploy and run it easier (issue #2)
- fix issues with postgis database (broken spatial reference)
- finish open tasks (issue [#13][i13] and issue [#14][i14])


## Usage hints

- be patient: currently geocoding takes a while (free tier, see issue [#16][i16])
- check the log.
  - saved to `/log` folder
  - warnings (e.g. failed geocoding, issue [#18][i18]) are displayed here
- a lot is still work in progress, feel free to participate.


[i13]: https://github.com/MBennGit/addr-to-pg/issues/13
[i14]: https://github.com/MBennGit/addr-to-pg/issues/14
[i16]: https://github.com/MBennGit/addr-to-pg/issues/16
[i18]: https://github.com/MBennGit/addr-to-pg/issues/18
