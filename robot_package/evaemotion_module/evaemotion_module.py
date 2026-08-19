from rich import print

import robot_profile  # Module with network device configurations.

import config

from base_command_handler import BaseCommandHandler


class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):

        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """Node handling function"""

        if xml_node.get("emotion") == "NEUTRAL":
            emoji = " 😐"
        elif xml_node.get("emotion") == "ANGRY":
            emoji = " 😠"
        elif xml_node.get("emotion") == "ANGRY2":
            emoji = " 😡"
        elif xml_node.get("emotion") == "FEAR":
            emoji = " 😧"
        elif xml_node.get("emotion") == "DISGUST":
            emoji = " 🤢"
        elif xml_node.get("emotion") == "HAPPY":
            emoji = " 😄"
        elif xml_node.get("emotion") == "INLOVE":
            emoji = " 🥰"
        elif xml_node.get("emotion") == "SAD":
            emoji = " 😔"
        elif xml_node.get("emotion") == "SURPRISE":
            emoji = " 😲"
        elif xml_node.get("emotion") == "BROKEN":
            emoji = " 😵"
        elif xml_node.get("emotion") == "GREETINGS":
            emoji = " [b red]FRED ❤️[/]"
        elif xml_node.get("emotion") == "PLEASED":
            emoji = " 😌"
        elif xml_node.get("emotion") == "SPEECH_ON_1":
            emoji = " 🗣️"
        elif xml_node.get("emotion") == "SPEECH_OFF_1":
            emoji = " 🤐"
        elif xml_node.get("emotion") == "SPEECH_ON_2":
            emoji = " 🗣️"
        elif xml_node.get("emotion") == "SPEECH_OFF_2":
            emoji = " 🤐"

        print(
            "[b white]State:[/] Setting the robot [b white]expression[/] to [b white]"
            + xml_node.get("emotion")
            + emoji
            + "[/]."
        )

        message = xml_node.get("emotion")

        base_topic = memory.get_base_topic()

        if base_topic == robot_profile.ROBOT_BASE_TOPIC:
            message = message.upper()
            self.send(topic_base=base_topic, mqtt_message=message)

        return xml_node
