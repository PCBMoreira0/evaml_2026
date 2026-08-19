# Esta classe permite que outros componentes (distribuídos) possam armazenar determinados valores na memória do robô.
# A informação chega por mensagem mqtt e, como esta classe tem acesso à memória física do robô, a informação é salva lá.

from paho.mqtt import client as mqtt_client

import sys

import os

import json

import numpy as np

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
parent_dir = os.path.abspath(os.path.join(BASE_DIR, "../../.."))
sys.path.append(parent_dir)
parent_dir = os.path.abspath(os.path.join(BASE_DIR, "../.."))
sys.path.append(parent_dir)


import config # Module with network device configurations.

import robot_package.robot_profile as robot_profile


broker = config.MQTT_BROKER_ADRESS # Broker address.
port = config.MQTT_PORT # Broker Port.
sim_base_topic = robot_profile.SIMULATOR_BASE_TOPIC
robot_base_topic = robot_profile.ROBOT_BASE_TOPIC



class SharedStateSync(): # 
    def __init__(self, robot_memory):

        self.robot_memory = robot_memory
        print("Id no Shared:", id(self.robot_memory))

        # MQTT
        # The callback for when the client receives a CONNACK response from the server.
        def on_connect(client, userdata, flags, rc):
            # Subscribing in on_connect() means that if we lose the connection and
            # Reconnect then subscriptions will be renewed.
            # Here, it will be received the robot affective state and the user affective state from ROSE and PULSE
            # Então, os valores serão armazenados na memória do robô tornado-se acessíveis aos módulos da EvaML
            # client.subscribe(topic=[(sim_base_topic + "/" + config.ROBOT_AFFECTIVE_STATE_TOPIC, 1), ]) # Simulator topic
            # client.subscribe(topic=[(sim_base_topic + "/" + config.USER_AFFECTIVE_STATE_TOPIC, 1), ]) # Simulator topic
            client.subscribe(topic=[(robot_base_topic + "/" + config.ROBOT_AFFECTIVE_STATE_TOPIC, 1), ]) # Robot topic
            client.subscribe(topic=[(robot_base_topic + "/" + config.USER_AFFECTIVE_STATE_TOPIC, 1), ]) # Robot topic
            client.subscribe(topic=[(robot_base_topic + "/" + config.ROBOT_BEHAVIOR_STATE_TOPIC, 1), ]) # Robot topic


        def on_message(client, userdata, msg):
            if msg.topic == robot_base_topic + "/" + config.ROBOT_AFFECTIVE_STATE_TOPIC:
                # Message structure {valence: 0.0, arousal: 0.0, dominance: 0.0}
                self.robot_memory.set_robot_affective_state(msg.payload.decode())
                # print("############# Storing Robot Affective State in Robot Memory:", msg.payload.decode())

            elif msg.topic == robot_base_topic + "/" + config.USER_AFFECTIVE_STATE_TOPIC:
                # Message structure {valence: 0.0, arousal: 0.0, dominance: 0.0}
                self.robot_memory.set_user_affective_state((msg.payload.decode()))
                # print("############# Storing User Affective State in Robot Memory:", msg.payload.decode())

            elif msg.topic == robot_base_topic + "/" + config.ROBOT_BEHAVIOR_STATE_TOPIC:
                # Message structure:
                # {
                #     "affective_state": "happiness_l1",
                #     "facial_expression": "l1",
                #     "leds": "l1",
                #     "pose": "l1"
                # }
                self.robot_memory.set_robot_behavior_state(msg.payload.decode())
                # print("############# Storing Robot Behavior State in Robot Memory:", msg.payload.decode())

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
