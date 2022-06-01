import paho.mqtt.client as mqtt

broker = ""

client = mqtt.Client("ME")
client.username_pw_set("Publisher1", password="WINXCLUB")
client.connect("broker.hivemq.com")
client.subscribe("Songs_POP")
client.publish("Songs_ROCK", "Try number 3")
client.publish("Songs_POP", "Try pop")