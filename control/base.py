"""
Base class for all control interfaces
"""
from abc import ABC, abstractmethod

class QUBOController(ABC):
    """Abstract base class for QUBO controllers"""
    
    @abstractmethod
    def __init__(self, problem_instance=None):
        self.problem = problem_instance
        self.current_matrix = {}
    
    @abstractmethod
    def start(self):
        """Start the controller"""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop the controller"""
        pass
    
    def connect_to_problem(self, problem_instance):
        """Connect controller to a QUBOProblem instance"""
        self.problem = problem_instance
