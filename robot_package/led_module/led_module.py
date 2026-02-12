import time

from rich import print

import config

import robot_profile  # Module with network device configurations.

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Função de tratamento do nó """


        print("[b white]State: Setting [/]the robot [b white]LEDs[/] to the animation/color [bold]" + xml_node.get("animation") + "![/].")

        message = xml_node.get("animation")
        
        base_topic = memory.get_base_topic()

        if base_topic == config.SIMULATOR_BASE_TOPIC or base_topic == robot_profile.ROBOT_BASE_TOPIC:
            self.send(topic_base=base_topic, mqtt_message=message)


        return xml_node # It returns the same node