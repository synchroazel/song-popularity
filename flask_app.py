from flask import Flask, render_template

from handlers.mqtt.mqtt_handler import MQTT_handler

mqtt_handler = MQTT_handler()

payload = mqtt_handler.subscribe('song-popularity/predictions', 'trending_now.json')

exec(f'payload={payload}')

last_update = payload['last_update']
trending_songs = payload['trending_songs']

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html',
                           last_update=last_update,
                           songs=trending_songs)
