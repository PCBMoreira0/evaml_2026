from abc import ABC, abstractmethod


class BaseCommandHandler(ABC):
    """
    Base class for all EvaML language command modules.
    All must implement the node_process() method.
    """
    def __init__(self, xml_node, communicator_obj):

        self.xml_node = xml_node
        self.comms = communicator_obj

    def send(self, **kwargs):
        self.comms.send(**kwargs)

    def receive(self):
        return self.comms.receive()
    
    @abstractmethod
    def node_process(self, xml_node, memory):
        pass
