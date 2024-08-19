from abc import ABC, abstractmethod

class AbstractSource(ABC):
    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def getPrimaryContent(self):
        pass

    @abstractmethod
    def getChildLinks(self):
        pass

    @abstractmethod
    def processChildren(self):
        pass
