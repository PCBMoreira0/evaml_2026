from paho.mqtt import client as mqtt_client

import sys

import os

import numpy as np

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
parent_dir = os.path.abspath(os.path.join(BASE_DIR, "../../.."))
sys.path.append(parent_dir)
parent_dir = os.path.abspath(os.path.join(BASE_DIR, "../.."))
sys.path.append(parent_dir)


import config # Module with network device configurations.

import robot_profile


broker = config.MQTT_BROKER_ADRESS # Broker address.
port = config.MQTT_PORT # Broker Port.
sim_base_topic = robot_profile.SIMULATOR_BASE_TOPIC
robot_base_topic = robot_profile.ROBOT_BASE_TOPIC

config.ROSE_ROBOT_AFFECTIVE_STATE_TOPIC
config.PULSE_USER_AFFECTIVE_STATE_TOPIC
class SharedStateSync(): # 
    def __init__(self, robot_memory):

        self.robot_memory = robot_memory

        # MQTT
        # The callback for when the client receives a CONNACK response from the server.
        def on_connect(client, userdata, flags, rc):
            # Subscribing in on_connect() means that if we lose the connection and
            # Reconnect then subscriptions will be renewed.
            # Here, it will be received the robot affective state and the user affective state from ROSE and PULSE
            # Então, os valores serão armazenados na memória do robô tornado-se acessíveis aos módulos da EvaML
            client.subscribe(topic=[(sim_base_topic + config.ROSE_ROBOT_AFFECTIVE_STATE_TOPIC, 1), ]) # Simulator topic
            client.subscribe(topic=[(robot_base_topic + config.ROSE_ROBOT_AFFECTIVE_STATE_TOPIC, 1), ]) # Robot topic
            client.subscribe(topic=[(sim_base_topic + config.PULSE_USER_AFFECTIVE_STATE_TOPIC, 1), ]) # Simulator topic
            client.subscribe(topic=[(robot_base_topic + config.PULSE_USER_AFFECTIVE_STATE_TOPIC, 1), ]) # Robot topic
            print("Shared State Sync - Connected.")



        def on_message(client, userdata, msg):
            if (msg.topic == sim_base_topic + config.ROSE_ROBOT_AFFECTIVE_STATE_TOPIC or msg.payload == robot_base_topic + config.ROSE_ROBOT_AFFECTIVE_STATE_TOPIC):
                
                self.robot_memory.set_robot_affective_state(np.array(msg.payload.decode().split(","), dtype=float))
                print("############# Message received", msg.payload.decode())



        # Run the MQTT client thread.
        client = mqtt_client.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        try:
            client.connect(broker, port)
        except:
            print ("Unable to connect to Broker.")
            exit(1)

        # You cannot use the "forever" method (as in other modules) because it blocks not allowing
        # for the graphical interface thread loop to execute.
        client.loop_start()