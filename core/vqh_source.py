from queue import Queue, Empty
from threading import Thread, Lock
from time import sleep
from typing import Protocol, Callable, Any, Union, Optional
import json
import numpy as np
from util.data_manager import VQHDataFileManager, VQHDataSet


class VQHSourceStrategy(Protocol):
    def run(self, iteration_handler: Callable[[tuple[np.ndarray,...]], None], **kwargs) -> None:
        ...

class VQHFileSource:
    def __init__(self, filem: VQHDataFileManager, filenum=0) -> None:
        self.filenumber = filenum
        self.file_manager = filem
        self.type = 'file'
        self.problem = None

    def run_latest(self, iteration_handler: Callable[[tuple[np.ndarray,...]], None]) -> None:
        dataset = self.file_manager.read(self.file_manager.latest_index)
        #print(dataset)
        for iteration in dataset.data:
            iteration_handler(iteration)
    def run_index(self, iteration_handler: Callable[[tuple[np.ndarray,...]], None], index:int=0) -> None:
        dataset = self.file_manager.read(index)
        for iteration in dataset.data:
            iteration_handler(iteration)
    
    def run(self, iteration_handler: Callable[[tuple[np.ndarray,...]], None]) -> None:


        if self.filenumber == 0:
            self.run_latest(iteration_handler)

        elif self.filenumber > 0:
            self.run_index(iteration_handler, self.filenumber)


class VQHProblem(Protocol):
    data: np.ndarray
    size: int

    def evaluate(self, x: np.ndarray) -> float:
        ...
    def load_data(self, filename: str) -> Any:
        ...

class VQHProtocol(Protocol):
    def encode(self, problem: VQHProblem) -> Any: # 'Any' means a list of instances of the problem
        ...
    def decode(self, data: Any) -> np.ndarray: # Any means a probability distribution
        ...

class VQHAlgorithm(Protocol):
    protocol: VQHProtocol
    def iteration_callback(self, iter_sample: Any, iter_expval: Union[float, np.ndarray, Any], handler: Callable[tuple[np.ndarray,...],None]) -> None:
        ...
    def prepare(self, problem: VQHProblem, count: Optional[int]=None) -> dict:
        ...
    def run_algorithm(self, initial_point: np.ndarray, callback: Callable[[Any], Any], **kwargs: Any) -> Any:
        ...

"""
class VQHProcess(VQHSourceStrategy, Protocol):
    problem: VQHProblem
    algorithm: VQHAlgorithm
    rt_mode: int
"""

class VQHProcess:
    def __init__(self, problem:VQHProblem, algorithm: VQHAlgorithm, rt_mode: int=0, problem_event=None, filem:VQHDataFileManager=None) -> None:

        self.problem = problem
        self.algorithm = algorithm
        self.handler = None
        self.rt_mode = rt_mode
        self.problem_event = problem_event
        self.lock = Lock()
        self.dataset = VQHDataSet()
        self.type = 'process'
        self.file_manager = filem
        self.statuspath = 'source_status.json'
        self.busy = False

        self._active = True

    @property
    def active(self):
        with self.lock:
            return self._active

    @active.setter
    def active(self, value):
        with self.lock:
            self._active = value

    def run_fixed(self, iteration_handler: Callable[[Any], Any])-> None:
        print('NON-REALTIME MODE')
        #print('NOT IMPLEMENTED YET! Use "segmented" mode for now. Exiting...')
        #sleep(2)
        self.handler = iteration_handler

        count = 0
        
        for c in range(1):

            print(f'Fixed Problem: #{count}')

            # Prepare the algorithm
            algorithm_params = self.algorithm.prepare(self.problem, count)
            if count == 0:
                current_point = self.algorithm.init_point()

            # Run the algorithm
            current_point = self.algorithm.run_algorithm(current_point, self.handler, **algorithm_params)

            print(f'Writing Data Set to File...')
            self.file_manager.write(self.dataset)

            count += 1



        #raise NotImplementedError
        #needs to send sentinel to queue?


    def run_segmented(self, iteration_handler: Callable[[Any], Any]):

        print('SEGMENTED REALTIME MODE')

        self.handler = iteration_handler
        count = 0

        while self.active:

            print(f'Next Segment: #{count}')
            self.busy = True
            with open(self.statuspath, 'w') as f:
                json.dump({'busy': self.busy}, f)

            # Prepare the algorithm
            algorithm_params = self.algorithm.prepare(self.problem, count)
            if count == 0:
                current_point = self.algorithm.init_point()
            # Run the algorithm
            current_point = self.algorithm.run_algorithm(current_point, self.handler, **algorithm_params)

            print(f'Writing Data Set to File...')
            self.file_manager.write(self.dataset)


            print(f'Waiting for New Problem...')

            self.problem_event.wait()
            self.problem_event.clear()
            self.busy = False
            with open(self.statuspath, 'w') as f:
                json.dump({'busy': self.busy}, f)
            self.dataset.clear()

            count += 1

    def run_realtime(self, iteration_handler: Callable[[Any], Any]):

        print('HARD REALTIME MODE')
        print('NOT IMPLEMENTED YET! Use "segmented" mode for now. Exiting...')
        sleep(2)
        raise NotImplementedError

    def run(self, iteration_handler, **kwargs):
        print('Running VQH Process...')
        if self.rt_mode == 0:
            self.run_fixed(iteration_handler)
        elif self.rt_mode == 1:
            self.run_segmented(iteration_handler)
        elif self.rt_mode == 2:
            self.run_realtime(iteration_handler)
        else:
            print('Invalid RT Mode! Choose a valid mode [0, 1, 2] during startup. Exiting...')
            sleep(1)
            raise ValueError

class VQHSource:
    def __init__(self, strategy: VQHSourceStrategy, queue: Queue) -> None:
        self.strategy = strategy
        self.queue = queue
        self.sentinel = None
        self.is_done = False
        self.thread = Thread(target=self.run_strategy)
        self.thread.daemon = True
        print(f'Source Strategy: {strategy}')

    def start_source(self) -> None:
        self.thread.start()
        print("Source started")


    def iteration_handler(self, iteration: tuple[np.ndarray,...]) -> None:
        #print(f"Received iteration {iteration}")
        self.queue.put(iteration)
        if self.strategy.type == 'process':
            self.strategy.dataset += iteration
            #print('This is a process')
            pass

    def stop(self) -> None:
        #self.thread.join()
        print("Source finished")


    def run_strategy(self) -> None:
        print("Thread started")
        self.is_done = False
        self.strategy.run(self.iteration_handler)
        print("Putting sentinel...")
        self.queue.put(self.sentinel)
        self.is_done = True
