from rich import print as rprint

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Node handling function """
        rprint("[bold white]State:[/] [b white]Stopping [/]the script.")

        return xml_node # It returns the "target" node.