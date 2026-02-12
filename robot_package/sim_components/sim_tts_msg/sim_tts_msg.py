from paho.mqtt import client as mqtt_client

import tkinter as tk
from tkinter import messagebox
from tkinter import *

import sys

import platform 

import sys
import os

# Adiciona o diretório pai ao path
# Caminho do diretório atual (onde está este script)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Sobe três níveis
parent_dir = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.append(parent_dir)
parent_dir = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.append(parent_dir)

import config  # Module with network device configurations.

import robot_profile

broker = config.MQTT_BROKER_ADRESS # Broker address.
port = config.MQTT_PORT # Broker Port.
response_topic = robot_profile.ROBOT_BASE_TOPIC
base_topic = config.SIMULATOR_BASE_TOPIC


# Cria a janela do módulo
janela = Tk()
janela.title("TTS Msg")
janela.geometry('193x65')
#fotofundo
back = Label(janela)
back.la = PhotoImage(file = 'robot_package/sim_components/sim_tts_msg/images/tts_msgbox.png')
back['image'] = back.la
back.place(x=0,y=0)


# MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # Reconnect then subscriptions will be renewed.
    client.subscribe(topic=[(base_topic + '/TALK', 1), ])
    print("SIM - TTS - MsgBox - Connected.")
            

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    text = msg.payload.decode().split("|")[2]

    
    messagebox.showinfo("The robot is speaking...", text)
    client.publish(response_topic + "/TALK_RESPONSE", "state|free", qos=2) # Libera o robô.





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

janela.mainloop()
