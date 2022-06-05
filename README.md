# Predicting a song popularity

A big data system able to predict popularity in 6 and 12 months of recently trending songs.

The overall structure of the system consists of a package of handlers to interact with Spotify APIs, a MySQL database in
which information about songs stored, a set of models to predict long and short term popularity, a set of script to
initialize and keep the database updated, and to communicate predictions to external users through MQTT.

The serving layer of the system, including an HTML interface served through Flask, come dockerized and easy-to-use.

## End-user installation

[...]

## Backend configuration

The main script that can be executed on backend are:

- **Initialize the database** through `init_db.py`
  - executed only once, to initialize the db for the first time and ingest an initial set of data
- **Update the database** through `update_db.py`
  - executed weekly, to ingest data on currently trending songs
- **Predict and publish the results** through `publish.py`
  - executed weekly, to predict popularities and send predictions to the MQTT broker 
- **Train the models** through `train_models.py`
  - executed weekly, once predictions have been made, to keep the models trained on the whole database

The general workflow in backend is:

- only once: `init_db.py` <br>
- then, weekly: `update_db.py` → `publish.py` → `train_models.py`

### Initialize the db

The following can be used to initialize the database.

```
python3 init_db.py \
--mysql_host song-popularity-db.cny8kp4zmknf.us-east-1.rds.amazonaws.com \
--mysql_user admin \
--mysql_password <REDACTED> \
--mysql_db song-popularity-db
```

- `mysql_host` `mysql_user` `mysql_admin` are used to connect to a running MySQL instance
- `mysql_db` is the name of the database to create.

For debugging purposes, you can also pass:

- `limit` to limit the number of artists initially imported
- `skipto` to skip to a specific phase of data ingestion

Please refer to `init_db.py --help` for more information.

### Update the db

The following can be used to initialize the database and populate it with a set of trending artists from the past three
years (imported from popularity charts from 2018, 2019, 2020, 2021)

```
python3 update_db.py \
--mysql_host song-popularity-db.cny8kp4zmknf.us-east-1.rds.amazonaws.com \
--mysql_user admin \
--mysql_password <REDACTED> \
--mysql_db song-popularity-db \
```

- `mysql_host` `mysql_user` `mysql_admin` are used to connect to a running MySQL instance containing the db `mysql_db`

For debugging purposes, you can also pass:

- `limit` to limit the number of artists initially imported
- `skipto` to skip to a specific phase of data ingestion

Please refer to `update_db.py --help` for more information.

### Publish predictions

The following can be used to get predictions for currently trending songs and publish them to the MQTT broker. In order
to collect information from the db, credentials are passed (with the same args as before) to connect to the MySQL instance.

```
python3 publish.py \
--mysql_host song-popularity-db.cny8kp4zmknf.us-east-1.rds.amazonaws.com \
--mysql_user admin \
--mysql_password new_tracks \
--mysql_db song-popularity-db
```

- `mysql_host` `mysql_user` `mysql_admin` are used to connect to a running MySQL instance containing the db `mysql_db`

### Train models

The following is used to train the models on the whole database. In order to collect information from the db,
credentials are passed (with the same args as before) to connect to the MySQL instance.

```
python3 train_models.py \
--mysql_host song-popularity-db.cny8kp4zmknf.us-east-1.rds.amazonaws.com \
--mysql_user admin \
--mysql_password <REDACTED> \
--mysql_db song-popularity-db
```

- `mysql_host` `mysql_user` `mysql_admin` are used to connect to a running MySQL instance containing the db `mysql_db`