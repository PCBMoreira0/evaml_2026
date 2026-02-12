import subprocess
import librosa
import soundfile as sf
import numpy as np
import io
from pydub import AudioSegment


from paho.mqtt import client as mqtt_client

import tkinter as tk
from tkinter import messagebox
from tkinter import *

import hashlib

import sys

import platform 

import sys
import os

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import robot_profile  # Module with network device configurations.

import config  # Module with network device configurations.

broker = config.MQTT_BROKER_ADRESS # Broker address.
port = config.MQTT_PORT # Broker Port.
topic_base = robot_profile.ROBOT_TOPIC_BASE



# Cria a janela do módulo
janela = Tk()
janela.title("FRED - Piper (TTS)")
janela.geometry('193x70')
#fotofundo
back = Label(janela)
back.la = PhotoImage(file = 'fred_tts_piper/images/tts_piper.png')
back['image'] = back.la
back.place(x=0,y=0)


def piper_com_modelo(modelo, texto, arquivo="temporary.mp3"):
    cmd = ["piper", "--model",
    modelo, "--output_file", arquivo]
    process = subprocess.Popen(cmd, cwd="fred_tts_piper/", stdin=subprocess.PIPE, text=True)
    process.communicate(input=texto)


# MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # Reconnect then subscriptions will be renewed.
    client.subscribe(topic=[(topic_base + '/talk', 1), ])
    print("FRED - TTS - Piper - Connected.")
            

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    voice_type = msg.payload.decode().split("|")[0] # Voice type is the model used
    pitch_shift = msg.payload.decode().split("|")[1]
    text = msg.payload.decode().split("|")[2]

    hash_object = hashlib.md5(text.encode())
    file_path = "fred_tts_piper/tts_cache_files/"
    file_name = "_audio_"  + voice_type + "_" + pitch_shift + "_" + hash_object.hexdigest() 

    if not (os.path.isfile(file_path + file_name + config.WATSON_AUDIO_EXTENSION)): # If it doesn't exist, call Piper.
    
        piper_com_modelo(voice_type, text, "temporary.mp3")

        audio =  AudioSegment.from_file("fred_tts_piper/temporary.mp3")
                            
        if audio.channels > 1:
            audio = audio.set_channels(1)
        
        y = np.array(audio.get_array_of_samples(), dtype=np.float32) / (2**15)
        sr = audio.frame_rate

        steps = float(pitch_shift)
        if steps != 0:
            y_pitched = librosa.effects.pitch_shift(y, sr=sr, n_steps=steps) # Executa o pirch de 3 semitons acima.
        else: # Sem processamento (Sem pitch)
            y_pitched = y

        sf.write("fred_tts_piper/tts_cache_files/" + file_name + config.WATSON_AUDIO_EXTENSION, y_pitched, sr)  # WAV é melhor que MP3

    client.publish(topic_base + "/expression", "speech_on_1", qos=2)
    client.publish(topic_base + "/speech", file_name)



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
