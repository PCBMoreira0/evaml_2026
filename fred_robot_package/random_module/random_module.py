import random as rnd

from rich import print



def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """

    min = node.get("min")
    max = node.get("max")
    
    # Check if min <= max
    if (int(min) > int(max)):
        aux = min
        min = max
        max = aux
        print('[b blink reverse red] Warning [/]: The value of [b white]min=' + str(min) + '[/] is greater than[b white] max=' + str(max) + '[/]. We [u]fixed[/] it. 👍') 

    if node.get("var") == None: # Maintains compatibility with the use of the $ variable
        result = str(rnd.randint(int(min), int(max)))
        memory.var_dolar.append([result, "<random>"])
        print('[b white]State:[/] [b white]Generating[/] a [b white]random[/] integer between [b white]min=' + str(min) + '[/] and [b white]max=' + str(max) + '[/]. Putting the [b white]result=' + result + ' [/]in the [b white]$[/] variable.')
    else:
        var_name = node.attrib["var"]
        result = str(rnd.randint(int(min), int(max)))
        memory.vars[var_name] = result
        print('[b white]State:[/] [b white]Generating[/] a [b white]random[/] integer between [b white]min=' + str(min) + '[/] and [b white]max=' + str(max) + '[/]. Putting the [b white]result=' + result + ' in the [b white]' + var_name + '[/] variable.')

    return node # It returns the same node
