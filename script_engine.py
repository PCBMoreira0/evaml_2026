import sys
import os
import time

from rich import print
from rich.console import Console

from lxml import etree as ET

# Utilities Classes
from module_loader import ModuleLoader
from script_metadata import ScriptMetadata

import config

# Robot Memory Class
from robot_memory import RobotMemory

sys.path.append(os.getcwd() + "/" + "robot_package/")

import robot_profile

console = Console()



class ScriptEngine:
    def __init__(self):
        # Player Object states:
        # "EMPTY" - The object has been created and no script has been loaded into memory.
        # "NOT_INIT" - The object has already read the script but needs to be initialized. During initialization, modules are loaded and the ID table is generated.
        # "IDLE" - The script_player object has already been initialized and is ready to execute a script from scratch, or the player has finished executing a script.
        # "PLAY" - In this state, the player is executing a script.
        # "BLOCKED" - The player is blocked, waiting for a module, such as talk, to finish processing.

        self.__state = "EMPTY"
        self.__robot_memory = RobotMemory() # Cria o objeto de memória do "robô"
        self.__root = None # Elemento root do arquivo XML
        self.__moduleloader = ModuleLoader()
        self.__scriptmetadata = ScriptMetadata()

    # get the player state
    def get_state(self):
        return self.__state 

    # Load a script file
    def load_script(self, script_file):
        self.script_file  = script_file
        
        try:
            tree = ET.parse(self.script_file)  # XML code file
        except:
            print("[b blink reverse red] We have a problem... I can't find the file: " + script_file + "[/]")
            return False
        
        self.__root = tree.getroot() # script root node
        self.__state  = "NOT_INIT"

        return True
        


    # Run before play to position the start of the XML
    def initialize(self, verbose_mode=True):
        if self.__state != "NOT_INIT":
            if self.__state == "EMPTY":
                print("O Player se encontra no estado EMPTY e não pode ser inicializado. Primeiro, carregue um script!")
                return False # Initialization did not occur
            else:
                print("O Player já foi inicializado e se encontra no estado " + self.__state + ".")
                return False # Initialization did not occur
        
        self.__robot_memory = RobotMemory() # Resets the "robot" memory
        
        # Loading commands modules
        # # Contains the association between the element names and their classes (CommandHandlers).
        # The key is the element tag and the value is a list with two elements:
        # 1) The number of occurrences of the element in the script.
        # 2) The instance of the class from the imported module.
        self.tab_modules = self.__moduleloader.import_modules(self.__root, verbose_mode) # Load modules dynamically
        # This table must contain all elements with "id", that is, those that can be called by a <goto> or by a <useMacro>.
        self.__robot_memory.set_tab_ids(self.__scriptmetadata.identify_targets(self.__root, verbose_mode)) # Identify scrpit elements
        self.settings_node = self.__root.find("settings")
        self.script_node = self.__root.find("script")
        self.__state = "IDLE"
        return True # All is ok!
        


    def start_script(self, running_mode="terminal"):
        if self.__state != "IDLE":
            print("O Player não se encontra no estado IDLE.")
            return False

        console.rule("🤖 [yellow reverse b]  Starting the script in " + running_mode.upper() + " MODE - Reading the global <settings> from file: " + self.script_file + "  [/] 🤖\n")
        self.__robot_memory.reset_memory()
        # Set the player execution mode.
        self.__robot_memory.set_running_mode(config, robot_profile, running_mode)

        # Execute the <settings> section
        self.node = self.settings_node[0] # First node of the <settings> section
        self.__state = "PLAY"
        self.play_next() # <voice>
        self.play_next() # <lightEffects>
        self.play_next() # <audioEffects>
        
        # Points to the first node of the <script> section
        self.node = self.script_node[0] # First node of the <script> section
        self.__state = "PLAY"
        console.rule("🤖 [red reverse b]  Executing the script: " + self.script_file + "  [/] 🤖\n")



    # Play the script
    def play_next(self): 
        if self.__state != "PLAY":
            print('The Player is not in the "PLAY" state and cannot be reset.')
            return False
        # Iterative version of the player. Now the XML is read iteratively, without recursion.
        if self.node == None: # None means the end of a level, where there is no longer a sibling node.
            if len(self.__robot_memory.get_node_stack()) != 0: # If there is an element in the stack.
                self.node = self.__robot_memory.node_stack_pop()
            else:
                if self.__state  == "PLAY":
                    # End of script
                    print('[b white]State:[/] [b white]End of script![/] 🎈🥳🥳🎈\n')
                    console.rule("🤖 [green reverse b]  Script finished: " + self.script_file + "  [/] 🤖")
                    time.sleep(1) # Tempo necessário para envio de mensagem MQTT.
                    print("\n\n")
                self.__state  = "IDLE"
                return True# Break

        # Process nodes that have children.
        elif len(self.node) > 0:
            # Gets the instance of the class corresponding to the implementation of the command associated with the node.
            command_handler_instance = self.tab_modules[self.node.tag][3] 
            if self.node.tag == "switch":
                if self.node.getnext() != None: # The "switch" node has a sibling ahead.
                    self.__robot_memory.node_stack_push(self.node.getnext()) # Node that will be executed after <switch> returns.
                self.__state = "BLOCKED"
                self.node = command_handler_instance.node_process(self.node, self.__robot_memory) # Executes the <switch> by placing its operator in memory.
                self.__state = "PLAY"
                self.node = self.node[0] # First <case> of <switch>

            elif self.node.tag == "case":
                # A case only executes if there is a switch operator in memory.
                if self.__robot_memory.get_op_switch() != None: # There must be a switch operator in memory. None indicates that a true case has already occurred in this switch.
                    self.__state = "BLOCKED"
                    self.node = command_handler_instance.node_process(self.node, self.__robot_memory) # Executes the <case> element by comparing it with the (switch) operator in memory. The result of the comparison is in robot_memory.flag_case.
                    self.__state = "PLAY"
                    if self.__robot_memory.get_flag_case() == True:
                        self.__robot_memory.set_flag_case(False)
                        self.__robot_memory.set_op_switch(None)
                        self.node = self.node[0] # Executes the first node of the <case> compound element (True).
                    else:
                        # Try to find the next case or the element default.
                        # If not found, node will be None.
                        self.node = self.node.getnext() 
                else:
                    self.node = self.node.getnext() 

            elif self.node.tag == "default" and self.__robot_memory.get_op_switch() != None: # If you've made it this far... then run!
                self.__state = "BLOCKED"
                self.node = command_handler_instance.node_process(self.node, self.__robot_memory)
                self.__state = "PLAY"
                self.node = self.node[0] # First <Default> node
            
            else:
                self.node = self.node.getnext()

        else: # Execution of common nodes.
            # Gets the instance of the class corresponding to the implementation of the command associated with the node.
            command_handler_instance = self.tab_modules[self.node.tag][3] 
            # Some cases of special nodes.
            if self.node.tag == "goto":
                self.__state = "BLOCKED"
                self.node = command_handler_instance.node_process(self.node, self.__robot_memory) # Executa o <goto> que retorna o nó destino (target).
                self.__state = "PLAY"
                self.node_target = self.node # Stores the target of the goto.
                # With execution directed to the <goto> "target" node
                # The nodes in the return address stack may lose their meaning if the goto directs
                # execution to a target node that belongs to a different parent than the goto's parent.
                # The stack must be cleared and new nodes inserted that are the parents of the "target" node.
                self.__robot_memory.node_stack_empty()

                # First element of node_stack must be the target node itself.
                self.__robot_memory.node_stack_push(self.node_target)
                self.node = self.node_target.getparent()

                # Search for the target node's parents.
                # Cases are not considered, because executing a case requires information about the switch that would be the cases' parent.
                # Therefore, switches are considered when searching for parents, and lastly, the root (script).
                # Macros are also considered as parents of their command groups, but not...
                while self.node.tag != "script" and self.node.tag != "macro":
                    if self.node.tag == "switch":
                        if self.node.getnext() == None:
                            self.node = self.node.getparent()
                        else:
                            self.__robot_memory.node_stack_push(self.node.getnext())
                            self.node = self.node.getparent()
                    else:
                        self.node = self.node.getparent()

                self.__robot_memory.node_stack_reverse()
                self.node = None # Will force reading of node_stack.

            elif self.node.tag == "useMacro": # Handling <useMacro> element
                if self.node.getnext() != None: # The "useMacro" node has a sibling ahead.
                    self.__robot_memory.node_stack_push(self.node.getnext()) # Node that will be executed after <useMacro> returns.
                
                self.__state = "BLOCKED"
                self.node = command_handler_instance.node_process(self.node, self.__robot_memory) # Run <useMacro> which returns the "macro" node.
                self.__state = "PLAY"
                self.node = self.node[0] # First node inside the "macro".

            else:
                self.__state = "BLOCKED"
                self.node = command_handler_instance.node_process(self.node, self.__robot_memory)
                self.__state = "PLAY"
                if self.node.tag == "stop":
                    if self.__state  == "PLAY":
                        # End of script
                        print('[b white]State:[/] [b white]End of script![/] 🎈🥳🥳🎈')
                        print()
                        console.rule("🤖 [green reverse b]  Script finished: " + self.script_file + "  [/] 🤖\n\n\n")
                        print("\n\n")
                    self.__state  = "IDLE"
                    return True # break
                self.node = self.node.getnext() # Call the next brother of the current node.



    # Allows play to return to the beginning of the script, resetting memory without resetting the ID table.   
    def reset(self):
        if self.__state != "PLAY":
            print('The Player is not in the "PLAY" state and cannot be reset.')
            return False
        self.__state  = "IDLE"
        self.node = self.script_node[0] # First node of the script.
        self.__robot_memory.reset_memory()
        return True