from rich import print

import numpy as np

from base_command_handler import BaseCommandHandler

import robot_profile  # Module with network device configurations.


class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Node process function """


        if xml_node.get("profile") != None:
            if xml_node.get("profile") == "NEUTRAL":
                memory.set_empathy("0.30")
                memory.set_decay("0.70")
                memory.set_base_mood("0.0, 0.0, 0.0")

            elif xml_node.get("profile") == "EMPATHETIC":
                memory.set_empathy("0.9")
                memory.set_decay("0.10")
                memory.set_base_mood("0.0, 0.0, 0.0")

            elif xml_node.get("profile") == "THERAPEUTIC":
                memory.set_empathy("0.5")
                memory.set_decay("0.7")
                memory.set_base_mood("0.0, 0.0, 0.0")

            elif xml_node.get("profile") == "OPTIMISTIC":
                memory.set_empathy("0.9")
                memory.set_decay("0.1")
                memory.set_base_mood("0.3, 0.2, 0.2") # Verificar esta posição no espaço de acordo com o artigo.

            elif xml_node.get("profile") == "MELANCHOLIC":
                memory.set_empathy("0.10")
                memory.set_decay("0.08")
                memory.set_base_mood("-0.3, -0.3, -0.5") 
            else:
                # Profile not found...
                exit(1)
        else:
            xml_node.set("profile", "UNCATEGORIZED")
            memory.set_empathy(xml_node.get("empathy"))
            memory.set_decay(xml_node.get("decay"))
            memory.set_base_mood(xml_node.get("baseMood"))

        print("[b white]State: Setting [/]the [b white]robot affective profile=" + xml_node.get("profile") + "[/].")
        print("[b white]State: Setting [/]the [b white]robot empathy=" + memory.get_empathy() + "[/].")
        print("[b white]State: Setting [/]the [b white]robot emotion decay=" + memory.get_decay() + "[/].")
        print("[b white]State: Setting [/]the [b white]robot base mood (VAD vector)=" + memory.get_base_mood() + "[/].")
                
        base_topic = memory.get_base_topic()

        message = xml_node.get('profile') + "|" + memory.get_empathy() + "|" + memory.get_decay() + "|" + memory.get_base_mood()
        

        if base_topic == robot_profile.SIMULATOR_BASE_TOPIC or base_topic == robot_profile.ROBOT_BASE_TOPIC:
            self.send(topic_base=base_topic, mqtt_message=message)

        return xml_node # It returns the same node
        