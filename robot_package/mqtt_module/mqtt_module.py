from rich import print

import re

import robot_profile  # Module with network device configurations.

import config

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Node handling function """

        if (len(xml_node.get("pubTopic"))) == 0: # error
            print("[b white on red blink] FATAL ERROR [/]: The [bold white]MQTT topic[/] is [b reverse white] EMPTY [/].✋⛔️")
            exit(1)

        if xml_node.text == None: # There is no text to send.
            print("[b white on red blink] FATAL ERROR [/]:[bold] There is [b reverse white] no message [/] to send.✋⛔️")
            exit(1)

        message = xml_node.text
        palavras = message.split()
        message = ' '.join(palavras) # Removing more than one space between words.
        message = message.replace('\n', '').replace('\r', '').replace('\t', '') # Remove tabs and line breaks.
        # Replace variables throughout the text. variables must exist in memory
        if "#" in message:
            var_list = re.findall(r'\#[a-zA-Z]+[a-zA-Z0-9_-]*', message) # Generate list of occurrences of vars (#...)
            for v in var_list:
                if v[1:] in memory.vars:
                    message = message.replace(v, str(memory.vars[v[1:]]))
                    print(message)
                else:
                    # If the variable does not exist in the robot's memory, it displays an error message
                    print("[b white on red blink] FATAL ERROR [/]:  The variable [b white]" + v[1:] + "[/] used in[b white] MQTT[/] element,[b yellow reverse] has not been declared [/]. Please, check your code.✋⛔️")
                    exit(1)

        # This part replaces the $, or the $-1 or the $1 in the text
        if "$" in message: # Check if there is $ in the text
            # Checks if var_dollar has any value in the robot's memory
            if (len(memory.var_dollar)) == 0:
                exit(1)
            else: # Find the patterns $ $n or $-n in the string and replace with the corresponding values
                dollars_list = re.findall(r'\$[-0-9]*', message) # Find dollar patterns and return a list of occurrences
                dollars_list = sorted(dollars_list, key=len, reverse=True) # Sort the list in descending order of length (of the element)
                for var_dollar in dollars_list:
                    if len(var_dollar) == 1: # Is the dollar ($)
                        message = message.replace(var_dollar, memory.var_dollar[-1][0])
                    else: # May be of type $n or $-n
                        if "-" in var_dollar: # $-n type
                            indice = int(var_dollar[2:]) # Var dollar is of type $-n. then just take n and convert it to int
                            message = message.replace(var_dollar, memory.var_dollar[-(indice + 1)][0]) 
                        else: # tipo $n
                            indice = int(var_dollar[1:]) # Var dollar is of type $n. then just take n and convert it to int
                            message = message.replace(var_dollar, memory.var_dollar[(indice - 1)][0])

        print("[b white ]STATE[/]:[bold] Sending the [b white]MQTT message: [/][yellow]" + message + "[/]. [b white] TOPIC: [/][reverse cyan] " + xml_node.get("pubTopic") + " [/].") #  to the topic: [b white]" + node.get("topic") + "[/]."

        base_topic = memory.get_base_topic()

        if base_topic == config.SIMULATOR_BASE_TOPIC or base_topic == robot_profile.ROBOT_BASE_TOPIC:
            self.send(topic_base=base_topic, pub_topic=xml_node.get("pubTopic"), mqtt_message=message)
        
        return xml_node # It returns the same node
