from time import sleep
from random import random
import numpy as np


class ProblemTest:
    def __init__(self, filename):
        self.data = None
        self.load_data(filename)

    def evaluate(self, x):
        return np.sum(self.data)

    def load_data(self, filename):
        self.data = np.random.random(10)
    

class ProtocolTest:
    def __init__(self):
        pass

    def encode(self, problem):
        return problem.data + 1

    def decode(self, iteration):
        return iteration + 100

class ProcessTest:
    def __init__(self, problem, protocol):
        self.problem = problem
        self.protocol = protocol

    def run(self, iteration_handler):

        algo = self.protocol.encode(self.problem)


        for i in range(len(algo)):
            sleep(0.1 + random())
            iteration = (np.random.random(12), random())
            observable = (self.protocol.decode(iteration[0]), iteration[1])
            print(observable)
            iteration_handler(observable)

class MappingTest:
    def __init__(self):
        pass

    def map(self, observable):
        print(f"Mapping: {observable}")
