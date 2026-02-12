from rich import print



def get_var_value(value, memory, client_mqtt):
    # Os valores em var (var_value) só podem ser números, $ (de todos os tipos) e variáveis sem # no início.
    if value[0] == "$": # É do tipo $, $n ou $-n
        if len(memory.var_dolar) == 0: # A memória para $ ainda não tem nenhum elemento e precisa ser reiniciada
            # memory.var_dolar.append(["", ""])
            print('[b white on red blink] FATAL ERROR [/]: The [b white]"' + value +'"[/] variable [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
            exit(1)

        if len(value) == 1: # Is the dollar ($)
            return memory.var_dolar[-1][0]
        else: # May be of type $n or $-n
            if "-" in value: # $-n type
                indice = int(value[2:]) # Var dollar is of type $-n. then just take n and convert it to int
                try:
                    return memory.var_dolar[-(indice + 1)][0] 
                except IndexError:
                    print("[b white on red blink] FATAL ERROR [/]: [b yellow reverse] Unable to access the variable [/][b white] " + value + "[/] with the [b yellow reverse] index [/] used. Please, check your code.✋⛔️")
                    exit(1)
            else: # tipo $n
                indice = int(value[1:]) # Var dollar is of type $n. then just take n and convert it to int
                try:
                    return memory.var_dolar[(indice - 1)][0]
                except IndexError:
                    print("[b white on red blink] FATAL ERROR [/]: [b yellow reverse] Unable to access the variable [/][b white] " + value + "[/] with the [b yellow reverse] index [/] used. Please, check your code.✋⛔️")
                    exit(1)
            
    else: # É uma var definida pelo usuário, mas sem o # no início ou um número.
        # Checks if the operation is different from assignment and checks if var ... DOES NOT exist in memory
        if (value not in memory.vars): # Impede que seja feita uma operação (que não a atribuição) com uma variável que não existe na memória.
            print("[b white on red blink] FATAL ERROR [/]: The variable [b white]" + value + "[/] [b yellow reverse] has not been declared [/]. Please, check your code.✋⛔️")
            exit(1)
        else:
            return memory.vars[value]



def node_processing(node, memory):
    """ Função de tratamento do nó """
    # Por definição, o switch pode conter referências aos "$" e às variáveis.
    # As variaveis são referenciadas pelo nome, sem o uso do "#" no início.

    memory.op_switch = get_var_value(node.get("var"), memory)
    memory.flag_case = False
    print('[b white]State:[/] Processing a [b white]Switch[/]. [b white]Var = "' + node.get("var") + '"[/], with[b white] the string = "' + memory.op_switch + '".')
    
    return node # It returns the same node