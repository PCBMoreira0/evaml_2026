# import sounddevice as sd
# import speech_recognition as sr


from rich import print
from rich.console import Console

console = Console()

import robot_profile  # Module with network device configurations.

import config

from base_command_handler import BaseCommandHandler

# recognizer = sr.Recognizer()
# microphone = sr.Microphone(chunk_size = 64)
# threshold = 980 # Regulates the sensitivity between speech and silence. A good value tested in my house was 980.
# timeout = 10

# r.dynamic_energy_threshold = False
# recognizer.energy_threshold = threshold # Audio capture sensitivity.


class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):

        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """Node handling function"""

        base_topic = memory.get_base_topic()

        if base_topic == config.TERMINAL_BASE_TOPIC:
            if (
                xml_node.get("var") == None
            ):  # Maintains compatibility with the use of the $ variable
                print(
                    "[b white]State:[/] The Robot is [b green]listening[/] in [b white]"
                    + xml_node.get("language")
                    + "[/]. It will stored in [b white]$[/] ",
                    end="",
                )
                user_answer = console.input("[b white on green blink] > [/] ")
                memory.setDollar([user_answer, "<listen>"])
            else:
                var_name = xml_node.get("var")
                print(
                    "[b white]State:[/] The Robot is [b green]listening[/] in [b white]"
                    + xml_node.get("language")
                    + "[/]. It will stored in [b white]"
                    + var_name
                    + "[/] ",
                    end="",
                )
                user_answer = console.input("[b white on green blink] > [/] ")
                memory.setVar(var_name, user_answer)

        elif base_topic == robot_profile.ROBOT_BASE_TOPIC:
            self.send(topic_base=base_topic, pub_topic="LEDS", mqtt_message="LISTEN")
            self.send(topic_base=base_topic, mqtt_message="pt-BR")

            mqtt_response = self.receive()

            user_answer = ""
            self.send(topic_base=base_topic, pub_topic="LEDS", mqtt_message="STOP")

            if mqtt_response["RESPONSE"].split("|")[0].strip() == "[ABORT]":
                print("❌ Listening não conseguiu entender o que foi dito.")
            else:
                user_answer = mqtt_response["RESPONSE"]

            if (
                xml_node.get("var") == None
            ):  # Maintains compatibility with the use of the $ variable
                print(
                    "[b white]State:[/] The Robot is [b green]listening[/] in [b white]"
                    + xml_node.get("language")
                    + "[/]. It will be stored in [b white]$[/] ",
                    end="",
                )
                memory.setDollar([user_answer, "<listen>"])
            else:
                var_name = xml_node.get("var")
                print(
                    "[b white]State:[/] The Robot is [b green]listening[/] in [b white]"
                    + xml_node.get("language")
                    + "[/]. It will be stored in [b white]"
                    + var_name
                    + "[/] ",
                    end="",
                )
                memory.setVar(var_name, user_answer)

        return xml_node
