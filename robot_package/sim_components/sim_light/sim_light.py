from paho.mqtt import client as mqtt_client

import socket
import time
from tkinter import *

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

import platform 

import config  # Module with network device configurations.

import robot_profile


broker = config.MQTT_BROKER_ADRESS # Broker address.
port = config.MQTT_PORT # Broker Port.
sim_base_topic = robot_profile.SIMULATOR_BASE_TOPIC
robot_base_topic = robot_profile.ROBOT_BASE_TOPIC

# Position for graphical elements
smart_bulb_x_pos = 95
smart_bulb_y_pos = 90
smart_bulb_x_light = 56
smart_bulb_y_light = 10

COLOR_TABLE = {
    "RED"   : "FF0000",
    "GREEN" : "00FF00",
    "BLUE"  : "0000FF",
    "YELLOW": "FFFF00",
    "PINK"  : "FF00FF",
    "WHITE" : "FFFFFF",
    "BLACK" : "000000"
}


# MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # Reconnect then subscriptions will be renewed.
    client.subscribe(topic=[(sim_base_topic + '/LIGHT', 1), ]) # Simulator topic
    client.subscribe(topic=[(robot_base_topic + '/LIGHT', 1), ]) # Robot topic
    print("SIM - Smart Bulb Module - Connected.")
            

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # Processing in the simulation mode
    if msg.topic == sim_base_topic + '/LIGHT':
    # client.publish(base_topic + '/log', 'Controlling the Smart Bulb (color|state): ' + msg.payload.decode())
        
        color, state, ip, port = msg.payload.decode().split("|") # Msg format COLOR|STATE|IP_ADRESS|IP_PORT
        
        if color == "": color = "000000"

        color_map = {"WHITE":"#ffffff", "BLACK":"#000000", "RED":"#ff0000", "PINK":"#e6007e", "GREEN":"#00ff00", "YELLOW":"#ffff00", "BLUE":"#0000ff"}
        if color_map.get(color) != None:
            color = color_map.get(color)
        if state == "ON":
            gui.canvas.create_oval(smart_bulb_x_light, smart_bulb_y_light, smart_bulb_x_light + 75, smart_bulb_y_light + 85, fill = color, outline = color )
            gui.canvas.create_image(smart_bulb_x_pos, smart_bulb_y_pos, image = gui.bulb_image) # redesenha a lampada
        else:
            gui.canvas.create_oval(smart_bulb_x_light, smart_bulb_y_light, smart_bulb_x_light + 75, smart_bulb_y_light + 85, fill = "#000000", outline = "#000000" ) # cor preta indica light off
            gui.canvas.create_image(smart_bulb_x_pos, smart_bulb_y_pos, image = gui.bulb_image) # redesenha a lampada
    # Processing in the robot mode
    elif msg.topic == robot_base_topic + '/LIGHT':
        bulb_color = ""
        color, state, ip, port = msg.payload.decode().split("|")
        # client.publish(topic_base + '/syslog', 'Controlling the Smart Bulb (color|state): ' + msg.payload.decode())
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((ip, int(port)))
                print("TCP connection with the Smart Bulb established.")
                # color = msg.payload.decode().split("|")[0]
                if color == "": color = "000000"
                # state = msg.payload.decode().split("|")[1]

                if color in COLOR_TABLE:
                    bulb_color = str(int(COLOR_TABLE[color], 16))
                else:
                    bulb_color = str(int(color, 16))
                    
                if state == "OFF":
                    # off command
                    s.sendall('{"id":1, "method":"set_power","params":["off", "smooth", 0]}\r\n'.encode())
                elif state == "ON":
                    # on command
                    s.sendall('{"id":1, "method":"set_power","params":["on", "smooth", 0]}\r\n'.encode())
                    time.sleep(0.1) # parece precisar de um tempo para enviar os dois comandos seguidos
                    s.sendall(('{"id":1,"method":"set_rgb","params":[' + bulb_color + ', "smooth", 0]}\r\n').encode())

            except socket.error:
                print ("Unable to connect to Smart Bulb. \nTurn on the device and configure its IP address correctly.")
            
            # In the same time control the simulated Smart Bulb 
            color = msg.payload.decode().split("|")[0]
            if color == "": color = "000000"
            state = msg.payload.decode().split("|")[1]

            color_map = {"WHITE":"#ffffff", "BLACK":"#000000", "RED":"#ff0000", "PINK":"#e6007e", "GREEN":"#00ff00", "YELLOW":"#ffff00", "BLUE":"#0000ff"}
            if color_map.get(color) != None:
                color = color_map.get(color)
            if state == "ON":
                gui.canvas.create_oval(smart_bulb_x_light, smart_bulb_y_light, smart_bulb_x_light + 75, smart_bulb_y_light + 85, fill = color, outline = color )
                gui.canvas.create_image(smart_bulb_x_pos, smart_bulb_y_pos, image = gui.bulb_image) # redesenha a lampada
            else:
                gui.canvas.create_oval(smart_bulb_x_light, smart_bulb_y_light, smart_bulb_x_light + 75, smart_bulb_y_light + 85, fill = "#000000", outline = "#000000" ) # cor preta indica light off
                gui.canvas.create_image(smart_bulb_x_pos, smart_bulb_y_pos, image = gui.bulb_image) # redesenha a lampada

# Select the GUI definition file for the host operating system
if platform.system() == "Linux":
    print("Linux platform identified. Loading GUI formatting for Linux.")
    import gui_sim_light_linux as gui_sim_light # Definition of the graphical user interface (Linux)
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

gui = gui_sim_light.Gui(window) # Instance of the Gui class within the graphical user interface definition module

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

# Draw the smart bulb
gui.canvas.create_oval(smart_bulb_x_light, smart_bulb_y_light, smart_bulb_x_light + 75, smart_bulb_y_light + 85, fill = "#000000", outline = "#000000" ) # black color mean light off
gui.canvas.create_image(smart_bulb_x_pos, smart_bulb_y_pos, image = gui.bulb_image)

gui.mainloop()
