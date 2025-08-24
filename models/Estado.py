from abc import ABC, abstractmethod

class Estado(ABC):

    @abstractmethod
    def iniciarEstado(self):
        pass

    @abstractmethod
    def emExecucao(self):
        pass
    
    @abstractmethod
    def sairEstado(self):
        pass