 
from rich import print
from rich.console import Console

console = Console()

import robot_profile  # Module with network device configurations.

import config


from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Node handling function """   

        base_topic = memory.get_base_topic()

        # When in terminal mode or terminal-plus mode, entries are made via keyboard via the terminal and the base_topic is TERMINAL_BASE_TOPIC that is TERMINAL.
        if base_topic == config.TERMINAL_BASE_TOPIC: # It is TERMINAL
            
            if xml_node.get("var") == None: # Maintains compatibility with the use of the $ variable
                print('[b white]State:[/] The Robot is [b green]reading[/] [b white]a QR Code[/]. It will be stored in [b white]$[/] ', end="")
            else:
                print('[b white]State:[/] The Robot is [b green]reading[/] [b white]a QR Code[/]. It will be stored in [b white]' + xml_node.get("var") + '[/] ' , end="")

            user_answer = console.input("[b white on green blink] > [/] ")
            
            if xml_node.get("var") == None: # Maintains compatibility with the use of the $ variable
                memory.setDollar([user_answer, "<qrRead>"])
            else:
                var_name = xml_node.get("var")
                memory.setVar(var_name, user_answer)
        
        

        if base_topic == config.SIMULATOR_BASE_TOPIC or base_topic == robot_profile.ROBOT_BASE_TOPIC:
            self.send(topic_base=base_topic)
            
            if xml_node.get("var") == None: # Maintains compatibility with the use of the $ variable
                print('[b white]State:[/] The Robot is [b green]reading[/] [b white]a QR Code[/]. It will be stored in [b white]$[/].')
            else:
                print('[b white]State:[/] The Robot is [b green]reading[/] [b white]a QR Code[/]. It will be stored in [b white]' + xml_node.get("var") + '[/].')

            mqtt_response = self.receive() # self.receive() returns a dict {RESPONSE: "response"}

            if xml_node.get("var") == None: # Maintains compatibility with the use of the $ variable
                memory.setDollar([mqtt_response["RESPONSE"], "<qrRead>"])
            else:
                var_name = xml_node.get("var")
                memory.setVar(var_name, mqtt_response["RESPONSE"])

        return xml_node # It returns the same node

