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
        if value[0] == "#": # É uma var definida pelo usuário.
            if (value[1:] not in memory.vars): # Verifica se a variável foi declarada e está na memória.
                print("[b white on red blink] FATAL ERROR [/]: The variable [b white]" + value + "[/] [b yellow reverse] has not been declared [/]. Please, check your code.✋⛔️")
                exit(1)
            else: # Variável encontrada.
                return memory.vars[value[1:]]
        else: # É valor literal (uma string ou um inteiro).
            return value




def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """
    
    # As comparações podem ser de 3 tipos: exact, contain e math (com operadores condicionais).

    # Caso 1 (Exact).
    if node.get("op") == "exact":
    # As comparações do tipo "exact" são sempre comparações entre strings e não são case sensitive. 
        if memory.op_switch.lower() == get_var_value(node.get("value"), memory):
            memory.flag_case = True
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = exact)[/]. Comparing[b white] "' + memory.op_switch + '"[/] with [b white]"' + node.get("value") + '"[/]. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
        else:
            memory.flag_case = False
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = exact)[/]. Comparing[b white] "' + memory.op_switch + '"[/] with [b white]"' + node.get("value") + '"[/]. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

        return node # It returns the same node
    
    # Caso 2 (Contain).
    elif node.get("op") == "contain":
    # Essa comparação verifica se a sting em "value" está contida na string em "var".
        if get_var_value(node.get("value"), memory) in memory.op_switch.lower() :
            memory.flag_case = True
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = contain)[/]. Is the string [b white]"' + node.get("value") + '"[/] [u]contained[/] in the string [b white]"' + memory.op_switch + '"[/] ?. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
        else:
            memory.flag_case = False
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = contain)[/]. Is the string [b white]"' + node.get("value") + '"[/] [u]contained[/] in the string [b white]"' + memory.op_switch + '"[/] ?. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

        return node # It returns the same node
    
    # Caso 3 (Math comparison - eq, gt, gte, lt, lte e ne).
    # A comparação matemática compara os operandos considerando-os como números. Para isso, eles são transformados de string (como são aamzenados na memória do robô) para inteiro.
    
    # Operador "eq" -> Igualdade.
    elif node.get("op") == "eq": # Testa se o valor contido em "var" é igual ao valor contido em "value".
        value_str = get_var_value(node.get("value"), memory)
        if int(memory.op_switch) == int(get_var_value(node.get("value"), memory)):
            memory.flag_case = True
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]equal[/] to the value [b white]' + value_str + '[/] ?. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
        else:
            memory.flag_case = False
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]equal[/] to the value [b white]' + value_str + '[/] ?. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

        return node # It returns the same node
    
    # Operador "gt" -> Maior que.
    elif node.get("op") == "gt": # Testa se o valor contido em "var" é maior que valor contido em "value".
        value_str = get_var_value(node.get("value"), memory)
        if int(memory.op_switch) > int(get_var_value(node.get("value"), memory)):
            memory.flag_case = True
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]greater than[/] the value [b white]' + value_str + '[/] ?. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
        else:
            memory.flag_case = False
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]greater than[/] the value [b white]' + value_str + '[/] ?. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

        return node # It returns the same node
    
    # Operador "gte" -> Maior ou igual a.
    elif node.get("op") == "gte": # Testa se o valor contido em "var" é maior ou igual ao valor contido em "value".
        value_str = get_var_value(node.get("value"), memory)
        if int(memory.op_switch) >= int(get_var_value(node.get("value"), memory)):
            memory.flag_case = True
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]greater than or equal[/] to the value [b white]' + value_str + '[/] ?. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
        else:
            memory.flag_case = False
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]greater than or equal[/] to the value [b white]' + value_str + '[/] ?. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

        return node # It returns the same node
    
    # Operador "lt" -> Menor que.
    elif node.get("op") == "lt": # Testa se o valor contido em "var" é menor que valor contido em "value".
        value_str = get_var_value(node.get("value"), memory)
        if int(memory.op_switch) < int(get_var_value(node.get("value"), memory)):
            memory.flag_case = True
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]less than[/] the value [b white]' + value_str + '[/] ?. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
        else:
            memory.flag_case = False
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]less than[/] the value [b white]' + value_str + '[/] ?. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

        return node # It returns the same node
    
    # Operador "lte" -> Menor ou igual a.
    elif node.get("op") == "lte": # Testa se o valor contido em "var" é menor ou igual ao valor contido em "value".
        value_str = get_var_value(node.get("value"), memory)
        if int(memory.op_switch) <= int(get_var_value(node.get("value"), memory)):
            memory.flag_case = True
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]less than or equal[/] to the value [b white]' + value_str + '[/] ?. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
        else:
            memory.flag_case = False
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]less than or equal[/] to the value [b white]' + value_str + '[/] ?. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

        return node # It returns the same node
    
    # Operador "ne" -> Diferente de.
    elif node.get("op") == "ne": # Testa se o valor contido em "var" é diferente do valor contido em "value".
        value_str = get_var_value(node.get("value"), memory)
        if int(memory.op_switch) != int(get_var_value(node.get("value"), memory)):
            memory.flag_case = True
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]different[/] from the value [b white]' + value_str + '[/] ?. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
        else:
            memory.flag_case = False
            print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]different[/] from the value [b white]' + value_str + '[/] ?. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

        return node # It returns the same node