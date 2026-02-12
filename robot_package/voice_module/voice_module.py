from rich import print

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):

        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Node pocess function """
        
        memory.set_default_voice(xml_node.get("type"))

        print("[b white]State: Setting [/]the robot default[b white] voice=" + xml_node.get("type") + "[/].")

        return xml_node # It returns the same node