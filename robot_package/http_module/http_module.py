from rich import print

import re

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    # Sem __init__ definido, usa o __init__ da classe mãe (BaseCommandHandler)
    def node_process(self, xml_node, memory):
        """ Node handling function """

        self.send(xml_node.text)

        return xml_node # It returns the same node
