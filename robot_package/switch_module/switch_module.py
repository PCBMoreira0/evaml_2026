from rich import print

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)
        
    def get_var_value(self, value, memory):
        # Values ​​in var (var_value) can only be numbers, $ (of all types) and variables without # at the beginning.
        if value[0] == "$": # Is of type $, $n, or $-n
            if len(memory.var_dollar) == 0: # The memory for $ does not yet have any elements and needs to be reset
                print('[b white on red blink] FATAL ERROR [/]: The [b white]"' + value +'"[/] variable [b reverse yellow] was not initialized [/]. Please, check your code.✋⛔️')
                exit(1)

            if len(value) == 1: # Is the dollar ($)
                return memory.var_dollar[-1][0]
            else: # May be of type $n or $-n
                if "-" in value: # $-n type
                    indice = int(value[2:]) # Var dollar is of type $-n. then just take n and convert it to int
                    try:
                        return memory.var_dollar[-(indice + 1)][0] 
                    except IndexError:
                        print("[b white on red blink] FATAL ERROR [/]: [b yellow reverse] Unable to access the variable [/][b white] " + value + "[/] with the [b yellow reverse] index [/] used. Please, check your code.✋⛔️")
                        exit(1)
                else: # tipo $n
                    indice = int(value[1:]) # Var dollar is of type $n. then just take n and convert it to int
                    try:
                        return memory.var_dollar[(indice - 1)][0]
                    except IndexError:
                        print("[b white on red blink] FATAL ERROR [/]: [b yellow reverse] Unable to access the variable [/][b white] " + value + "[/] with the [b yellow reverse] index [/] used. Please, check your code.✋⛔️")
                        exit(1)
                
        else: # It's a user-defined var, but without the leading # or a number.
            # Checks if the operation is different from assignment and checks if var ... DOES NOT exist in memory
            if (value not in memory.vars): # Prevents an operation (other than assignment) from being performed on a variable that does not exist in memory.
                print("[b white on red blink] FATAL ERROR [/]: The variable [b white]" + value + "[/] [b yellow reverse] has not been declared [/]. Please, check your code.✋⛔️")
                exit(1)
            else:
                return memory.vars[value]



    def node_process(self, xml_node, memory):
        """ Função de tratamento do nó """
        # By definition, the switch can contain references to "$" and variables.
        # Variables are referenced by name, without the use of a "#" at the beginning.

        memory.op_switch = self.get_var_value(xml_node.get("var"), memory)
        memory.flag_case = False
        print('[b white]State:[/] Processing a [b white]Switch[/]. [b white]Var = "' + xml_node.get("var") + '"[/], with[b white] the string = "' + memory.op_switch + '".')
        
        return xml_node # It returns the same node