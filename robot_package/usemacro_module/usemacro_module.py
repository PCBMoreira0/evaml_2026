from rich import print as rprint

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Node handling function """

        # Checks if the <macro> has the "id" attribute set
        macro_id = xml_node.get('macro')
        if macro_id == None:
            rprint("[red bold]Macro ID was not found on <useMacro>.")
            exit(1)

        # Search for id in tab_ids
        for key, value in memory.tab_ids.items():
            if key == xml_node.get("macro"):
                rprint("[b white]State:[/] Using macro [b white]" + key + "[/].")
                return value[1] # Returns the macro associated with the found "id".
        
        # Could not find "id"
        rprint("[red bold]It was not possible to find the macro: " + key)
        exit(1)

    
