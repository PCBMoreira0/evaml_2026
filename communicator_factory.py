# Contém a fábrica e a instância global
from null_communicator import NullCommunicator
from pub_mqtt_communicator import PubMqttCommunicator
from pub_sub_mqtt_communicator import PubSubMqttComunicator
from http_communicator import HttpCommunicator

class CommunicatorFactory:

    def create_communicator(self, xml_node):

        comm_mode = xml_node.get("commMode")

        if comm_mode == "NULL":
            return NullCommunicator() # Retorna instância
            
        elif comm_mode == "MQTT_PUB":
            return PubMqttCommunicator(xml_node) # Retorna instância
            
        elif comm_mode == "MQTT_PUB_SUB":
            return PubSubMqttComunicator(xml_node) # Retorna instância

        elif comm_mode == "HTTP":
            return HttpCommunicator(xml_node) # Retorna instância    

        else:
            pass  

        # elif comm_mode == "serial":
        #     return SerialSender(port="/dev/ttyUSB0") # Retorna instância
        # else:
        #     raise ValueError(f"Tipo de comunicação desconhecido: {comm_type}")


# # AQUI ESTÁ A CHAVE: A instância da fábrica é criada uma única vez.
# comms_factory = CommunicatiorFactory() # Padrão Singleton