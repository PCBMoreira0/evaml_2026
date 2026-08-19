import wave
from piper import PiperVoice

import time

from paho.mqtt import client as mqtt_client

import tkinter as tk
from tkinter import messagebox
from tkinter import *

import hashlib

import sys
import os

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
# Adiciona o diretório pai ao path
# Caminho do diretório atual (onde está este script)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Sobe três níveis
parent_dir = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.append(parent_dir)
parent_dir = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.append(parent_dir)

import config  # Module with network device configurations.

import robot_package.robot_profile as robot_profile


broker = config.MQTT_BROKER_ADRESS # Broker address.
port = config.MQTT_PORT # Broker Port.
topic_base = robot_profile.SIMULATOR_BASE_TOPIC
sim_base_topic = robot_profile.SIMULATOR_BASE_TOPIC
robot_base_topic = robot_profile.ROBOT_BASE_TOPIC
voice_type = config.VOICE_TYPE

# piper_voice = PiperVoice.load(BASE_DIR / "pt_BR-faber-medium.onnx")
# piper_voice = PiperVoice.load(BASE_DIR / "en_US-bryce-medium.onnx") 
piper_voice = PiperVoice.load(BASE_DIR / "en_US-ryan-high.onnx")




# Cria a janela do módulo
janela = Tk()
janela.title("Piper - TTS")
janela.geometry('193x70')
#fotofundo
back = Label(janela)
back.la = PhotoImage(file = BASE_DIR / 'images/tts_piper.png')
back['image'] = back.la
back.place(x=0,y=0)



# def piper_com_modelo(modelo, texto, arquivo="temporary.mp3"):
#     cmd = ["piper", "--model",
#     modelo, "--output_file", arquivo]
#     process = subprocess.Popen(cmd, cwd="sim_tts_piper/", stdin=subprocess.PIPE, text=True)
#     process.communicate(input=texto)


# MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # Reconnect then subscriptions will be renewed.
    client.subscribe(topic=[(sim_base_topic + '/TALK', 1), ]) # Subscribe to Simulator
    client.subscribe(topic=[(robot_base_topic + '/TALK', 1), ]) # Subscribe to Robot
    print("SIM - TTS - Piper - Connected.")
            

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global voice_tone, auth_start_time, apikey, url, authenticator, tts, first_requisition
    if (msg.topic == sim_base_topic + '/TALK') or (msg.topic == robot_base_topic + '/TALK'):
        print("Using PIPER TTS to convert text to audio...")
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
        

        audio_file_is_ok = False
        while(not audio_file_is_ok):
            # Checks if the speech audio already exists in the cache folder.
            file_to_seacrh = (BASE_DIR / ".." / "sim_audio" / "tts_cache_files" / (file_name + config.PIPER_AUDIO_EXTENSION)).resolve()
            if not (os.path.isfile(file_to_seacrh)): # If it doesn't exist, call Watson.
                print("The file is not cached... Let's try to generate it!")

                # Start the TTS process
                tts_start = time.time() # Variable used to mark the processing time of the TTS service.
                while(not audio_file_is_ok):
                    # Functions of the TTS service for EVA
                    file_to_play = (BASE_DIR / ".." / "sim_audio" / "tts_cache_files" / (file_name + config.PIPER_AUDIO_EXTENSION)).resolve()
                    
                    with wave.open(str(file_to_play), "wb") as wav_file:
                        piper_voice.synthesize_wav(msg.payload.decode(), wav_file)
                        print(f"Arquivo salvo: ", file_to_play)
                    tts_ending = time.time()

                    client.publish(topic_base + "/log", "The audio was generated correctly in (s): %.2f" % (tts_ending - tts_start))
                    print("The file will be played!")
           
                    client.publish(topic_base + "/log", "The Robot is busy trying to speak the text: " + msg.payload.decode())
                    client.publish(topic_base + "/SPEECH", file_name)
                    audio_file_is_ok = True
                    
            else:
                print("The file is cached!")
                file_to_play = (BASE_DIR / ".." / "sim_audio" / "tts_cache_files" / (file_name + config.PIPER_AUDIO_EXTENSION)).resolve()
                if (os.path.getsize(file_to_play)) == 0: # Corrupted file
                    print("The generated audio file is 0 bytes, corrupt and will be removed!")
                    os.remove("../sim_audio/tts_cache_files/" + file_name + config.PIPER_AUDIO_EXTENSION)
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

janela.mainloop()
