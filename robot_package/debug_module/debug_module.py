from rich import print, box
from rich.console import Console
from rich.table import Table

console = Console()

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Node handling function """

        # Operation: PAUSE.
        if xml_node.get("operation") == "PAUSE":
            print('[b reverse yellow]Debug mode:[/] Executing a [white b]PAUSE[/] operation. To continue, please press [b white]<ENTER>[/].', end="")
            input()

        # Operation: Show dollar var contents.
        elif xml_node.get("operation") == "SHOW_DOLLAR_VAR":
            print('[b reverse yellow]Debug mode:[/] Showing the [white b]Dollar Variable[/] Contents Table.')
            print("")
            table = Table(title="[b]Table: Dollar ($) Variable Contents (Memory MAP)[/]")
            table.add_column("Index")
            table.add_column("Content")
            table.add_column("Source")
            dollar_item_conter = 1
            total_dollar_items = len(memory.getDollar())
            for item in memory.getDollar():
                if dollar_item_conter == total_dollar_items:
                    table.add_row("$", "[bold yellow]" + item[0], "[bold cyan ]" + item[1])
                else:
                    table.add_row("$" + str(dollar_item_conter), "[bold yellow]" + item[0], "[bold cyan ]" + item[1])
                    dollar_item_conter += 1
            console.print(table)

        # Operation: Show user vars contents.
        elif xml_node.get("operation") == "SHOW_USER_VARS":
            print('[b reverse yellow]Debug mode:[/] Showing the [white b]User Variables Contents[/] Table.')
            print("")
            table = Table(title="[b]Table: User Variables Contents (Memory MAP)[/]")
            table.add_column("Variable Name")
            table.add_column("Content")
            for var_name, value in memory.getVars().items():
                table.add_row("[yellow b]" + var_name + "[/]", value)
            console.print(table)

            
        return xml_node # It returns the same node