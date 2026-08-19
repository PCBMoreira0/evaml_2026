from rich import print

import sys

sys.path.insert(0, "../")

import robot_package.robot_profile as robot_profile  # Module with network device configurations.

import config

def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """
    if memory.running_mode == "simulator":
        topic_base = config.SIMULATOR_TOPIC_BASE
    elif memory.running_mode == "robot":
        topic_base = robot_profile.ROBOT_TOPIC_BASE
    else:
        topic_base = config.TERMINAL_TOPIC_BASE

    if node.get("emotion") == "NEUTRAL":
        emoji = " 😐"
    elif node.get("emotion") == "GREETINGS":
        emoji = " 👋👋"
    elif node.get("emotion") == "BROKEN":
        emoji = " 😵"
    elif node.get("emotion") == "PLEASED":
        emoji = " 🙂"
    elif node.get("emotion") == "ANGRY":
        emoji = " 😡"
    elif node.get("emotion") == "ANGRY2":
        emoji = " 😡😡"
    elif node.get("emotion") == "DISGUST":
        emoji = " 😖"
    elif node.get("emotion") == "AFRAID":
        emoji = " 😧"
    elif node.get("emotion") == "HAPPY":
        emoji = " 😄"
    elif node.get("emotion") == "IN_LOVE":
        emoji = " 🥰"
    elif node.get("emotion") == "SAD":
        emoji = " 😔"
    elif node.get("emotion") == "SURPRISED":
        emoji = " 😲"
    elif node.get("emotion") == "SPEECH_ON_1":
        emoji = " 💬 ⭕"
    elif node.get("emotion") == "SPEECH_OFF_1":
        emoji = " 🔇"
    elif node.get("emotion") == "SPEECH_ON_2":
        emoji = " 💬💬"
    elif node.get("emotion") == "SPEECH_OFF_2":
        emoji = " 🔇🔇"

    print("[b white]State:[/] Setting the robot [b white]expression[/] to [b white]" + node.get("emotion") + emoji + "[/].")

    if memory.running_mode == "robot":
        message = node.get("emotion")
        topic = "expression" # Para o FRED o tópico não é "emotion".
        client_mqtt.publish(topic_base + '/' + topic, message.lower())
    elif memory.running_mode == "simulator":
        message = node.get("emotion")
        if message == "SPEECH_ON_1": 
            message = "3"
            topic = "camera"
        elif message == "SPEECH_OFF_1": 
            message = "1"
            topic = "camera"
        elif message == "SPEECH_ON_2": 
            message = "2"
            topic = "camera"
        elif message == "SPEECH_OFF_2": 
            message = "4"
            topic = "camera"
        else:
            topic = "display" # Para o FRED simulado o tópico não é "emotion" e nem "expression".
        
        client_mqtt.publish(topic, message.lower(), qos=2)

        # greetings, angry, happy, sad, neutral, pleased, afraid e surprised


    return node # It returns the same node

