from kokoro import KPipeline
import soundfile as sf
import numpy as np


import threading
import time


from paho.mqtt import client as mqtt_client

from tkinter import *
from  tkinter import ttk # Using tables

import hashlib
import os


import sys
import os

import platform 

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
parent_dir = os.path.abspath(os.path.join(BASE_DIR, "../../.."))
sys.path.append(parent_dir)
parent_dir = os.path.abspath(os.path.join(BASE_DIR, "../.."))
sys.path.append(parent_dir)
parent_dir = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.append(parent_dir)


import config # Module with network device configurations.

import robot_profile

broker = config.MQTT_BROKER_ADRESS # Broker address.
port = config.MQTT_PORT # Broker Port.
topic_base = robot_profile.SIMULATOR_BASE_TOPIC
sim_base_topic = robot_profile.SIMULATOR_BASE_TOPIC
robot_base_topic = robot_profile.ROBOT_BASE_TOPIC
voice_type = config.VOICE_TYPE


# Kokoro configuration

# 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
# 🇪🇸 'e' => Spanish es
# 🇫🇷 'f' => French fr-fr
# 🇮🇳 'h' => Hindi hi
# 🇮🇹 'i' => Italian it
# 🇯🇵 'j' => Japanese: pip install misaki[ja]
# 🇧🇷 'p' => Brazilian Portuguese pt-br
# 🇨🇳 'z' => Mandarin Chinese: pip install misaki[zh]
lang_code = 'p'
pipeline = KPipeline(lang_code=lang_code)
talk_speed = 0.8

# Você pode conferir outras vozes aqui: 
# http://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md


x_pos = 95
y_pos = 30
event_anim_state = threading.Event() # used to start and stop threads

# Select the GUI definition file for the host operating system
if platform.system() == "Linux":
    print("Linux platform identified. Loading GUI formatting for Linux.")
    import gui_sim_tts_kokoro_linux as gui_sim_tts_kokoro # Definition of the graphical user interface (Linux)
    audio_ext = ".mp3" # Audio extension used by the audio library on Linux
    # ibm_audio_ext = "audio/mp3" # Audio extension used to generate watson audios
elif platform.system() == "Windows":
    # This version of the Graphical User Interface (GUI) has been discontinued.
    print("Windows platform identified. Loading GUI formatting for Windows.")
    print("This version of the Graphical User Interface (GUI) has been discontinued. Sorry!")
    exit(1)

else:
    print("Sorry, the current OS is not supported by EvaSIM.") # Incompatible OS
    exit(1)


# Create the Tkinter window
window = Tk()
gui = gui_sim_tts_kokoro.Gui(window) # Instance of the Gui class within the graphical user interface definition module   



# MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # Reconnect then subscriptions will be renewed.
    client.subscribe(topic=[(sim_base_topic + '/TALK', 1), ]) # Subscribe to Simulator
    client.subscribe(topic=[(robot_base_topic + '/TALK', 1), ]) # Subscribe to Robot
    print("SIM - Text-To-Speech Module - Connected.")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global voice_tone, auth_start_time, apikey, url, authenticator, tts, first_requisition
    if (msg.topic == sim_base_topic + '/TALK') or (msg.topic == robot_base_topic + '/TALK'):
        print("Using Kokoro TTS to convert text to audio...")
        # Assumes the default UTF-8 (Generates the hashing of the audio file).
        # Additionally, use the voice timbre attribute in the file hash.
        if len(msg.payload.decode().split("|")) == 2:
            voice_tone = msg.payload.decode().split("|")[0]
            msg.payload = (msg.payload.decode()).split("|")[1]
            msg.payload = msg.payload.encode()
        else:
            print("Ooops... No voice tone defined...")
            exit(1)

        print("Voice:", voice_tone, "Message:", msg.payload.decode())
        hash_object = hashlib.md5(msg.payload)
        file_name = "_audio_"  + voice_tone + hash_object.hexdigest()
        
        voice = 'pm_santa'
        # Portugueses voices
        # pm_alex
        # pm_santa
        # pf_dora

        audio_file_is_ok = False
        while(not audio_file_is_ok):
            # Checks if the speech audio already exists in the cache folder.
            file_to_seacrh = (BASE_DIR / ".." / "sim_audio" / "tts_cache_files" / (file_name + config.WATSON_AUDIO_EXTENSION)).resolve()
            if not (os.path.isfile(file_to_seacrh)): # If it doesn't exist, call Watson.
                print("The file is not cached... Let's try to generate it!")
                event_anim_state.set()
                # Criação de uma instância de Thread
                threading.Thread(target=anim, args=(event_anim_state,)).start()
                
                # Start the TTS process
                tts_start = time.time() # Variable used to mark the processing time of the TTS service.
                while(not audio_file_is_ok):
                    # Functions of the TTS service for EVA
                    file_to_play = (BASE_DIR / ".." / "sim_audio" / "tts_cache_files" / (file_name + config.WATSON_AUDIO_EXTENSION)).resolve()
                    
                    generator = pipeline(msg.payload.decode(), voice=voice_tone, speed=talk_speed)
                    audio_chunks = []
                    for i, (gs, ps, audio) in enumerate(generator):
                        print(i, gs, ps)
                        audio_chunks.append(audio)
                    print("Fim...")

                    if audio_chunks:
                        audio_completo = np.concatenate(audio_chunks)
                        sf.write(file_to_play, audio_completo, 24000)
                        print(f"Arquivo salvo: ", file_to_play)

                    tts_ending = time.time()
                    client.publish(topic_base + "/log", "The audio was generated correctly in (s): %.2f" % (tts_ending - tts_start))
                    print("The file will be played!")
                    event_anim_state.clear()
                    client.publish(topic_base + "/log", "EVA is busy trying to speak the text: " + msg.payload.decode())
                    client.publish(topic_base + "/SPEECH", file_name)
                    audio_file_is_ok = True
                    
            else:
                print("The file is cached!")
                file_to_play = (BASE_DIR / ".." / "sim_audio" / "tts_cache_files" / (file_name + config.WATSON_AUDIO_EXTENSION)).resolve()
                if (os.path.getsize(file_to_play)) == 0: # Corrupted file
                    print("The generated audio file is 0 bytes, corrupt and will be removed!")
                    os.remove("../sim_audio/tts_cache_files/" + file_name + config.WATSON_AUDIO_EXTENSION)
                else:
                    print("The file is more than 0 bytes and will be played now!")
                    client.publish(topic_base + "/log", "The audio was found in the cache.")
                    client.publish(topic_base + "/log", "EVA is busy trying to speak the text: " + msg.payload.decode())
                    client.publish(topic_base + "/SPEECH", file_name)
                    audio_file_is_ok = True  





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
    while(gui.estado == "running"):
        if event_anim_state.is_set():
            gui.canvas.create_image(x_pos, y_pos, image = gui.tts_kokoro_1)
            time.sleep(0.4)
            gui.canvas.create_image(x_pos, y_pos, image = gui.tts_kokoro_2)
            time.sleep(0.4)
            gui.canvas.create_image(x_pos, y_pos, image = gui.tts_kokoro_0)
        else:
            return


# Draw the sound speaker
gui.canvas.create_image(x_pos, y_pos, image = gui.tts_kokoro_0)

gui.mainloop()
