from rich import print

from base_command_handler import BaseCommandHandler

class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)    

    def get_var_value(self, value, memory):
        # Values ​​in var (var_value) can only be numbers, $ (of all types) and variables without # at the beginning.
        if value[0] == "$": # Is of type $, $n, or $-n
            if len(memory.var_dolar) == 0: # The memory for $ does not yet have any elements and needs to be reset
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

        else: # It's a user-defined var, but without the leading # or a number.
            # Checks if the operation is different from assignment and checks if var ... DOES NOT exist in memory
            if value[0] == "#": # It is a user-defined var.
                if (value[1:] not in memory.vars): # Checks if the variable has been declared and is in memory.
                    print("[b white on red blink] FATAL ERROR [/]: The variable [b white]" + value + "[/] [b yellow reverse] has not been declared [/]. Please, check your code.✋⛔️")
                    exit(1)
                else: # Variable found.
                    return memory.vars[value[1:]]
            else: # It is a literal value (a string or an integer).
                return value




    def node_process(self, xml_node, memory):
        """ Node handling function """
        
        # Comparisons can be of 3 types: exact, contain and math (with conditional operators).

        # Case 1 (Exact).
        if xml_node.get("op") == "exact":
        # "Exact" comparisons are always string comparisons and are not case sensitive.
            if memory.op_switch.lower() == self.get_var_value(xml_node.get("value"), memory).lower():
                memory.flag_case = True
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = exact)[/]. Comparing[b white] "' + memory.op_switch.lower() + '"[/] with [b white]"' + xml_node.get("value").lower() + '"[/]. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
            else:
                memory.flag_case = False
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = exact)[/]. Comparing[b white] "' + memory.op_switch.lower() + '"[/] with [b white]"' + xml_node.get("value").lower() + '"[/]. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

            return xml_node # It returns the same node
        
        # Case 2 (Contain).
        elif xml_node.get("op") == "contain":
        # This comparison checks whether the string in "value" is contained in the string in "var".
            if self.get_var_value(xml_node.get("value"), memory).lower() in memory.op_switch.lower() :
                memory.flag_case = True
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = contain)[/]. Is the string [b white]"' + xml_node.get("value") + '"[/] [u]contained[/] in the string [b white]"' + memory.op_switch + '"[/] ?. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
            else:
                memory.flag_case = False
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = contain)[/]. Is the string [b white]"' + xml_node.get("value") + '"[/] [u]contained[/] in the string [b white]"' + memory.op_switch + '"[/] ?. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

            return xml_node # It returns the same node
        
        # Case 3 (Math comparison - eq, gt, gte, lt, lte e ne).
        # Mathematical comparison compares the operands considering them as numbers.
        # To do this, they are transformed from strings (as they are stored in the robot's memory) to integers.
        
        # Operator "eq" -> Equality.
        elif xml_node.get("op") == "eq": # Tests whether the value contained in "var" is equal to the value contained in "value".
            value_str = self.get_var_value(xml_node.get("value"), memory)
            if int(memory.op_switch) == int(self.get_var_value(xml_node.get("value"), memory)):
                memory.flag_case = True
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + xml_node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]equal[/] to the value [b white]' + value_str + '[/] ?. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
            else:
                memory.flag_case = False
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + xml_node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]equal[/] to the value [b white]' + value_str + '[/] ?. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

            return xml_node # It returns the same node
        
        # Operator "gt" -> Greater than.
        elif xml_node.get("op") == "gt": # Tests whether the value contained in "var" is greater than the value contained in "value".
            value_str = self.get_var_value(xml_node.get("value"), memory)
            if int(memory.op_switch) > int(self.get_var_value(xml_node.get("value"), memory)):
                memory.flag_case = True
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + xml_node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]greater than[/] the value [b white]' + value_str + '[/] ?. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
            else:
                memory.flag_case = False
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + xml_node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]greater than[/] the value [b white]' + value_str + '[/] ?. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

            return xml_node # It returns the same node
        
        # Operator "gte" -> Greater than or equal to.
        elif xml_node.get("op") == "gte": # Tests whether the value contained in "var" is greater than or equal to the value contained in "value".
            value_str = self.get_var_value(xml_node.get("value"), memory)
            if int(memory.op_switch) >= int(self.get_var_value(xml_node.get("value"), memory)):
                memory.flag_case = True
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + xml_node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]greater than or equal[/] to the value [b white]' + value_str + '[/] ?. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
            else:
                memory.flag_case = False
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + xml_node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]greater than or equal[/] to the value [b white]' + value_str + '[/] ?. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

            return xml_node # It returns the same node
        
        # Operator "lt" -> Less than.
        elif xml_node.get("op") == "lt": # Tests whether the value contained in "var" is less than the value contained in "value".
            value_str = self.get_var_value(xml_node.get("value"), memory)
            if int(memory.op_switch) < int(self.get_var_value(xml_node.get("value"), memory)):
                memory.flag_case = True
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + xml_node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]less than[/] the value [b white]' + value_str + '[/] ?. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
            else:
                memory.flag_case = False
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + xml_node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]less than[/] the value [b white]' + value_str + '[/] ?. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

            return xml_node # It returns the same node
        
        # Operator "lte" -> Less than or equal to.
        elif xml_node.get("op") == "lte": # Tests whether the value contained in "var" is less than or equal to the value contained in "value".
            value_str = self.get_var_value(xml_node.get("value"), memory)
            if int(memory.op_switch) <= int(self.get_var_value(xml_node.get("value"), memory)):
                memory.flag_case = True
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + xml_node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]less than or equal[/] to the value [b white]' + value_str + '[/] ?. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
            else:
                memory.flag_case = False
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + xml_node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]less than or equal[/] to the value [b white]' + value_str + '[/] ?. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

            return xml_node # It returns the same node
        
        # Operator "ne" -> Different from.
        elif xml_node.get("op") == "ne": # Tests whether the value contained in "var" is different from the value contained in "value".
            value_str = self.get_var_value(xml_node.get("value"), memory)
            if int(memory.op_switch) != int(self.get_var_value(xml_node.get("value"), memory)):
                memory.flag_case = True
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + xml_node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]different[/] from the value [b white]' + value_str + '[/] ?. Result: [b reverse green] ' + str(memory.flag_case).upper() + ' [/]')
            else:
                memory.flag_case = False
                print('[b white]State:[/] Executing a [b white]Case[/] [b yellow](type = math(' + xml_node.get("op") + '))[/]. Is the value [b white]' + memory.op_switch + '[/] [u]different[/] from the value [b white]' + value_str + '[/] ?. Result: [b reverse red] ' + str(memory.flag_case).upper() + ' [/]')

            return xml_node # It returns the same node