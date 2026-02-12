from rich import print
from rich.console import Console

console = Console()

import robot_profile  # Module with network device configurations.

import config

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

# Função de bloqueio que é usada para sincronia entre os módulos e o Script Player
# def block(state, memory, client_mqtt):
#     memory.robot_state = state # Altera o estado do robô.
#     client_mqtt.publish(topic_base + "/leds", "LISTEN")
#     while memory.robot_state != "free": # Aguarda que o robô fique livre para seguir para o próximo comando.
#         time.sleep(0.01)
#     client_mqtt.publish(topic_base + "/leds", "STOP")


    def node_process(self, xml_node, memory):
        """ Node handling function """

        # if memory.running_mode == "simulator":
        #     topic_base = config.SIMULATOR_BASE_TOPIC
        # elif memory.running_mode == "robot":
        #     topic_base = robot_profile.ROBOT_BASE_TOPIC
        # else:
        #     topic_base = config.TERMINAL_BASE_TOPIC

        # if xml_node.get("language") == None: # Maintains compatibility with the use of <listen> in old scripts
        #     # It will be used the default value defined in config.py file
        #     language_for_listen = config.LANG_DEFAULT_GOOGLE_TRANSLATING
        # else:
        #     language_for_listen =  xml_node.get("language")
        
        
        # Whether in terminal mode or terminal-plus mode, entries are made via the keyboard via the terminal.
        # client_mqtt.publish(topic_base + "/leds", "LISTEN")

        base_topic = memory.get_base_topic()
        
        if base_topic == config.TERMINAL_BASE_TOPIC:

            # client_mqtt.publish(topic_base + "/leds", "STOP")
            if xml_node.get("var") == None: # Maintains compatibility with the use of the $ variable
                print('[b white]State:[/] The Robot is [b green]listening[/] in [b white]' + xml_node.get("language") + '[/]. It will be stored in [b white]$[/] ', end="")
                # memory.var_dollar.append([user_answer, "<listen>"])
                user_answer = console.input("[b white on green blink] > [/] ")
                memory.setDollar([user_answer, "<listen>"])
            else:
                var_name = xml_node.get("var")
                print('[b white]State:[/] The Robot is [b green]listening[/] in [b white]' + xml_node.get("language") + '[/]. It will be stored in [b white]' + var_name + '[/] ', end="")
                # memory.vars[var_name] = user_answer
                user_answer = console.input("[b white on green blink] > [/] ")
                memory.setVar(var_name, user_answer)
        
        
  
            
        # Controls the physical robot.
        if memory.running_mode == "robot": 
            pass
            # client = create_mqtt_client()
            # client.publish(robot_topic_base + '/' + xml_node.tag, message)

        return xml_node # It returns the same node

