from rich import print

from base_command_handler import BaseCommandHandler


class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)
        
    def node_process(self, xml_node, memory):
        """ Node process function """
            
        print("[b white]State: Setting [/]the [b white] light effects=" + xml_node.get("mode") + "[/].")

        return xml_node # It returns the same node