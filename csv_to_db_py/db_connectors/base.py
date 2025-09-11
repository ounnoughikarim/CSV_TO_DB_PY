from abc import ABC, abstractmethod

class BaseDBConnector(ABC):

    def __init__(self, config):
        self.config = config
        self.engine = None

    @abstractmethod
    def connect(self):
        pass

    def get_engine(self):
        return self.engine
