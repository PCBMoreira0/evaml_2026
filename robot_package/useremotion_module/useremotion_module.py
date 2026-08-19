from email.mime import base

from rich import print
from rich.console import Console

console = Console()


import robot_package.robot_profile as robot_profile  # Module with network device configurations.

import config


from base_command_handler import BaseCommandHandler


class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):

        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """Node handling function"""

        base_topic = memory.get_base_topic()

        if base_topic == config.TERMINAL_BASE_TOPIC:
            print(
                "[b white]STATE:[/] The Robot is [b green]recognizing[/] [b white]the user emotion[/].",
                end="",
            )

            user_answer = console.input("[b white on green blink] > [/] ")

            if xml_node.get("var") == None:
                memory.var_dollar.append([user_answer, "<userEmotion>"])
            else:
                var_name = xml_node.get("var")
                memory.vars[var_name] = user_answer

        elif base_topic == robot_profile.ROBOT_BASE_TOPIC:
            self.send(topic_base=base_topic)
            self.send(topic_base=base_topic, pub_topic="LEDS", mqtt_message="LISTEN")
            mqtt_response = self.receive()

            user_answer = mqtt_response["RESPONSE"]

            if xml_node.get("var") == None:
                memory.var_dollar.append([user_answer, "<userEmotion>"])
            else:
                var_name = xml_node.get("var")
                memory.vars[var_name] = user_answer

        return xml_node
