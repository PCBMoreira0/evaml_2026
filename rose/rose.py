from paho.mqtt import client as mqtt_client

import numpy as np

import time

import sys
import os

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
parent_dir = os.path.abspath(os.path.join(BASE_DIR, "../"))
sys.path.append(parent_dir)


import config  # Module with network device configurations.

sys.path.append(os.getcwd() + "/" + "robot_package/")

import robot_profile


broker = config.MQTT_BROKER_ADRESS # Broker address.
port = config.MQTT_PORT # Broker Port.
sim_base_topic = robot_profile.SIMULATOR_BASE_TOPIC
robot_base_topic = robot_profile.ROBOT_BASE_TOPIC


# Initializing
profile = ""
user_affective_state = np.array([0.0, 0.0, 0.0])
robot_affective_state = np.array([0.0, 0.0, 0.0])
empathy = 0.0
decay = 0.0
base_mood = np.array([0.0, 0.0, 0.0])
robot_affective_target_state = user_affective_state


# MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # Reconnect then subscriptions will be renewed.
    client.subscribe(topic=[(sim_base_topic + '/USER_EMOTION', 1), ]) # Simulator topic
    client.subscribe(topic=[(robot_base_topic + '/USER_EMOTION', 1), ]) # Robot topic
    client.subscribe(topic=[(sim_base_topic + '/ROBOT_PERSONALITY', 1), ]) # Simulator topic
    client.subscribe(topic=[(robot_base_topic + '/ROBOT_PERSONALITY', 1), ]) # Robot topic
    print("ROSE - Robot Sentiment Engine - Connected.")
            

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global robot_affective_target_state, empathy, decay, user_affective_state, base_mood, factor
    # Processing in the simulation mode
    global profile, sensitivity, decay, base_mood, user_affective_state

    if msg.topic == sim_base_topic + '/USER_EMOTION':
        print("User emotion msg")
        user_affective_state = np.fromstring(msg.payload.decode(), dtype=float, sep=',')
        # robot_affective_target_state = user_affective_state
        # robot_affective_target_state = user_affective_state * empathy # A emoção do robo
        user_affective_state = user_affective_state * empathy + robot_affective_state * (1 - empathy)
        robot_affective_target_state = user_affective_state
        print(user_affective_state)

    elif msg.topic == robot_base_topic + '/USER_EMOTION':
        print("User emotion msg")
        user_affective_state = np.fromstring(msg.payload.decode(), dtype=float, sep=',')
        # robot_affective_target_state = user_affective_state
        # robot_affective_target_state = user_affective_state * empathy # A emoção do robo
        user_affective_state = user_affective_state * empathy + robot_affective_state * (1 - empathy)
        robot_affective_target_state = user_affective_state
        print(user_affective_state)

    if (msg.topic == sim_base_topic + '/ROBOT_PERSONALITY') or (msg.topic == robot_base_topic + '/ROBOT_PERSONALITY'):
        profile = msg.payload.decode().split("|")[0]
        print(profile)
        empathy = float(msg.payload.decode().split("|")[1])
        print(empathy)
        decay = float(msg.payload.decode().split("|")[2])
        print(decay)
        base_mood = np.fromstring(msg.payload.decode().split("|")[3], dtype=float, sep=',')
        print(base_mood)
        robot_affective_target_state = base_mood


def robot_affective_state_update():
    global robot_affective_state, robot_affective_target_state, factor
    while (1):
        if np.allclose(robot_affective_state, robot_affective_target_state) == True:
            if np.allclose(robot_affective_target_state, user_affective_state) == True:
                robot_affective_target_state = base_mood
                print("No user target, voltando para a base")
                # time.sleep(2)
            else:
                time.sleep(0.01)
        else:
            if np.allclose(robot_affective_target_state, user_affective_state) == True:
                robot_affective_state = user_affective_state * 0.2 + (1 - 0.2) * robot_affective_state
                client.publish("SIMULATOR/ROBOT_EMOTION", str(robot_affective_state).encode())
                time.sleep(0.1)
                
            else:
                print("indo para a base")
                robot_affective_state = base_mood * decay + (1 - decay) * robot_affective_state
                print(robot_affective_state, decay)
                client.publish("SIMULATOR/ROBOT_EMOTION", str(robot_affective_state).encode())
                time.sleep(0.5)
            
        

    # while 1:
    #     if np.allclose(robot_affective_state, robot_affective_target_state) == False:
    #         robot_affective_state = robot_affective_target_state * factor + robot_affective_state * (1 - factor)
    #         client.publish("SIMULATOR/ROBOT_EMOTION", str(robot_affective_state).encode())
    #         print("Updated:", robot_affective_state, "Factor:", factor)
    #         time.sleep(0.1)
    #     if np.allclose(robot_affective_state, robot_affective_target_state) == True:
    #         robot_affective_target_state = base_mood
    #         factor = decay / 2 # Divide por 10 para suavizar
    #         #print("aqui", robot_affective_state, robot_affective_target_state)

        


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
# client.loop_forever()

client.loop_start()
while(1):
    robot_affective_state_update()
