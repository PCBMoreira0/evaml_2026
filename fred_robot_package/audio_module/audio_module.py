
from play_audio import playsound # Adapter module for the audio library.
# Depending on the OS it matters and defines a function called "playsound".
 
from rich import print

import sys

import os

import time

import config

sys.path.insert(0, "../")

import robot_profile  # Module with network device configurations.



# Função de bloqueio que é usada para sincronia entre os módulos e o Script Player
def block(state, memory):
    memory.robot_state = state # Altera o estado do robô.
    while memory.robot_state != "free": # Aguarda que o robô fique livre para seguir para o próximo comando.
        time.sleep(0.01)


def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """
    if memory.running_mode == "simulator":
        topic_base = config.SIMULATOR_TOPIC_BASE
    elif memory.running_mode == "robot":
        topic_base = robot_profile.ROBOT_TOPIC_BASE
    else:
        topic_base = config.TERMINAL_TOPIC_BASE

    if node.get("block") == "TRUE":
        print('[b white]State:[/][b white] Playing[/] ▶️  the sound [bold][b white]"' + node.get("source") + '"[/] in [b white]BLOCKING[/] mode.')
        if topic_base != "TERMINAL":
            message = node.get("source") + "|" + node.get("block")
            client_mqtt.publish(topic_base + '/' + node.tag, message)
            block("Playing a sound", memory)
        else:
            try:
                playsound(os.getcwd() + "/" + config.ROBOT_PACKAGE_FOLDER + "/audio_module/audio_files/" + node.get("source") + ".wav", block = True)
            except FileNotFoundError as e:
                print('[b white on red blink] FATAL ERROR [/]: [b yellow reverse] There was a problem playing the audio file [/]: [b white]"' + node.get("source") + '"[/]. Check if it [b white u]exists[/] or is in the [b white u]correct format[/] (wav).✋⛔️')
                exit(1) 
    else:
        print('[b white]State:[/][b white] Playing[/] ▶️  the sound [bold][b white]"' + node.get("source") + '"[/] in [b white]NON-BLOCKING[/] mode.')
        if topic_base != "TERMINAL":
            message = node.get("source") + "|" + node.get("block")
            client_mqtt.publish(topic_base + '/' + node.tag, message)
        else:
            try:
                playsound(os.getcwd() + "/" + config.ROBOT_PACKAGE_FOLDER + "/audio_module/audio_files/" + node.get("source") + ".wav", block = False)
            except FileNotFoundError as e:
                print('[b white on red blink] FATAL ERROR [/]: [b yellow reverse] There was a problem playing the audio file [/]: [b white]"' + node.get("source") + '"[/]. Check if it [b u white]exists[/] or is in the [b u white]correct format[/] (wav)[/].✋⛔️')
                exit(1) 
    
    return node # It returns the same node