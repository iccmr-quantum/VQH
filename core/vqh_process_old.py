from queue import Queue, Empty
from threading import Thread
from typing import Protocol, Union
import time




class VQHProcess(Protocol):
    def run(self):
        ...

class VQHProcessSource:
    def __init__(self, process: Union[VQHAlgorithm, VQHFile]):
        #self.data = data

        self.process = process

        self.queue = Queue()
        self.thread = Thread(target=self.process.run, kwargs={'callback': self.post})
        self.thread.start()

    def post(self, data):
        print(f'Posting {data}')
        self.queue.put(data)
        #for item in self.data:
        #    self.queue.put(item)
        #    time.sleep(1)

    def close(self):
        self.thread.join()
        print('closed')



class VQHProblem:
    def __init__(self):
        self.data = "DATA"

#    def evaluate(self, configuration):




class VQHAlgorithm(Protocol):
    cost_fn: callable
    configuration: dict

    def encode(self, data): # input variables to qc variables
        ...
    def decode(self, data): # qc variables to input variables
        ...

    def run(self, problem: VQHProblem):
        ...
        
       
class VQHFile(Protocol):
    metadata: dict

    def read(self):
        ...
    def run(self):
        ...


"""

class VQHVQEFile:
    def __init__(self, source: VQHProcessSource, metadata: dict):
        self.source = source
        self.metadata = metadata
        self.data = None

    def read(self):
        print('Reading...')
        self.data = 'DATA'

    def run(self):
        self.read()
        print(f'Running {self.data}')
        self.source.post()
        self.source.close()


class VQHVQE:
    def __init__(self, source: VQHProcessSource, cost_fn: callable, configuration: dict):
        self.source = source
        self.cost_fn = cost_fn
        self.configuration = configuration

    def encode(self, data=None):
        print(f'Encoding {data}')
        
    def decode(self, data=None):
        print(f'Decoding {data}')

    def run(self, problem: VQHProblem):
        self.encode(problem.data)
        print(f'Running {problem.data}')
        self.decode(problem.data)
        self.source.post()
        self.source.close()

def fooo(p: VQHAlgorithm):
    p.run(VQHProblem())

def fooofile(p: VQHFile):
    p.run()

def main():
    
    source = VQHProcessSource()
    algorithm = VQHVQE(source, lambda x: x, {})
    file = VQHVQEFile(source, {})
    fooo(algorithm)
    fooofile(file)

if __name__ == '__main__':
    main()


"""
