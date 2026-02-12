from abc import ABC, abstractmethod

class CommunicatorInterface(ABC):
    @abstractmethod
    def send(self, **kwargs):
        pass

    @abstractmethod
    def receive(self):
        pass