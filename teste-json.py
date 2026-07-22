import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "SIMULATOR/PERCEPTION"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

message = {
    "action": "start",
    "sources": ["FER", "TER"]
}

payload = json.dumps(message)


client.publish(TOPIC, payload)

client.disconnect()

data = json.loads(payload)

print(data.get("sources")[0])