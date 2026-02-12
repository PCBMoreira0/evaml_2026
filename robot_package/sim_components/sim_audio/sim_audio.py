import threading
import time
from paho.mqtt import client as mqtt_client
import subprocess

from tkinter import *
# from  tkinter import ttk # Using tables

import sys
import os

# Adiciona o diretório pai ao path
# Caminho do diretório atual (onde está este script)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Sobe três níveis
parent_dir = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.append(parent_dir)


import platform

import config # Module with network device configurations.

broker = config.MQTT_BROKER_ADRESS # Broker address.
port = config.MQTT_PORT # Broker Port.
base_topic = config.SIMULATOR_BASE_TOPIC

x_pos = 90
y_pos = 80
event_anim_state = threading.Event() # used to start and stop threads

# Select the GUI definition file for the host operating system
if platform.system() == "Linux":
    print("Linux platform identified. Loading GUI formatting for Linux.")
    import gui_sim_audio_linux as gui_sim_audio # Definition of the graphical user interface (Linux)
    audio_ext = ".mp3" # Audio extension used by the audio library on Linux
    ibm_audio_ext = "audio/mp3" # Audio extension used to generate watson audios
elif platform.system() == "Windows":
    # This version of the Graphical User Interface (GUI) has been discontinued.
    print("Windows platform identified. Loading GUI formatting for Windows.")
    print("This version of the Graphical User Interface (GUI) has been discontinued. Sorry!")
    exit(1)
    # import gui_windows as EvaSIM_gui # definition of the graphical user interface (Windows) [This file is outdated and has been discontinued]
    # audio_ext = ".wav"
    # ibm_audio_ext = "audio/wav"
else:
    print("Sorry, the current OS is not supported by EvaSIM.") # Incompatible OS
    exit(1)


# Create the Tkinter window
window = Tk()

gui = gui_sim_audio.Gui(window) # Instance of the Gui class within the graphical user interface definition module


# Play a Sound or a Speech
def playsound(file_path, audio_file, type, block = True):
        if type == "audio":
            # client.publish(base_topic + "/log", "Playing the sound: " + audio_file)
            audio_format = ".wav" # config.AUDIO_EXTENSION
        elif type == "speech":
            audio_format = config.WATSON_AUDIO_EXTENSION
            # client.publish(base_topic + "/log", "EVA spoke the text and is free now.")
        
        if block == True:
            print('Playing audio in BLOCKING mode.')
            # Start the thread animation
            event_anim_state.set()
            # Criação de uma instância de Thread
            threading.Thread(target=anim, args=(event_anim_state,)).start()
            play = subprocess.Popen(['play', file_path + audio_file + audio_format], stdout=subprocess.PIPE)
            play.communicate()[0]
            # End of animation
            event_anim_state.clear()
            client.publish(base_topic + "/robot_response", "state|free", qos=2) # Libera o robô.
        else:
            print('Playing audio in NON-BLOCKING mode.')

            # Start the thread animation
            event_anim_state.set()
            # Criação de uma instância de Thread
            threading.Thread(target=anim, args=(event_anim_state,)).start()
            play = subprocess.Popen(['play', file_path + audio_file + audio_format], stdout=subprocess.PIPE)
            play.communicate()[0]
            # End of animation
            event_anim_state.clear()

        

# The speech is always of the type (Blocking).
# The playsound function is responsible for setting the robot's state to "FREE".
def speech(audio_file, block = True):
    file_path = "sim_tts_piper/tts_cache_files/"
    # Start the thread animation
    event_anim_state.set()
    # Criação de uma instância de Thread
    threading.Thread(target=anim, args=(event_anim_state,)).start()
    playsound(file_path, audio_file, "speech", block)
    event_anim_state.clear()


# MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # Reconnect then subscriptions will be renewed.
    client.subscribe(topic=[(base_topic + '/AUDIO', 1), ])
    client.subscribe(topic=[(base_topic + '/SPEECH', 1), ])
    print("Audio Module - Connected.")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if msg.topic == base_topic + '/AUDIO':
        file_name = msg.payload.decode().split("|")[0]
        block = msg.payload.decode().split("|")[1]
        if block == "TRUE":
            # Start the thread animation
            event_anim_state.set()
            # Criação de uma instância de Thread
            threading.Thread(target=anim, args=(event_anim_state,)).start()
            playsound("robot_package/sim_components/sim_audio/audio_files/", file_name, "audio", True)
            # client.publish(base_topic + "/robot_response", "state|free", qos=2) # Libera o robô.
            # Draw the sound speaker
            event_anim_state.clear()
        else:
            playsound("robot_package/sim_components/sim_audio/audio_files/", file_name, "audio", False) 

    if msg.topic == base_topic + '/SPEECH':
        file_name = msg.payload.decode()
        speech(file_name, True) # Speech always runs in "Blocking" mode.


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


def anim(event):
    while(gui.estado == "running"): # it runs if the gui still running
        if event.is_set():
            gui.canvas.create_image(x_pos, y_pos, image = gui.alto_falante2)
            time.sleep(0.2)
            gui.canvas.create_image(x_pos, y_pos, image = gui.alto_falante3)
            time.sleep(0.2)
            gui.canvas.create_image(x_pos, y_pos, image = gui.alto_falante1)
            time.sleep(0.2)
        else:
            return


# Draw sound speaker
gui.canvas.create_image(x_pos, y_pos, image = gui.alto_falante1)

gui.mainloop()
