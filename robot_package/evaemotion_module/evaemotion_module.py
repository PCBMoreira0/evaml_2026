from rich import print

import robot_profile  # Module with network device configurations.

import config

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Node handling function """


        if xml_node.get("emotion") == "NEUTRAL":
            emoji = " 😐"
        elif xml_node.get("emotion") == "ANGRY":
            emoji = " 😡"
        elif xml_node.get("emotion") == "DISGUST":
            emoji = " 😖"
        elif xml_node.get("emotion") == "FEAR":
            emoji = " 😧"
        elif xml_node.get("emotion") == "HAPPY":
            emoji = " 😄"
        elif xml_node.get("emotion") == "INLOVE":
            emoji = " 🥰"
        elif xml_node.get("emotion") == "SAD":
            emoji = " 😔"
        elif xml_node.get("emotion") == "SURPRISE":
            emoji = " 😲"

        print("[b white]State:[/] Setting the robot [b white]expression[/] to [b white]" + xml_node.get("emotion") + emoji + "[/].")

        message = xml_node.get("emotion")

        base_topic = memory.get_base_topic()

        if base_topic == config.SIMULATOR_BASE_TOPIC or base_topic == robot_profile.ROBOT_BASE_TOPIC:
            self.send(topic_base=base_topic, mqtt_message=message)


        return xml_node # It returns the same node

