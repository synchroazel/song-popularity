import random
import time
from paho.mqtt import client as mqtt_client


class MQTT_handler:

    def __init__(self, broker='broker.hivemq.com', port=1883):
        self.broker = broker
        self.port = port
        self.id = f'python-mqtt-{random.randint(0, 1000)}'
        self.client = None

        self.connect_mqtt()

    def connect_mqtt(self):

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("[INFO] Connected to MQTT Broker!")
            else:
                print(f"[ERROR] Failed to connect, return code {rc}")

        client = mqtt_client.Client(self.id)
        client.username_pw_set('username', 'password')
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        self.client = client

    def publish(self, msg, topic, retain=True):

        self.client.loop_start()

        time.sleep(0.5)

        result = self.client.publish(topic, msg, retain=retain, qos=2)
        status = result[0]

        if status == 0:
            print(f"[INFO] Message successfully sent to topic {topic}.")
        else:
            print(f"[ERROR] Failed to send message to topic {topic}.")

        self.client.loop_stop()
        self.client.disconnect()
        print(f'[INFO] Connection with {self.broker}:{self.port} closed.')

    def subscribe(self, topic):

        received_msg = None

        def on_message(client, userdata, msg):
            print(f"[INFO] Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            received_msg = msg.payload

        self.client.subscribe(topic)
        self.client.on_message = on_message



        self.client.loop_start()
        time.sleep(0.5)
        self.client.loop_stop()
        self.client.disconnect()
        print(f'[INFO] Connection with {self.broker}:{self.port} closed.')

        return received_msg
