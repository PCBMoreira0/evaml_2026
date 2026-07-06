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

    print("[b white]State:[/] Putting the robot in the [b white]pose[/]: [b white reverse] " + node.get("type") + " [/].")

    message = node.get("type")

    # Executa no robô.
    if memory.running_mode == "robot":
        # As mensagens, no mqtt do esp8266, estão definidas em letras minúsculas.
        client_mqtt.publish(topic_base + '/' + node.tag, message.lower())

    elif memory.running_mode == "simulator":
        if message == "LEFT_FOOT1": message = "left_foot"
        elif message == "LEFT_FOOT2": message = "left_foot_neutral"

        elif message == "RIGHT_FOOT1": message = "right_foot"
        elif message == "RIGHT_FOOT2": message = "right_foot_neutral"

        elif message == "SAD_FOOT_FAST": message = "sad_foot"
        elif message == "SAD_FOOT_SLOW": message = "sad_foot_neutral"

        elif message == "TIPTOE_FOOT": message = "tiptoe_foot"
        elif message == "NEUTRAL": message = "tiptoe_foot_neutral"

    client_mqtt.publish("move", message.lower())
    
    return node # It returns the same node

