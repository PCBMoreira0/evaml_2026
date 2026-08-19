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
        
        print("[b white]State:[/] The robot is [b white]MOVING[/]. [b white]Type: [/][reverse b white on black] " + xml_node.attrib["head"] + " [/].")
        
        body = "HEAD"
        message = xml_node.get("head")
        
        base_topic = memory.get_base_topic()

        if base_topic == robot_profile.ROBOT_BASE_TOPIC:
            self.send(pub_topic=base_topic + "/MOTION" + "/HEAD", mqtt_message=message)
            


        return xml_node
    