import time

import random as rnd
import re
from rich import print

import config  # Module with network device configurations.

import robot_profile  # Module with network device configurations.


from base_command_handler import BaseCommandHandler


class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):

        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """Node handling function"""

        base_topic = memory.get_base_topic()

        # Node processing
        if xml_node.text == None:  # There is no text to speech
            print(
                "[b white on red blink] FATAL ERROR [/]: [b yellow reverse] There is no text to speech [/] in the element [b white]<talk>[/]. Please, check your code.✋⛔️"
            )
            exit(1)

        text_to_speech = xml_node.text
        palavras = text_to_speech.split()
        texto_normalizado = " ".join(palavras)
        text_to_speech = (
            texto_normalizado.replace("\n", "").replace("\r", "").replace("\t", "")
        )  # Remove tabulações e salto de linha.
        # Replace variables throughout the text. variables must exist in memory
        if "#" in text_to_speech:
            # Checks if the robot's memory (vars) is empty
            if memory.vars == {}:
                print(
                    "[b white on red blink] FATAL ERROR [/]: [b yellow reverse] No variables have been defined [/] to be used in the[b white] <talk>[/]. Please, check your code.✋⛔️"
                )
                exit(1)

            var_list = re.findall(
                r"\#[a-zA-Z_]+[0-9]*", text_to_speech
            )  # Generate list of occurrences of vars (#...)
            for v in var_list:
                if v[1:] in memory.vars:
                    text_to_speech = text_to_speech.replace(v, str(memory.vars[v[1:]]))
                else:
                    # If the variable does not exist in the robot's memory, it displays an error message
                    print(
                        "[b white on red blink] FATAL ERROR [/]: The variable [b white]"
                        + v[1:]
                        + "[/] [b yellow reverse] has not been declared [/] to be used in the [b white]<talk>[/]. Please, check your code.✋⛔️"
                    )
                    exit(1)

        # This part replaces the $, or the $-1 or the $1 in the text
        if "$" in text_to_speech:  # Check if there is $ in the text
            # Checks if var_dollar has any value in the robot's memory
            if (len(memory.var_dollar)) == 0:
                print(
                    "[b white on red blink] FATAL ERROR [/]: There are [b yellow reverse] no values [/] for the [b white]$[/] used in the [b white]<talk>[/]. Please, check your code.✋⛔️"
                )
                exit(1)
            else:  # Find the patterns $ $n or $-n in the string and replace with the corresponding values
                dollars_list = re.findall(
                    r"\$[-0-9]*", text_to_speech
                )  # Find dollar patterns and return a list of occurrences
                dollars_list = sorted(
                    dollars_list, key=len, reverse=True
                )  # Sort the list in descending order of length (of the element)
                for var_dollar in dollars_list:
                    if len(var_dollar) == 1:  # Is the dollar ($)
                        text_to_speech = text_to_speech.replace(
                            var_dollar, memory.var_dollar[-1][0]
                        )
                    else:  # May be of type $n or $-n
                        if "-" in var_dollar:  # $-n type
                            indice = int(
                                var_dollar[2:]
                            )  # Var dollar is of type $-n. then just take n and convert it to int.
                            try:
                                text_to_speech = text_to_speech.replace(
                                    var_dollar, memory.var_dollar[-(indice + 1)][0]
                                )
                            except IndexError:
                                print(
                                    '[b white on red blink] FATAL ERROR [/]: There was an [b yellow reverse] index error [/] for the variable [b white]"'
                                    + var_dollar
                                    + '"[/]. Please, check your code.✋⛔️'
                                )
                                exit(1)
                        else:  # tipo $n
                            indice = int(
                                var_dollar[1:]
                            )  # Var dollar is of type $n. then just take n and convert it to int.
                            try:
                                text_to_speech = text_to_speech.replace(
                                    var_dollar, memory.var_dollar[(indice - 1)][0]
                                )
                            except IndexError:
                                print(
                                    '[b white on red blink] FATAL ERROR [/]: There was an [b yellow reverse] index error [/] for the variable [b white]"'
                                    + var_dollar
                                    + '"[/]. Please, check your code.✋⛔️'
                                )
                                exit(1)

        # This part implements the random text generated by using the / character
        text_to_speech = text_to_speech.split(
            sep="/"
        )  # Text becomes a list with the number of sentences divided by character. /
        ind_random = rnd.randint(0, len(text_to_speech) - 1)


        if base_topic == config.TERMINAL_BASE_TOPIC:
            # Running in terminal mode....
            print(
                '[b white]State:[/] The Robot is [b blue]speaking[/] the sentence: [b white]"[/]',
                end="",
            )
            print("[b white]" + text_to_speech[ind_random])
            print('[b white]"')

        elif base_topic == robot_profile.ROBOT_BASE_TOPIC:
            print(
                '[b white]State:[/] The Robot is [b blue]speaking[/] the sentence: [b white]"[/]',
                end="",
            )
            for c in text_to_speech[ind_random]:
                print("[b white]" + c + "[/]", end="")
            print('[b white]"')
            if xml_node.get("voiceType") == None:
                message = memory.default_voice + "|" + text_to_speech[ind_random]
            elif xml_node.get("voiceType") != None:
                message = xml_node.get("voiceType") + "|" + text_to_speech[ind_random]

            self.send(topic_base=base_topic, mqtt_message=message)
            self.send(topic_base=base_topic, pub_topic="LEDS", mqtt_message="SPEAK")

            mqtt_response = (
                self.receive()
            )  # self.receive() returns a dict {RESPONSE: "response"}
            self.send(topic_base=base_topic, pub_topic="LEDS", mqtt_message="STOP")

        return xml_node  # It returns the same node
