import time

from rich import print

import robot_package.robot_profile as robot_profile  # Module with network device configurations.

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Função de tratamento do nó """


        print("[b white]STATE: Setting [/]the robot [b white]LEDs[/] to the animation/color [bold]" + xml_node.get("animation") + "![/].")

        message = xml_node.get("animation")
        
        base_topic = memory.get_base_topic()

        if base_topic == robot_profile.SIMULATOR_BASE_TOPIC or base_topic == robot_profile.ROBOT_BASE_TOPIC:
            # Mapping uppercase atributes to MQTT FRED lowercase atributes
            m = {
                    "GREEN"     : "green",
                    "GREEN0"    : "green0",
                    "GREEN1"    : "green1",
                    "GREEN2"    : "green2",
                    "BLUE"      : "blue",
                    "BLUE0"     : "blue0",
                    "BLUE1"     : "blue1",
                    "BLUE2"     : "blue2",
                    "RED"       : "red",
                    "RED0"      : "red0",
                    "RED1"      : "red1",
                    "RED2"      : "red2",
                    "RAINBOW"   : "rainbow",
                    "BLACK"     : "black",
                    "WHITE"     : "white",
                    "WHITE0"    : "white0",
                    "WHITE1"    : "white1",
                    "WHITE2"    : "white2",
                    "PINK"      : "pink",
                    "PINK0"     : "pink0",
                    "PINK1"     : "pink1",
                    "PINK2"     : "pink2",
                    "YELLOW"    : "yellow",
                    "YELLOW0"   : "yellow0",
                    "YELLOW1"   : "yellow1",
                    "YELLOW2"   : "yellow2",

                    "HAPPY"     : "green",
                    "HAPPY0"    : "green0",
                    "HAPPY1"    : "green1",
                    "HAPPY2"    : "green2",
                    "SAD"       : "blue",
                    "SAD0"      : "blue0",
                    "SAD1"      : "blue1",
                    "SAD2"      : "blue2",
                    "ANGRY"     : "red",
                    "ANGRY0"    : "red0",
                    "ANGRY1"    : "red1",
                    "ANGRY2"    : "red2",
                    "STOP"      : "black",
                    "SPEAK"     : "blue",
                    "LISTEN"    : "green",
                    "SURPRISE"  : "yellow",
                    "SURPRISE0" : "yellow0",
                    "SURPRISE1" : "yellow1",
                    "SURPRISE2" : "yellow2",

                    "GREEN_BLUE"    : "green_blue",
                    "BLUE_GREEN"      : "blue_green",
                    "GREEN_RED"    : "green_red",
                    "RED_GREEN"     : "red_green",
                    "GREEN_YELLOW"    : "green_yellow",
                    "YELLOW_GREEN"   : "yellow_green",
                    "BLUE_RED" : "blue_red",
                    "RED_BLUE" : "red_blue",
                    "BLUE_YELLOW" : "blue_yellow",
                    "YELLOW_BLUE" : "yellow_blue",
                    "YELLOW_RED" : "yellow_red",
                    "RED_YELLOW" : "red_yellow",

                    "HAPPY_SAD"    : "green_blue",
                    "SAD_HAPPY"      : "blue_green",
                    "HAPPY_ANGRY"    : "green_red",
                    "ANGRY_HAPPY"     : "red_green",
                    "HAPPY_SURPRISE"    : "green_yellow",
                    "SURPRISE_HAPPY"   : "yellow_green",
                    "SAD_ANGRY" : "blue_red",
                    "ANGRY_SAD" : "red_blue",
                    "SAD_SURPRISE" : "blue_yellow",
                    "SURPRISE_SAD" : "yellow_blue",
                    "SURPRISE_ANGRY" : "yellow_red",
                    "ANGRY_SURPRISE" : "red_yellow"
            }

            self.send(topic_base=base_topic, mqtt_message=m[message])


        return xml_node # It returns the same node