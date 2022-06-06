# Predicting Spotify songs popularity

A big data system able to predict popularity in 6 and 12 months of recently trending songs.

The architecture of the system includes a MySQL database in which information about songs stored, a set of models to
predict long and short term popularity, a set of script to initialize and keep the database updated, and to communicate
predictions to external users through MQTT, and lastly a package of handlers to easily interact with Spotify APIs.

The serving layer of the system, including an HTML interface through Flask, comes dockerized and easy-to-use.

## Installation

Simply pull our docker image with:

```bash
docker pull ghcr.io/synchroazel/song-popularity-img:latest
```

## Usage

Start the docker image with:

```bash
docker start -p -d 8000:8000 ghcr.io/synchroazel/song-popularity-img
```

and navigate to `127.0.0.1:8000` to see the dashboard.

## Backend configuration

The main scripts executed in back-end are:

- `init_db.py` to **initialize the database** for the first time and ingest an initial set of data
- `update_db.py` to **update the database** weekly, to ingest data on currently trending songs
- `publish.py` to **predict and publish the predictions** sent through an MQTT broker
- `train_models.py` to **train the models** with available data every week, to keep the models trained on the most data

The general workflow in backend is:

- only once: `init_db.py` <br>
- then, weekly: `update_db.py` → `publish.py` → `train_models.py`

### Initialize the db

The following is executed once to initialize the database:

```
python3 init_db.py \
--mysql_host song-popularity-db.cny8kp4zmknf.us-east-1.rds.amazonaws.com \
--mysql_user admin \
--mysql_password <REDACTED> \
--mysql_db song-popularity-db
```

- `mysql_host` `mysql_user` `mysql_admin` are used to connect to a running MySQL instance
- `mysql_db` is the name of the database to create

For debugging purposes, one can also pass `limit` to limit the number of artists initially imported.

### Update the db

The following can be used to initialize the database and populate it with a set of trending artists from the past 2
years.

```bash
python3 update_db.py \
--mysql_host song-popularity-db.cny8kp4zmknf.us-east-1.rds.amazonaws.com \
--mysql_user admin \
--mysql_password '<REDACTED>' \
--mysql_db song-popularity-db
```

- `mysql_host` `mysql_user` `mysql_admin` are used to connect to a running MySQL instance containing the db `mysql_db`

Again, for debugging purposes, one can also pass `limit` to limit the number of trending tracks and albums to import.

### Publish predictions

The following can be used to get predictions for currently trending songs and publish them through the MQTT broker. In
order to collect information from the db, credentials are passed (with the same args as before) to connect to the MySQL
instance.

```bash
python3 publish.py \
--mysql_host song-popularity-db.cny8kp4zmknf.us-east-1.rds.amazonaws.com \
--mysql_user admin \
--mysql_password '<REDACTED>' \
--mysql_db song-popularity-db
```

- `mysql_host` `mysql_user` `mysql_admin` are used to connect to a running MySQL instance containing the db `mysql_db`

### Train models

The following is used to train the models on the whole database:

```bash
python3 train_models.py \
--mysql_host song-popularity-db.cny8kp4zmknf.us-east-1.rds.amazonaws.com \
--mysql_user admin \
--mysql_password '<REDACTED>' \
--mysql_db song-popularity-db
```

- `mysql_host` `mysql_user` `mysql_admin` are used to connect to a running MySQL instance containing the db `mysql_db`

### Verifying db update

The scripts above run at the server boot, scheduled every Monday at 12:00 CEST. The machine then stop after 3 hours.
Inside the virtual machine, one can verify the time of the last update and the logs from the scripts execution with:

```bash
cat /tmp/rc.local.log
```

### Module `secrets.py`

It contains the object ```SpotifyClientCredentials``` which stores the `client_id` and the `client_secret` to interact
with Spotify APIs. It is not meant to be shared publicly.

Here is the file structure, in case the user might want to recreate it:

```python
from spotipy.oauth2 import SpotifyClientCredentials

sp_credentials = SpotifyClientCredentials(client_id='<REDACTED>',
                                          client_secret='<REDACTED>')
```