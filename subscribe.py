import argparse
import os
import pickle
from pprint import pprint
from sklearn.preprocessing import StandardScaler

from handlers.music.spotify_handler import SpotifyHandler
from handlers.mysql.mysql_connector import MYSQL_connector
from handlers.mqtt.mqtt_handler import MQTT_handler

mqtt_handler = MQTT_handler()

mqtt_handler.subscribe('song-popularity/predictions', 'trending_now.json')


