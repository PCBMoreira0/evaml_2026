from rich import print

import robot_profile  # Module with network device configurations.

import config

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Função de tratamento do nó """

        if xml_node.get('state') == "OFF":
            light_color = 'BLACK'
            message = light_color + "|" + 'OFF'
        else:
            if xml_node.get('color') == None:
                light_color = 'WHITE'
                message = light_color + "|" + xml_node.get("state")
            else:
                light_color = xml_node.get('color')
                message = light_color + "|" + xml_node.get("state")

        tab_colors = {"BLACK": "[b white on grey19] OFF [/]",
                    "BLUE": "[b white on blue ] ON [/]",
                    "GREEN": "[b white on green ] ON [/]",
                    "PINK": "[b white on magenta ] ON [/]",
                    "RED": "[b white on red ] ON [/]",
                    "YELLOW": "[b white on yellow ] ON [/]",
                    "WHITE": "[b reverse white] ON [/]"
                    }
        print("[b white]State: Setting [/]the [b white]Smart Bulb[/]. 💡 " + tab_colors[light_color])
        
        base_topic = memory.get_base_topic()

        if base_topic == config.SIMULATOR_BASE_TOPIC or base_topic == robot_profile.ROBOT_BASE_TOPIC:
            self.send(topic_base=base_topic, mqtt_message=message)


        return xml_node # It returns the same node