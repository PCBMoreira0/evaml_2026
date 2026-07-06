# Todos os valores na memória do robô são armazenados como strings, inclusive as representações de vetores VAD.
# Sendo de responsabildade de quem usa essas variáveis a conversão para o tipo adequado.

class RobotMemory(): # 
    def __init__(self):
        # Is equivalent to the $ of the original Eva VPL software.
        # Is a list of results.
        self.var_dollar = [] # It is a list of list, for example [user_answer, "<qrRead>"].

        # Eva ram (a key/value dictionary)
        self.vars = {}

        # System vars (a  key/value dictionary)
        self.system_vars = {}

        # LLM vars (a  key/value dictionary)
        self.llm_vars = {}

        # Flag de inicialização da LLM
        self.llm_vars["LLM_INIT"] = False

        # Stack of return nodes, used in script execution.
        self.node_stack = []

        # Contains the results of a comparison with the <case>. Can be True, False, or None.
        self.flag_case = None

        # <switch> element operator.
        self.op_switch = None

        # Script Player execution mode (default = terminal).
        self.running_mode = 'terminal'

        # Stores a response from the physical robot. It can be an STT text, an expression, etc.
        self.robot_response = None

        # Stores the state of the physical robot.
        self.robot_state = "free"

        # This table stores the count of sequence numbers from event logs.
        # Format {"log_name" : "number"}
        self.log_seq_numbers = {}

        # This table must contain all elements with "id", that is, those that can be called by a <goto> or by a <useMacro>.
        # Format {"Element name" : ["element_type (str)", <elment_reference>]}
        self.tab_ids = {} # Identify scrpit elements
        
        # Base topic for MQTT messages
        self.base_topic = None

        # [0, 1] values
        self.empathy = "0"

        # [0, 1] values
        self.emotion_decay = "0"

        # String representando um vetor do tipo VAD "0.1, 0.2, 0.3". VAD vector ([0, 1] values))
        self.base_mood = "0.0, 0.0, 0.0"

        # String representando um vetor do tipo VAD "0.1, 0.2, 0.3". VAD vector ([0, 1] values))
        self.robot_affective_state = "0.0, 0.0, 0.0"

        # String representando um vetor do tipo VAD "0.1, 0.2, 0.3". VAD vector ([0, 1] values))
        self.user_affective_state = "0.0, 0.0, 0.0"


    # Setters and Getters 
    def setDollar(self, value):
        self.var_dollar.append(value)

    def getDollar(self):
        return self.var_dollar
    
    def setVar(self, var_name, value):
        self.vars[var_name] = value

    def getVar(self, var_name):
        return self.vars[var_name]
    
    def getVars(self):
        return self.vars
    
    def getSystemVars(self):
        return self.system_vars
    
    def get_node_stack(self):
        return self.node_stack
    
    def node_stack_push(self, value):
        self.node_stack.append(value)

    def node_stack_empty(self):
        self.node_stack = []

    def node_stack_reverse(self):
        self.node_stack.reverse()

    def node_stack_pop(self):
        return self.node_stack.pop()

    def node_stack_last(self):
        return self.node_stack[-1]
    
    def set_flag_case(self, value):
        self.flag_case = value

    def get_flag_case(self):
        return self.flag_case

    def set_op_switch(self, value):
        self.op_switch = value

    def get_op_switch(self):
        return self.op_switch

    def set_base_topic(self, topic_name):
        self.base_topic = topic_name

    def get_base_topic(self):
        return self.base_topic
    
    def set_running_mode(self, config_file_ref, robot_profile_ref, mode):
        # When setting the execution mode, it sets the base topic based on informations in config and robot profile files.
        self.running_mode = mode # Setting mode

        # Setting MQTT base topic
        if mode == "terminal" or mode == "terminal-plus":
            self.set_base_topic(config_file_ref.TERMINAL_BASE_TOPIC)
        elif mode == "simulator":
            self.set_base_topic(robot_profile_ref.SIMULATOR_BASE_TOPIC)
        elif mode == "robot":
            self.set_base_topic(robot_profile_ref.ROBOT_BASE_TOPIC)

    def get_running_mode(self):
        return self.running_mode
    
    def set_robot_response(self, response):
        self.robot_response = response

    def get_robot_response(self):
        return self.robot_response

    def set_robot_state(self, state):
        self.robot_state = state

    def get_robot_state(self):
        return self.robot_state
    
    def set_log_seq_numbers(self, log_name, seg_number):
        self.log_seq_numbers[log_name] = seg_number

    def get_log_seq_numbers(self, log_name):
        return self.log_seq_numbers[log_name]
    
    def set_tab_ids(self, tab_ids): # The complete table.
        self.tab_ids = tab_ids

    def set_tab_ids_elemen_obj_ref(self, element_name, element_type, element_obj_ref):
        self.tab_ids[element_name] = [element_name, element_obj_ref]

    def get_tab_ids(self): # The complete table.
        return self.tab_ids

    def get_tab_ids_elemen_obj_ref(self, element_name):
        return self.tab_ids[element_name][1] # The obj_reference is the second element from list.
    
    def set_default_voice(self, voice_type):
        self.default_voice = voice_type

    def get_default_voice(self):
        return self.default_voice
    
    def set_default_voice_pitch_shift(self, value):
        self.default_voice_pitch_shift = value

    def get_default_voice_pitch_shift(self):
        return self.default_voice_pitch_shift
    
    # System Vars
    def set_empathy(self, value):
        self.system_vars["EMPATHY"] = value

    def set_decay(self, value):
        self.system_vars["EMOTION_DECAY"] = value

    def set_base_mood(self, value):
        self.system_vars["BASE_MOOD"] = value

    def set_robot_affective_state(self, value): # Value é uma string representando um vetor do tipo VAD "0.1, 0.2, 0.3"
        self.system_vars["ROBOT_AFFECTIVE_STATE"] = value

    def set_user_affective_state(self, value): # Value é uma string representando um vetor do tipo VAD "0.1, 0.2, 0.3"
        self.system_vars["USER_AFFECTIVE_STATE"] = value

    def get_empathy(self):
        return self.system_vars["EMPATHY"]

    def get_decay(self):
        return self.system_vars["EMOTION_DECAY"]
    
    def get_base_mood(self):
        return self.system_vars["BASE_MOOD"]
    
    def get_robot_affective_state(self):
        return self.system_vars["ROBOT_AFFECTIVE_STATE"]
    
    def get_user_affective_state(self):
        return self.system_vars["USER_AFFECTIVE_STATE"]

    # LLM Configuration Vars
    def set_llm_temperature(self, value):
        self.llm_vars["TEMPERATURE"] = value

    def set_llm_num_predict(self, value):
        self.llm_vars["NUM_PREDICT"] = value

    def get_llm_temperature(self):
        return self.llm_vars["TEMPERATURE"]

    def get_llm_num_predict(self):
        return self.llm_vars["NUM_PREDICT"]
    
    def set_llm_messages(self, value):
        if "MESSAGES" in self.llm_vars:
            self.llm_vars["MESSAGES"].append(value)
        else:
            self.llm_vars["MESSAGES"] = [value]

    def get_llm_messages(self):
        return self.llm_vars["MESSAGES"]
    
    def set_llm_init(self):
        self.llm_vars["LLM_INIT"] = True

    def get_llm_init(self):
        return self.llm_vars["LLM_INIT"]


    def reset_memory(self): # 
        # 
        self.var_dollar = []
        self.node_stack = []
        self.flag_case = None
        self.op_switch = None
        self.vars = {}
        self.log_seq_numbers = {}
        self.running_mode = 'terminal'
        self.robot_response = None
        self.robot_state = "free"
        self.system_vars["EMPATHY"] = "0"
        self.system_vars["EMOTION_DECAY"] = "0"
        self.system_vars["BASE_MOOD"] = "0.0, 0.0, 0.0" # VAD
        self.system_vars["ROBOT_AFFECTIVE_STATE"] = "0.0, 0.0, 0.0" # VAD
        self.system_vars["USER_AFFECTIVE_STATE"] = "0.0, 0.0, 0.0" # VAD
        self.llm_vars = {}
        self.llm_vars["LLM_INIT"] = False


