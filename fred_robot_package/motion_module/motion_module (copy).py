import sys

from rich import print

sys.path.insert(0, "../")

import config  # Module with network device configurations.


topic_base = config.ROBOT_TOPIC_BASE



def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """
    if node.get("leftArm") != None: # Move the left arm
        print("[b white]State:[/] [b white]Moving[/] the [b white]LEFT ARM[/]. [b white]Type: [/][reverse b white on black] " + node.attrib["leftArm"] + " [/].")
    if node.get("rightArm") != None: # Move the right arm
        print("[b white]State:[/] [b white]Moving[/] the [b white]RIGHT ARM[/]. [b white]Type: [/][reverse b white on black] " + node.attrib["rightArm"] + " [/].")
    if node.get("head") != None: # Move head with the new format (<head> element)
        print("[b white]State:[/] [b white]Moving[/] the [b white]HEAD[/]. [b white]Type: [/][reverse b white on black] " + node.attrib["head"] + " [/].")
    else: # Check if the old version was used
        if node.get("type") != None: # Maintaining compatibility with the old version of the motion element
            print("[b white]State:[/] [b white]Moving[/] the [b white]HEAD[/]. [b white]Type: [/][reverse b white on black] " + node.attrib["type"] + " [/].")


    # client_mqtt.publish(topic_base + '/' + node.tag, message)

    return node # It returns the same node
