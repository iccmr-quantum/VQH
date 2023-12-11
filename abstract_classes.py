from abc import ABC, abstractmethod
import asyncio

class QuantumHardwareInterface(ABC):
    
    @abstractmethod
    def __init__(self, n):
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

class VQHProtocol(ABC):
    
    @abstractmethod
    def __init__(self, n):
        self.name = None
        self.data = None

    @abstractmethod
    def encode(self): # midi to code
        pass
    @abstractmethod
    def decode(self): # code to midi
        pass
    @abstractmethod
    def run(self):
        pass

class SonificationInterface(ABC):
    
    def __init__(self, n):
        self.platform = None

    @abstractmethod
    async def map_data(self):
        pass

    @abstractmethod
    async def play(self):
        pass

