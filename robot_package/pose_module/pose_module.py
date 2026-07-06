import sys

from rich import print

import robot_profile  # Module with network device configurations.

import config

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Função de tratamento do nó """
        
        print("[b white]State:[/] The robot is [b white]STRIKING[/] the [reverse b white on black] " + xml_node.attrib["type"] + " [/] pose.")


        message = xml_node.get("type").lower()
        
        base_topic = memory.get_base_topic()

        if base_topic == config.SIMULATOR_BASE_TOPIC or base_topic == robot_profile.ROBOT_BASE_TOPIC:
            # Mapping uppercase atributes to MQTT FRED lowercase atributes
            # m = {
            #         "GREEN"    : "green",
            #         "BLUE"     : "blue",
            #         "RED"      : "red",
            #         "RAINBOW"  : "rainbow",
            #         "BLACK"    : "black",
            #         "WHITE"    : "white",
            #         "PINK"     : "pink",
            #         "YELLOW"   : "yellow",

            #         "HAPPY"    : "green",
            #         "SAD"      : "blue",
            #         "ANGRY"    : "red",
            #         "STOP"     : "black",
            #         "SPEAK"    : "blue",
            #         "LISTEN"   : "green",
            #         "SURPRISE" : "yellow"
            # }

            self.send(topic_base=base_topic, mqtt_message=message)


        return xml_node # It returns the same node
