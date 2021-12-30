# Geocode addresses with Flask and PostGIS

Flask app to geocode CSV-files with GeoAPIfy, do a few processing steps, and display results in the map.

## Quickstart 


**add address for reference**
```bash
echo "<street>, <postcode>, <city>, <country>" > data/headquarter.txt
```
> Hint: make sure that the address is spelled correctly and has the corresponding postcode. This increases the chance of a correct match and accurate geolocation.

**check settings in config file**
```bash
cat config.py
```

**create user config** 
```bash
echo """
GEOAPIFYKEY = 'd2d6flob6xxxxxxxxxxx4b4002d1'
DB_USER = 'pguser'
DB_PWD = 'pgpwd'
""" > user_config.py
```

**Build container**
 ```bash
docker-compose build --no-cache
 ```

**Run the app**
 ```bash
docker-compose up
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
   2. find the closest point to the headquarter (see issue [#28][i28])
   3. ~~find points within 10km distance to headquarter~~ (see issue [#13][i13])
   4. ~~get additional statistics~~ (see issue [#14][i14])


## Issues

These are the most pressing issues.

- fix issues with postgis database (broken spatial reference)
- finish open tasks (issue [#13][i13] and issue [#14][i14])


## Usage hints

- be patient
  - currently geocoding takes a while (free tier, see issue [#16][i16])
  - you can change the number of lookups in the config
- check the log.
  - saved to `/log` folder
  - warnings (e.g. failed geocoding, issue [#18][i18]) are displayed here
- a lot is still work in progress, feel free to participate.


[i13]: https://github.com/MBennGit/addr-to-pg/issues/13
[i14]: https://github.com/MBennGit/addr-to-pg/issues/14
[i16]: https://github.com/MBennGit/addr-to-pg/issues/16
[i18]: https://github.com/MBennGit/addr-to-pg/issues/18
[i28]: https://github.com/MBennGit/addr-to-pg/issues/28
