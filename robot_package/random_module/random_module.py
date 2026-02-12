import random as rnd

from rich import print

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Node handling function """

        min = xml_node.get("min")
        max = xml_node.get("max")
        
        # Check if min <= max
        if (int(min) > int(max)):
            aux = min
            min = max
            max = aux
            print('[b blink reverse red] Warning [/]: The value of [b white]min=' + str(min) + '[/] is greater than[b white] max=' + str(max) + '[/]. We [u]fixed[/] it. 👍') 

        if xml_node.get("var") == None: # Maintains compatibility with the use of the $ variable
            result = str(rnd.randint(int(min), int(max)))
            memory.var_dollar.append([result, "<random>"])
            print('[b white]State:[/] [b white]Generating[/] a [b white]random[/] integer between [b white]min=' + str(min) + '[/] and [b white]max=' + str(max) + '[/]. Putting the [b white]result=' + result + ' [/]in the [b white]$[/] variable.')
        else:
            var_name = xml_node.attrib["var"]
            result = str(rnd.randint(int(min), int(max)))
            memory.vars[var_name] = result
            print('[b white]State:[/] [b white]Generating[/] a [b white]random[/] integer between [b white]min=' + str(min) + '[/] and [b white]max=' + str(max) + '[/]. Putting the [b white]result=' + result + ' in the [b white]' + var_name + '[/] variable.')

        return xml_node # It returns the same node
