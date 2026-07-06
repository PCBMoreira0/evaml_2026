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

    print("[b white]State:[/] [b white]Moving[/] the [b white]Robot[/]. [b white]Type: [/][reverse b white on black] " + node.attrib["type"] + " [/].")
    
    # Controla o robô físico.
    if memory.running_mode == "robot":  
        topic = "move" # O tópico para movimentos no FRED é move e não motion.
        message = node.get("type")
        client_mqtt.publish(topic_base + '/' + topic, message.lower())

    elif memory.running_mode == "simulator":
        topic = "move" # O tópico para movimentos no FRED é move e não motion.
        message = node.get("type")
        if message == "DANCE1": message = "dance1_cycle"
        elif message == "DANCE2": message = "dance2_cycle"
        elif message == "RIGHT_MOON": message = "moonwalk_right_cycle"
        elif message == "LEFT_MOON": message = "moonwalk_left_cycle"
        elif message == "STOMPING_FOOT_L": message = "stomping_foot"
        elif message == "STOMPING_FOOT_R": message = "stomping_foot"
        client_mqtt.publish(topic, message.lower())

    return node # It returns the same node
