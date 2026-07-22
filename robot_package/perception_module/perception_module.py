import json

from rich import print

import robot_profile  # Module with network device configurations.

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)


    def node_process(self, xml_node, memory):
        """ Node handling function """

        if xml_node.get("action") == "START":
            # verifica se tem sources
            if xml_node.get("sources") == None:
                print("[b white on red blink] FATAL ERROR [/]: There is no [bold white]sources [/]defined in [bold white]perception[/] element. ✋⛔️")
                exit(1)
            else:
                message = {
                    "action": "START",
                    "sources": [s.strip() for s in xml_node.get("sources").split(",") if s.strip()]
                }
                message = json.dumps(message)
                print("[b white ]STATE[/]:[b green] Perception window [/]started. [b blue]PULSE[/] will use the following sources: [yellow]" + xml_node.get("sources") + "[/].")

        else: # Igual a END
            message = {
                "action": "END"
            }

            message = json.dumps(message)
            print("[b white ]STATE[/]:[b green] Perception window [/]ended.")


        
        base_topic = memory.get_base_topic()

        if base_topic == robot_profile.SIMULATOR_BASE_TOPIC or base_topic == robot_profile.ROBOT_BASE_TOPIC:
            self.send(topic_base=base_topic, pub_topic=xml_node.get("pubTopic"), mqtt_message=message)
        
        
        return xml_node # It returns the same node
