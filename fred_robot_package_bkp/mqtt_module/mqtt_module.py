from rich import print

import re

import sys



def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """

    if (len(node.get("topic"))) == 0: # erro
        print("[b white on red blink] FATAL ERROR [/]: The [bold white]MQTT topic[/] is [b reverse white] EMPTY [/].✋⛔️")
        exit(1)

    if node.text == None: # There is no text to send.
        print("[b white on red blink] FATAL ERROR [/]:[bold] There is [b reverse white] no message [/] to send.✋⛔️")
        exit(1)

    texto = node.text
    palavras = texto.split()
    texto = ' '.join(palavras) # Removendo mais de um espaço entre as palavras.
    texto = texto.replace('\n', '').replace('\r', '').replace('\t', '') # Remove tabulações e salto de linha.
    # Replace variables throughout the text. variables must exist in memory
    if "#" in texto:
        var_list = re.findall(r'\#[a-zA-Z]+[a-zA-Z0-9_-]*', texto) # Generate list of occurrences of vars (#...)
        for v in var_list:
            if v[1:] in memory.vars:
                texto = texto.replace(v, str(memory.vars[v[1:]]))
                print(texto)
            else:
                # If the variable does not exist in the robot's memory, it displays an error message
                print("[b white on red blink] FATAL ERROR [/]:  The variable [b white]" + v[1:] + "[/] used in[b white] MQTT[/] element,[b yellow reverse] has not been declared [/]. Please, check your code.✋⛔️")
                exit(1)

    # This part replaces the $, or the $-1 or the $1 in the text
    if "$" in texto: # Check if there is $ in the text
        # Checks if var_dollar has any value in the robot's memory
        if (len(memory.var_dolar)) == 0:
            exit(1)
        else: # Find the patterns $ $n or $-n in the string and replace with the corresponding values
            dollars_list = re.findall(r'\$[-0-9]*', texto) # Find dollar patterns and return a list of occurrences
            dollars_list = sorted(dollars_list, key=len, reverse=True) # Sort the list in descending order of length (of the element)
            for var_dollar in dollars_list:
                if len(var_dollar) == 1: # Is the dollar ($)
                    texto = texto.replace(var_dollar, memory.var_dolar[-1][0])
                else: # May be of type $n or $-n
                    if "-" in var_dollar: # $-n type
                        indice = int(var_dollar[2:]) # Var dollar is of type $-n. then just take n and convert it to int
                        texto = texto.replace(var_dollar, memory.var_dolar[-(indice + 1)][0]) 
                    else: # tipo $n
                        indice = int(var_dollar[1:]) # Var dollar is of type $n. then just take n and convert it to int
                        texto = texto.replace(var_dollar, memory.var_dolar[(indice - 1)][0])

    print("[b white ]STATE[/]:[bold] Sending the [b white]MQTT message: [/][yellow]" + texto + "[/]. [b white] TOPIC: [/][reverse cyan] " + node.get("topic") + " [/].") #  to the topic: [b white]" + node.get("topic") + "[/]."

    # Envia para o robô físico.
    if memory.running_mode == "robot":
        # Envia para o robô.
        client_mqtt.publish(node.get("topic"), texto)    
    
    return node # It returns the same node
