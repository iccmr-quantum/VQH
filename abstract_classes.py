from abc import ABC, abstractmethod
import asyncio

class QuantumHardwareInterface(ABC):
    
    @abstractmethod
    def __init__(self, n):
        self.provider = None
        self.backend = None

    @abstractmethod
    def execute(self, n):
        pass
    @abstractmethod
    def connect(self, n):
        pass
    @abstractmethod
    def get_backend(self, n):
        pass
    @abstractmethod
    def optimize(self, n):
        pass

class VQHProtocol(ABC):
    
    @abstractmethod
    def __init__(self, n):
        self.name = None

    @abstractmethod
    def encode(self, n): # midi to code
        pass
    @abstractmethod
    def decode(self, n): # code to midi
        pass

class SonificationInterface(ABC):
    
    def __init__(self, n):
        self.platform = None

    @abstractmethod
    async def map_data(self, newnotes):
        pass

    @abstractmethod
    async def play(self, newnotes):
        pass

