from rich import print

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)
        
    def get_var_ref(self, var, memory):
        if var[0] == "$": # Is of type $, $n, or $-n
            if len(memory.var_dollar) == 0: # The memory for $ does not yet contain any elements. The program will exit.
                print('[b white on red blink] FATAL ERROR [/]: The [b white]"' + var +'"[/] variable [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
                exit(1)

            if len(var) == 1: # Is the dollar ($)
                return memory.var_dollar[-1]
            else: # May be of type $n or $-n
                if "-" in var: # $-n type
                    indice = int(var[2:]) # Var dollar is of type $-n. then just take n and convert it to int
                    try:
                        return memory.var_dollar[-(indice + 1)] 
                    except IndexError:
                        print("[b white on red blink] FATAL ERROR [/]: [b yellow reverse] Unable to access the variable [/][b white] " + var + "[/] with the [b yellow reverse] index [/] used. Please, check your code.✋⛔️")
                        exit(1)
                else: # $n type
                    indice = int(var[1:]) # Var dollar is of type $n. then just take n and convert it to int
                    try:
                        return memory.var_dollar[(indice - 1)]
                    except IndexError:
                        print("[b white on red blink] FATAL ERROR [/]: [b yellow reverse] Unable to access the variable [/][b white] " + var + "[/] with the [b yellow reverse] index [/] used. Please, check your code.✋⛔️")
                        exit(1)
        else: # It is a user-defined variable
            # Checks if the variable already exists.
            if (var not in memory.vars):
                return None # This value will be checked when processing the operation.
            else:
                return var # Returns the var name itself (which is the key) and is the reference to the value in the variables dictionary.


    def get_var_value(self, value, memory):
        # Values ​​in var (var_value) can only be numbers, $ (of all types) and variables without # at the beginning.
        if value[0] == "$": # Is of type $, $n, or $-n
            if len(memory.var_dollar) == 0: # The memory for $ does not yet have any elements and needs to be reset
                print('[b white on red blink] FATAL ERROR [/]: The [b white]"' + value +'"[/] variable [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
                exit(1)

            if len(value) == 1: # Is the dollar ($)
                var_aux = memory.var_dollar[-1][0]
            else: # May be of type $n or $-n
                if "-" in value: # $-n type
                    indice = int(value[2:]) # Var dollar is of type $-n. then just take n and convert it to int
                    try:
                        return  memory.var_dollar[-(indice + 1)][0]
                    except IndexError:
                        print("[b white on red blink] FATAL ERROR [/]: [b yellow reverse] Unable to access the variable [/][b white] " + var + "[/] with the [b yellow reverse] index [/] used. Please, check your code.✋⛔️")
                        exit(1)
                    
                else: # tipo $n
                    indice = int(value[1:]) # Var dollar is of type $n. then just take n and convert it to int
                    try:
                        return  memory.var_dollar[(indice - 1)][0]
                    except IndexError:
                        print("[b white on red blink] FATAL ERROR [/]: [b yellow reverse] Unable to access the variable [/][b white] " + var + "[/] with the [b yellow reverse] index [/] used. Please, check your code.✋⛔️")
                        exit(1)
            
            try: # Tests if it is a number.
                int(var_aux)
                return var_aux
            except:
                print('[b white on red blink] FATAL ERROR [/]: You used a [b yellow reverse] string "' + var_aux + '" [/] as [b white]op2[/] of a [b pink]<counter>[/]. Please, check your code.✋⛔️')
                exit(1)

        else: # It's a user-defined var, but without the leading # or a number.
            # Checks if the operation is different from assignment and checks if var ... DOES NOT exist in memory
            if (value not in memory.vars): # Prevents an operation (other than assignment) from being performed on a variable that does not exist in memory.
                try: # Tests if it is a number.
                    int(value) # Test.
                    return value
                except:
                    print("[b white on red blink] FATAL ERROR [/]: The variable [b white]" + value + "[/] [b yellow reverse] has not been declared [/]. Please, check your code.✋⛔️")
                    exit(1)
            else:
                try: # Tests if it is a number.
                    int(memory.vars[value])
                    return memory.vars[value]
                except:
                    print('[b white on red blink] FATAL ERROR [/]: You used a [b yellow reverse] string "' + memory.vars[value] + '" [/] as [b white]op2[/] of a [b pink]<counter>[/]. Please, check your code.✋⛔️')
                    exit(1)
            
        
    def node_process(self, xml_node, memory):
        """ Função de tratamento do nó """
        # Get the operator.
        self.op= xml_node.get("op")

        # Gets the variable reference in the robot's memory. It can be a list (from a $) or a string (the variable's key in memory).
        # A list, because each element of $ has a value and a source (a listen, a qrread, etc.).
        self.var_ref= self.get_var_ref(xml_node.get("var"), memory)

        # Values ​​can be numbers and references to $, $n, $-n, and #some_var.
        self.var_value = self.get_var_value(xml_node.get("value") , memory) 
        

        # Start processing operations.
        if self.op== "=": # Perform the assignment
            if isinstance(self.var_ref, list): # If it's a list, then it's a reference to a $ type.
                self.var_ref[0] = self.var_value
                self.var_ref[1] = "<counter>" # Updates the source of the $ variable, which becomes the <counter>
                print('[b white]State:[/] [b white]Assigning[/] the value [b white]' + self.var_ref[0] + '[/] to the variable [b white]' + xml_node.get("var") + "[/].")
            else: # It is a string that represents the key to the user variables dictionary.
                memory.vars[xml_node.get("var")] = self.var_value
                print('[b white]State:[/] [b white]Assigning[/] the value [b white]' + str(self.var_value) + '[/] to the variable [b white]' + xml_node.get("var") + "[/].")

        elif self.op== "+": # Perform the addition
            if isinstance(self.var_ref, list): # If it is a list, then it is a reference to a type of $.
                op1 = int(self.var_ref[0])
                op2 = self.var_value
                self.var_ref[0] = str(op1 + op2)
                self.var_ref[1] = "<counter>" # Update the source of the $ variable
                print('[b white]State:[/] [b white]Adding[/] the [b white]op1(' + xml_node.get("var") + ')=' + str(op1) + '[/] and [b white]op2(' + xml_node.get("value")  + ')=' + str(self.var_value) + '[/]. [b white]The result is ' + self.var_ref[0] + '[/].')
            else: # It is a string that represents the key to the user variables dictionary.
                if self.var_ref== None: # Variável não inicializada, o programa pára.
                    print('[b white on red blink] FATAL ERROR [/]: The variable[b white] "' + xml_node.get("var") + '"[/] [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
                    exit(1)
                aux = memory.vars[self.var_ref]
                memory.vars[self.var_ref] = str(int(memory.vars[self.var_ref]) + int(self.var_value))
                print('[b white]State:[/] [b white]Adding[/] the [b white]op1(' + xml_node.get("var") + ')=' + str(aux) + '[/] and [b white]op2(' + xml_node.get("value")  + ')=' + str(self.var_value) + '[/]. [b white]The result is ' + str(memory.vars[self.var_ref]) + '[/].')
                
        elif self.op== "-": # Perform the addition
            if isinstance(self.var_ref, list): # If it is a list, then it is a reference to a type of $.
                op1 = int(self.var_ref[0])
                op2 = self.var_value
                self.var_ref[0] = str(op1 - op2)
                self.var_ref[1] = "<counter>" # Update the source of the $ variable
                print('[b white]State:[/] [b white]Subtracting[/] the [b white]op1(' + xml_node.get("var") + ')=' + str(op1) + '[/] and [b white]op2(' + xml_node.get("value")  + ')=' + str(self.var_value) + '[/]. [b white]The result is ' + self.var_ref[0] + '[/].')
            else: # It is a string that represents the key to the user variables dictionary.
                if self.var_ref== None: # Variable not initialized, program stops.
                    print('[b white on red blink] FATAL ERROR [/]: The variable[b white] "' + xml_node.get("var") + '"[/] [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
                    exit(1)
                aux = memory.vars[self.var_ref]
                memory.vars[self.var_ref] = str(int(memory.vars[self.var_ref]) - int(self.var_value))
                print('[b white]State:[/] [b white]Adding[/] the [b white]op1(' + xml_node.get("var") + ')=' + str(aux) + '[/] and [b white]op2(' + xml_node.get("value")  + ')=' + str(self.var_value) + '[/]. [b white]The result is ' + str(memory.vars[self.var_ref]) + '[/].')
                
        elif self.op== "*": # Perform the product
            if isinstance(self.var_ref, list): # If it is a list, then it is a reference to a type of $.
                op1 = int(self.var_ref[0])
                op2 = self.var_value
                self.var_ref[0] = str(op1 * op2)
                self.var_ref[1] = "<counter>" # Update the source of the $ variable
                print('[b white]State:[/] [b white]Multiplying[/] the [b white]op1(' + xml_node.get("var") + ')=' + str(op1) + '[/] and [b white]op2(' + xml_node.get("value")  + ')=' + str(self.var_value) + '[/]. [b white]The result is ' + self.var_ref[0] + '[/].')
            else: # It is a string that represents the key to the user variables dictionary.
                if self.var_ref== None: # Variable not initialized, program stops.
                    print('[b white on red blink] FATAL ERROR [/]: The variable[b white] "' + xml_node.get("var") + '"[/] [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
                    exit(1)
                aux = memory.vars[self.var_ref]
                memory.vars[self.var_ref] = str(int(memory.vars[self.var_ref]) * int(self.var_value))
                print('[b white]State:[/] [b white]Multiplying[/] the [b white]op1(' + xml_node.get("var") + ')=' + str(aux) + '[/] and [b white]op2(' + xml_node.get("value")  + ')=' + str(self.var_value) + '[/]. [b white]The result is ' + str(memory.vars[self.var_ref]) + '[/].')

        elif self.op== "/": # Performs the division (it was /=) but I changed it to //= (integer division)
            if isinstance(self.var_ref, list): # If it is a list, then it is a reference to a type of $.
                op1 = int(self.var_ref[0])
                op2 = self.var_value
                self.var_ref[0] = str(op1 // op2)
                self.var_ref[1] = "<counter>" # Update the source of the $ variable
                print('[b white]State:[/] [b white]Dividing[/] the [b white]op1(' + xml_node.get("var") + ')=' + str(op1) + '[/] and [b white]op2(' + xml_node.get("value")  + ')=' + str(self.var_value) + '[/]. [b white]The result is ' + self.var_ref[0] + '[/].')
            else: # It is a string that represents the key to the user variables dictionary.
                if self.var_ref== None: # Variable not initialized, program stops.
                    print('[b white on red blink] FATAL ERROR [/]: The variable[b white] "' + xml_node.get("var") + '"[/] [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
                    exit(1)
                aux = memory.vars[self.var_ref]
                memory.vars[self.var_ref] = str(int(memory.vars[self.var_ref]) // int(self.var_value))
                print('[b white]State:[/] [b white]Dividing[/] the [b white]op1(' + xml_node.get("var") + ')=' + str(aux) + '[/] and [b white]op2(' + xml_node.get("value")  + ')=' + str(self.var_value) + '[/]. [b white]The result is ' + str(memory.vars[self.var_ref]) + '[/].')

        elif self.op== "^": # Calculating op1 to the power of op2.
            if isinstance(self.var_ref, list): # If it is a list, then it is a reference to a type of $.
                op1 = int(self.var_ref[0])
                op2 = self.var_value
                self.var_ref[0] = str(op1 ** op2)
                self.var_ref[1] = "<counter>" # Update the source of the $ variable
                print('[b white]State:[/] [b white]Calculating op1(' + xml_node.get("var") + ')=' + str(op1) + ' [/] to the [b white]power[/] of [b white]op2(' + xml_node.get("value")  + ')=' + str(self.var_value) + '[/]. [b white]The result is ' + self.var_ref[0] + '[/].')
            else: # It is a string that represents the key to the user variables dictionary.
                if self.var_ref== None: # Variável não inicializada, o programa pára.
                    print('[b white on red blink] FATAL ERROR [/]: The variable[b white] "' + xml_node.get("var") + '"[/] [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
                    exit(1)
                aux = memory.vars[self.var_ref]
                memory.vars[self.var_ref] = str(int(memory.vars[self.var_ref]) ** int(self.var_value))
                print('[b white]State:[/] [b white]Calculating op1(' + xml_node.get("var") + ')=' + str(aux) + ' [/]to the [b white]power[/] of [b white]op2(' + xml_node.get("value")  + ')=' + str(self.var_value) + '[/]. [b white]The result is ' + str(memory.vars[self.var_ref]) + '[/].')

        elif self.op== "%": # Calculate the module
            if isinstance(self.var_ref, list): # If it is a list, then it is a reference to a type of $.
                op1 = int(self.var_ref[0])
                op2 = self.var_value
                self.var_ref[0] = str(op1 % op2)
                self.var_ref[1] = "<counter>" # Update the source of the $ variable
                print('[b white]State:[/] [b white]Calculating the modulus of division between[/] the [b white]op1(' + xml_node.get("var") + ')=' + str(op1) + '[/] and [b white]op2(' + xml_node.get("value")  + ')=' + str(self.var_value) + '[/]. [b white]The result is ' + self.var_ref[0] + '[/].')
            else: # It is a string that represents the key to the user variables dictionary.
                if self.var_ref== None: # Variable not initialized, program stops.
                    print('[b white on red blink] FATAL ERROR [/]: The variable[b white] "' + xml_node.get("var") + '"[/] [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
                    exit(1)
                aux = memory.vars[self.var_ref]
                memory.vars[self.var_ref] = str(int(memory.vars[self.var_ref]) % int(self.var_value))
                print('[b white]State:[/] [b white]Calculating the modulus of division between[/] the [b white]op1(' + xml_node.get("var") + ')=' + str(aux) + '[/] and [b white]op2(' + xml_node.get("value")  + ')=' + str(self.var_value) + '[/]. [b white]The result is ' + str(memory.vars[self.var_ref]) + '[/].')
                

        return xml_node # It returns the same nodenode