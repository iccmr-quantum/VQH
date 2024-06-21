from abc import ABC, abstractmethod

class QuantumHardwareInterface(ABC):

    @abstractmethod
    def __init__(self):
        self.provider = None
        self.backend = None

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def get_backend(self):
        pass

    @abstractmethod
    def optimize(self):
        pass

class MappingInterface:

    def __init__(self):
        self.platform = None

    def map_data(self, method, data, **kwargs):
        getattr(self, method)(data, **kwargs)

