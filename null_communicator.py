from communicator_interface import CommunicatorInterface

# Estratégia 1: Sem comunicação
class NullCommunicator(CommunicatorInterface):
    
    def send(self, **kwargs):
        print("NULL: O módulo não se comunica com outros módulos.")
        
    def receive(self) -> dict:
        print("NULL: Sem recebimento. Nenhuma ação.")
        return {}