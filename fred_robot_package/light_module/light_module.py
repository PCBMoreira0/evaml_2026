from rich import print

import sys

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

    # É preciso tratar os casos em que o node vem sem o "color" definido
    if node.get('state') == "OFF":
        light_color = 'BLACK'
        message = light_color + "|" + 'OFF'
    else:
        if node.get('color') == None:
            light_color = 'WHITE'
        else:
            light_color = node.get('color')
            message = light_color + "|" + node.get("state")

    tab_colors = {"BLACK": "[b white on grey19] OFF [/]",
                  "BLUE": "[b white on blue ] ON [/]",
                  "GREEN": "[b white on green ] ON [/]",
                  "PINK": "[b white on magenta ] ON [/]",
                  "RED": "[b white on red ] ON [/]",
                  "YELLOW": "[b white on yellow ] ON [/]",
                  "WHITE": "[b reverse white] ON [/]"
                  }
    print("[b white]State: Setting [/]the [b white]Smart Bulb[/]. 💡 " + tab_colors[light_color])
    
    # Envia a mensagem MQTT para o módulo de controle da Smart Bulb.
    if memory.running_mode == "robot":
        color = message.split("|")[0]
        # After will be need to change EVA to topicbase
        client_mqtt.publish("EVA/light", color + "|" + node.get("state"), qos=2); # Command for the physical smart bulb
        
    
    elif memory.running_mode == "simulator":
        color = message.split("|")[0]
        if color == "BLACK": message = "off"
        if color == "PINK": message = "magenta"
        client_mqtt.publish("light", color.lower(), qos=2); # Command for the simulated robot.

    return node # It returns the same node