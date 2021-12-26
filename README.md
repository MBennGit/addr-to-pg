# Geocode Address with Flask and Postgis

Flask app to geocode CSV-files with GeoAPIfy, do a few processing steps, and display results in the map.

# Quickstart 

Create docker container with PostGIS 

```bash
 docker run --name=pgdemo -d -e \
 POSTGRES_USER=pguser -e POSTGRES_PASS=pgpwd -e POSTGRES_DBNAME=ske \
 -e ALLOW_IP_RANGE=0.0.0.0/0 -p5432:5432 -v pg_data:/var/lib/postgresql \
 --restart=always kartoza/postgis
 ```

Install the requirements.
```
pip install -r requirements.txt
```


add address for headquarters
```bash
echo "Street, Postcode, City, Country" > data/headquarters.txt
```

create user config 
```bash
echo """GEOAPIFYKEY = 'd2d6flob6xxxxxxxxxxx4b4002d1'
DB_USER = 'pguser'
DB_PWD = 'pgpwd'
""" > user_config.py
```


Run the app
 ```bash
 python app/flask-app.py
 ```

1. **Select and Upload CSV file.** Make sure the format is correct, see [template.csv](https://github.com/MBennGit/addr-to-pg/blob/main/data/template.csv)
2. **Wait**. for the background process to finish. 
3. **Find** the results in the webmap.
