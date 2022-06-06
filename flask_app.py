from flask import Flask, render_template

from handlers.mqtt.mqtt_handler import MQTT_handler

mqtt_handler = MQTT_handler()

# Subscribe to get the latest msg with predictions
payload = mqtt_handler.subscribe('song-popularity/predictions')

# From a <str> to an actual dictionary
exec(f'payload={payload}')

last_update = payload['last_update']
trending_songs = payload['trending_songs']

app = Flask(__name__)


# Renders an HTML page (passing contents from the received `payload`)

@app.route('/')
def index():
    return render_template('index.html',
                           last_update=last_update,
                           songs=trending_songs)
