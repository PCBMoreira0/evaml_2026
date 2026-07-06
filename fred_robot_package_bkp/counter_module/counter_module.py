from rich import print



def get_var_ref(var, memory):
    if var[0] == "$": # É do tipo $, $n ou $-n
        if len(memory.var_dolar) == 0: # A memória para $ ainda não tem nenhum elemento. O programa será encerrado.
            print('[b white on red blink] FATAL ERROR [/]: The [b white]"' + var +'"[/] variable [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
            exit(1)

        if len(var) == 1: # Is the dollar ($)
            return memory.var_dolar[-1]
        else: # May be of type $n or $-n
            if "-" in var: # $-n type
                indice = int(var[2:]) # Var dollar is of type $-n. then just take n and convert it to int
                try:
                    return memory.var_dolar[-(indice + 1)] 
                except IndexError:
                    print("[b white on red blink] FATAL ERROR [/]: [b yellow reverse] Unable to access the variable [/][b white] " + var + "[/] with the [b yellow reverse] index [/] used. Please, check your code.✋⛔️")
                    exit(1)
            else: # tipo $n
                indice = int(var[1:]) # Var dollar is of type $n. then just take n and convert it to int
                try:
                    return memory.var_dolar[(indice - 1)]
                except IndexError:
                    print("[b white on red blink] FATAL ERROR [/]: [b yellow reverse] Unable to access the variable [/][b white] " + var + "[/] with the [b yellow reverse] index [/] used. Please, check your code.✋⛔️")
                    exit(1)
    else: # É uma variável definida pelo usuário
        # Verifica se a variável já existe.
        if (var not in memory.vars):
            return None # Esse valor será verificado no momento do processamento da operação.
        else:
            return var # Retorna o próprio nome da var (que é a chave) e é a referência para o valor no dicionário de variáveis.


def get_var_value(value, memory):
    # Os valores em var (var_value) só podem ser números, $ (de todos os tipos) e variáveis sem # no início.
    if value[0] == "$": # É do tipo $, $n ou $-n
        if len(memory.var_dolar) == 0: # A memória para $ ainda não tem nenhum elemento e precisa ser reiniciada
            # memory.var_dolar.append(["", ""])
            print('[b white on red blink] FATAL ERROR [/]: The [b white]"' + value +'"[/] variable [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
            exit(1)

        if len(value) == 1: # Is the dollar ($)
            var_aux = memory.var_dolar[-1][0]
        else: # May be of type $n or $-n
            if "-" in value: # $-n type
                indice = int(value[2:]) # Var dollar is of type $-n. then just take n and convert it to int
                try:
                    return  memory.var_dolar[-(indice + 1)][0]
                except IndexError:
                    print("[b white on red blink] FATAL ERROR [/]: [b yellow reverse] Unable to access the variable [/][b white] " + var + "[/] with the [b yellow reverse] index [/] used. Please, check your code.✋⛔️")
                    exit(1)
                
            else: # tipo $n
                indice = int(value[1:]) # Var dollar is of type $n. then just take n and convert it to int
                try:
                    return  memory.var_dolar[(indice - 1)][0]
                except IndexError:
                    print("[b white on red blink] FATAL ERROR [/]: [b yellow reverse] Unable to access the variable [/][b white] " + var + "[/] with the [b yellow reverse] index [/] used. Please, check your code.✋⛔️")
                    exit(1)
        
        try: # Testa se é um número.
            int(var_aux)
            return var_aux
        except:
            print('[b white on red blink] FATAL ERROR [/]: You used a [b yellow reverse] string "' + var_aux + '" [/] as [b white]op2[/] of a [b pink]<counter>[/]. Please, check your code.✋⛔️')
            exit(1)

    else: # É uma var definida pelo usuário, mas sem o # no início ou um número.
        # Checks if the operation is different from assignment and checks if var ... DOES NOT exist in memory
        if (value not in memory.vars): # Impede que seja feita uma operação (que não a atribuição) com uma variável que não existe na memória.
            try: # Testa se é um número.
                int(value) # Testa.
                return value
            except:
                print("[b white on red blink] FATAL ERROR [/]: The variable [b white]" + value + "[/] [b yellow reverse] has not been declared [/]. Please, check your code.✋⛔️")
                exit(1)
        else:
            try: # Testa se é um número.
                int(memory.vars[value])
                return memory.vars[value]
            except:
                print('[b white on red blink] FATAL ERROR [/]: You used a [b yellow reverse] string "' + memory.vars[value] + '" [/] as [b white]op2[/] of a [b pink]<counter>[/]. Please, check your code.✋⛔️')
                exit(1)
        
    
def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """

    # Pega o operador.
    op = node.get("op")

    # Pega a referência da variável na memória do robô. Ela pode ser uma lista (vinda de um $) ou uma string (chave da variável na memória).
    # Uma lista, porque cada elemento de $ tem um valor e uma fonte de origem (um listen, um qrread etc).
    var_ref = get_var_ref(node.get("var"), memory)

    # Os valores podem ser números e referências a $, $n, $-n e #some_var.
    var_value = get_var_value(node.get("value") , memory) 

    # Começa o processamento das operações.
    if op == "=": # Perform the assignment
        if isinstance(var_ref, list): # Se é uma lista, então é uma referência a um tipo de $.
            var_ref[0] = var_value
            var_ref[1] = "<counter>" # Atualiza a fonte da variável $, que passa a ser o <counter>
            print('[b white]State:[/] [b white]Assigning[/] the value [b white]' + var_ref[0] + '[/] to the variable [b white]' + node.get("var") + "[/].")
        else: # É uma string que representa a chave para o dicionário de variáveis do usuário.
            memory.vars[node.get("var")] = var_value
            print('[b white]State:[/] [b white]Assigning[/] the value [b white]' + str(var_value) + '[/] to the variable [b white]' + node.get("var") + "[/].")

    elif op == "+": # Perform the addition
        if isinstance(var_ref, list): # Se é uma lista, então é uma referência a um tipo de $.
            op1 = int(var_ref[0])
            op2 = var_value
            var_ref[0] = str(op1 + op2)
            var_ref[1] = "<counter>" # Atualiza a fonte da variável $
            print('[b white]State:[/] [b white]Adding[/] the [b white]op1(' + node.get("var") + ')=' + str(op1) + '[/] and [b white]op2(' + node.get("value")  + ')=' + str(var_value) + '[/]. [b white]The result is ' + var_ref[0] + '[/].')
        else: # É uma string que representa a chave para o dicionário de variáveis do usuário.
            if var_ref == None: # Variável não inicializada, o programa pára.
                print('[b white on red blink] FATAL ERROR [/]: The variable[b white] "' + node.get("var") + '"[/] [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
                exit(1)
            aux = memory.vars[var_ref]
            memory.vars[var_ref] = str(int(memory.vars[var_ref]) + int(var_value))
            print('[b white]State:[/] [b white]Adding[/] the [b white]op1(' + node.get("var") + ')=' + str(aux) + '[/] and [b white]op2(' + node.get("value")  + ')=' + str(var_value) + '[/]. [b white]The result is ' + str(memory.vars[var_ref]) + '[/].')
            
    elif op == "-": # Perform the addition
        if isinstance(var_ref, list): # Se é uma lista, então é uma referência a um tipo de $.
            op1 = int(var_ref[0])
            op2 = var_value
            var_ref[0] = str(op1 - op2)
            var_ref[1] = "<counter>" # Atualiza a fonte da variável $
            print('[b white]State:[/] [b white]Subtracting[/] the [b white]op1(' + node.get("var") + ')=' + str(op1) + '[/] and [b white]op2(' + node.get("value")  + ')=' + str(var_value) + '[/]. [b white]The result is ' + var_ref[0] + '[/].')
        else: # É uma string que representa a chave para o dicionário de variáveis do usuário.
            if var_ref == None: # Variável não inicializada, o programa pára.
                print('[b white on red blink] FATAL ERROR [/]: The variable[b white] "' + node.get("var") + '"[/] [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
                exit(1)
            aux = memory.vars[var_ref]
            memory.vars[var_ref] = str(int(memory.vars[var_ref]) - int(var_value))
            print('[b white]State:[/] [b white]Adding[/] the [b white]op1(' + node.get("var") + ')=' + str(aux) + '[/] and [b white]op2(' + node.get("value")  + ')=' + str(var_value) + '[/]. [b white]The result is ' + str(memory.vars[var_ref]) + '[/].')
            
    elif op == "*": # Perform the product
        if isinstance(var_ref, list): # Se é uma lista, então é uma referência a um tipo de $.
            op1 = int(var_ref[0])
            op2 = var_value
            var_ref[0] = str(op1 * op2)
            var_ref[1] = "<counter>" # Atualiza a fonte da variável $
            print('[b white]State:[/] [b white]Multiplying[/] the [b white]op1(' + node.get("var") + ')=' + str(op1) + '[/] and [b white]op2(' + node.get("value")  + ')=' + str(var_value) + '[/]. [b white]The result is ' + var_ref[0] + '[/].')
        else: # É uma string que representa a chave para o dicionário de variáveis do usuário.
            if var_ref == None: # Variável não inicializada, o programa pára.
                print('[b white on red blink] FATAL ERROR [/]: The variable[b white] "' + node.get("var") + '"[/] [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
                exit(1)
            aux = memory.vars[var_ref]
            memory.vars[var_ref] = str(int(memory.vars[var_ref]) * int(var_value))
            print('[b white]State:[/] [b white]Multiplying[/] the [b white]op1(' + node.get("var") + ')=' + str(aux) + '[/] and [b white]op2(' + node.get("value")  + ')=' + str(var_value) + '[/]. [b white]The result is ' + str(memory.vars[var_ref]) + '[/].')

    elif op == "/": # Performs the division (it was /=) but I changed it to //= (integer division)
        if isinstance(var_ref, list): # Se é uma lista, então é uma referência a um tipo de $.
            op1 = int(var_ref[0])
            op2 = var_value
            var_ref[0] = str(op1 // op2)
            var_ref[1] = "<counter>" # Atualiza a fonte da variável $
            print('[b white]State:[/] [b white]Dividing[/] the [b white]op1(' + node.get("var") + ')=' + str(op1) + '[/] and [b white]op2(' + node.get("value")  + ')=' + str(var_value) + '[/]. [b white]The result is ' + var_ref[0] + '[/].')
        else: # É uma string que representa a chave para o dicionário de variáveis do usuário.
            if var_ref == None: # Variável não inicializada, o programa pára.
                print('[b white on red blink] FATAL ERROR [/]: The variable[b white] "' + node.get("var") + '"[/] [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
                exit(1)
            aux = memory.vars[var_ref]
            memory.vars[var_ref] = str(int(memory.vars[var_ref]) // int(var_value))
            print('[b white]State:[/] [b white]Dividing[/] the [b white]op1(' + node.get("var") + ')=' + str(aux) + '[/] and [b white]op2(' + node.get("value")  + ')=' + str(var_value) + '[/]. [b white]The result is ' + str(memory.vars[var_ref]) + '[/].')

    elif op == "^": # Calculating op1 to the power of op2.
        if isinstance(var_ref, list): # Se é uma lista, então é uma referência a um tipo de $.
            op1 = int(var_ref[0])
            op2 = var_value
            var_ref[0] = str(op1 ** op2)
            var_ref[1] = "<counter>" # Atualiza a fonte da variável $
            print('[b white]State:[/] [b white]Calculating op1(' + node.get("var") + ')=' + str(op1) + ' [/] to the [b white]power[/] of [b white]op2(' + node.get("value")  + ')=' + str(var_value) + '[/]. [b white]The result is ' + var_ref[0] + '[/].')
        else: # É uma string que representa a chave para o dicionário de variáveis do usuário.
            if var_ref == None: # Variável não inicializada, o programa pára.
                print('[b white on red blink] FATAL ERROR [/]: The variable[b white] "' + node.get("var") + '"[/] [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
                exit(1)
            aux = memory.vars[var_ref]
            memory.vars[var_ref] = str(int(memory.vars[var_ref]) ** int(var_value))
            print('[b white]State:[/] [b white]Calculating op1(' + node.get("var") + ')=' + str(aux) + ' [/]to the [b white]power[/] of [b white]op2(' + node.get("value")  + ')=' + str(var_value) + '[/]. [b white]The result is ' + str(memory.vars[var_ref]) + '[/].')

    elif op == "%": # Calculate the module
        if isinstance(var_ref, list): # Se é uma lista, então é uma referência a um tipo de $.
            op1 = int(var_ref[0])
            op2 = var_value
            var_ref[0] = str(op1 % op2)
            var_ref[1] = "<counter>" # Atualiza a fonte da variável $
            print('[b white]State:[/] [b white]Calculating the modulus of division between[/] the [b white]op1(' + node.get("var") + ')=' + str(op1) + '[/] and [b white]op2(' + node.get("value")  + ')=' + str(var_value) + '[/]. [b white]The result is ' + var_ref[0] + '[/].')
        else: # É uma string que representa a chave para o dicionário de variáveis do usuário.
            if var_ref == None: # Variável não inicializada, o programa pára.
                print('[b white on red blink] FATAL ERROR [/]: The variable[b white] "' + node.get("var") + '"[/] [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
                exit(1)
            aux = memory.vars[var_ref]
            memory.vars[var_ref] = str(int(memory.vars[var_ref]) % int(var_value))
            print('[b white]State:[/] [b white]Calculating the modulus of division between[/] the [b white]op1(' + node.get("var") + ')=' + str(aux) + '[/] and [b white]op2(' + node.get("value")  + ')=' + str(var_value) + '[/]. [b white]The result is ' + str(memory.vars[var_ref]) + '[/].')
            

    return node # It returns the same node