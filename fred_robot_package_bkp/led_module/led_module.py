from paho.mqtt import client as mqtt_client

import sys

from rich import print

sys.path.insert(0, "../")

import robot_profile  # Module with network device configurations.

import config


def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """
    if memory.running_mode == "simulator":
        topic_base = config.SIMULATOR_TOPIC_BASE
    elif memory.running_mode == "robot":
        topic_base = robot_profile.ROBOT_TOPIC_BASE
    else:
        topic_base = config.TERMINAL_TOPIC_BASE

    print("[b white]State: Setting [/]the robot [b white]LEDs[/] to the animation/color [bold]" + node.get("animation") + "![/].")

    tab_convertion = { # Tabela de conversão de emoções para as cores.
        "HAPPY"     : "GREEN",
        "SAD"       : "BLUE",
        "ANGRY"     : "RED",
        "SURPRISE"  : "YELLOW",
        "SPEAK"     : "BLUE",
        "LISTEN"    : "GREEN",
        "STOP"      : "BLACK",
        "RAINBOW"   : "RAINBOW",
        "PINK"      : "PINK"
    }

    message = node.get("animation")
    
    if message in tab_convertion:
        message = tab_convertion[message]

    
    if memory.running_mode == "robot":
        # As cores, no mqtt do esp8266, estão definidas em letras minúsculas.
        topic = "leds" # Esse é o nome do tópico para o FRED
        # Os valores para as cores no FRED são em letras minúsculas.
        client_mqtt.publish(topic_base + '/' + topic, message.lower())

    elif memory.running_mode == "simulator":
        # Utilizando o robot no unity
        topic = "leds" # Esse é o nome do tópico para o FRED e para o EVA.
        # Os valores para as cores no FRED são em letras minúsculas.
        client_mqtt.publish(topic, message.lower())

    return node # It returns the same node
