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
            emoji = " 😠"
        elif xml_node.get("emotion") == "ANGRY2":
            emoji = " 😡"
        elif xml_node.get("emotion") == "AFRAID":
            emoji = " 😧"
        elif xml_node.get("emotion") == "HAPPY":
            emoji = " 😄"
        elif xml_node.get("emotion") == "IN_LOVE":
            emoji = " 🥰"
        elif xml_node.get("emotion") == "SAD":
            emoji = " 😔"
        elif xml_node.get("emotion") == "SURPRISED":
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


        print("[b white]State:[/] Setting the robot [b white]expression[/] to [b white]" + xml_node.get("emotion") + emoji + "[/].")

        message = xml_node.get("emotion")

        base_topic = memory.get_base_topic()

        if memory.get_running_mode() == 'simulator':
            print("[b red reverse] Not implemented in simulation mode... Sorry! [/]")
            # # Mapping to FRED Simulator
            # m = {
            #     "GREETINGS": "greetings",
            #     "ANGRY"    : "angry",
            #     "ANGRY2"    : "angry",
            #     "HAPPY"    : "happy",
            #     "SAD"      : "sad",
            #     "NEUTRAL"  : "neutral",
            #     "PLEASED"  : "pleased",
            #     "AFRAID"   : "afraid",
            #     "SURPRISED": "surprised"
            # }

            # print(m[message], base_topic)

            # self.send(topic_base=base_topic, mqtt_message=m[message])
            # exit()

        elif memory.get_running_mode() == 'robot':
            # Converting uppercase atributes to MQTT FRED lowercase atributes
            message = message.lower()
            self.send(topic_base=base_topic, mqtt_message=message)



        return xml_node # It returns the same node

