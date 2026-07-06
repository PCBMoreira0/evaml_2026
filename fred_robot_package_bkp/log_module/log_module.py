from rich import print

import re

import sys

import config  # Module with network device configurations.

sys.path.insert(0, "../")

import robot_profile  # Module with network device configurations.

robot_topic_base = robot_profile.ROBOT_TOPIC_BASE



def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """

    if (len(node.get("name"))) == 0: # erro
        print('[b white on red blink] FATAL ERROR [/]: The [bold white]"log name" [/]attribute is [b reverse yellow] EMPTY [/].✋⛔️')
        exit(1)

    if node.text == None: # There is no text to send.
        print("[b white on red blink] FATAL ERROR [/]:[bold] There is [b reverse white] no text [/] to send in the element [b white]<log>[/].✋⛔️")
        exit(1)

    texto = node.text
    
    # Replace variables throughout the text. Variables must exist in memory.
    if "#" in texto:
        var_list = re.findall(r'\#[a-zA-Z]+[a-zA-Z0-9_-]*', texto) # Generate list of occurrences of vars (#...)
        for v in var_list:
            if v[1:] in memory.vars:
                texto = texto.replace(v, str(memory.vars[v[1:]]))
            else:
                # If the variable does not exist in the robot's memory, it displays an error message
                print('[b white on red blink] FATAL ERROR [/]: The variable [b white]"' + v[1:] + '"[/] used in[b white] <log>[/] element, [b yellow reverse] has not been declared [/]. Please, check your code.✋⛔️')
                exit(1)

    # This part replaces the $, or the $-1 or the $1 in the text
    if "$" in texto: # Check if there is $ in the text
        # Checks if var_dollar has any value in the robot's memory
        if (len(memory.var_dolar)) == 0:
            print("[b white on red blink] FATAL ERROR [/]: There are [b yellow reverse] no values [/] for the [b white]$[/] used in the [b white]<log>[/]. Please, check your code.✋⛔️")
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
                        try:
                            texto = texto.replace(var_dollar, memory.var_dolar[-(indice + 1)][0]) 
                        except IndexError:
                            print('[b white on red blink] FATAL ERROR [/]: There was an [b yellow reverse] index error [/] for the variable [b white]"' + var_dollar + '"[/]. Please, check your code.✋⛔️')
                            exit(1) 
                    else: # tipo $n
                        indice = int(var_dollar[1:]) # Var dollar is of type $n. then just take n and convert it to int
                        try:
                            texto = texto.replace(var_dollar, memory.var_dolar[(indice - 1)][0])
                        except IndexError:
                            print('[b white on red blink] FATAL ERROR [/]: There was an [b yellow reverse] index error [/] for the variable [b white]"' + var_dollar + '"[/]. Please, check your code.✋⛔️')
                            exit(1)
                        

    if node.get("name") in memory.log_seq_numbers:
        log_seq_number = memory.log_seq_numbers[node.get("name")] = memory.log_seq_numbers[node.get("name")] + 1
    else:
        log_seq_number = memory.log_seq_numbers[node.get("name")] = 1

    print('[b white ]State[/]:[b white] Sending [/]to the log ([b white]' + node.get("name") + '[/]), with sequence number ' + str(log_seq_number) + ', the text [b white]"' + texto.strip() + '"[/].')

    # O strip é usado para remover os \n dos textos que podem vir do xml.
    client_mqtt.publish(robot_topic_base + "/log", node.get("name") + "_" + str(log_seq_number) + '_' + texto.strip())    
    
    return node # It returns the same node