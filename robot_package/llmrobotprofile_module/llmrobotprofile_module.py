from rich import print

from base_command_handler import BaseCommandHandler

import robot_profile  # Module with network device configurations.


class CommandHandler(BaseCommandHandler):

    def __init__(self, xml_node, communicator_obj):
        
        super().__init__(self, communicator_obj)

    def node_process(self, xml_node, memory):
        """ Node process function """

        if xml_node.get("temperature") !=None:
            memory.set_llm_temperature(xml_node.get("temperature"))
            print("[b white]State: Setting [/]the [b white]LLM Temperature=" + xml_node.get("temperature") + "[/].")

        else:
            memory.set_llm_temperature("0.3")
            print("[b white]State: Setting [/]the [b white]LLM Temperature with the default value=" + "0.3" + "[/].")
        
        if xml_node.get("numPredict") !=None:
            memory.set_llm_num_predict(xml_node.get("numPredict"))
            print("[b white]State: Setting [/]the [b white]LLM Number of Predictions=" + xml_node.get("numPredict") + "[/].")

        else:
            memory.set_llm_num_predict("40")
            print("[b white]State: Setting [/]the [b white]LLM Number of Predictions with the default value=" + "40" + "[/].")
            
        # Coloca o texto do perfil do robot como um comando de system da LLM
        # Messages é uma lista de dicionários
        # Cada dicionário tem como chaves "role" e "content"
        # Messages armazena o contexto da sessão
        memory.set_llm_messages({"role": "system", "content": xml_node.text})
        print("[b white]State: Setting [/]the [b white]LLM Robot Profile Instructions:[/][b yellow][/]")


        return xml_node # It returns the same node
        