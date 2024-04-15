from queue import Queue, Empty
from threading import Thread
from time import sleep
from typing import Protocol, Callable, Any
import json
import numpy as np

class VQHSourceStrategy(Protocol):
    def run(self, iteration_handler: Callable[[tuple[np.ndarray,...]], None]) -> None:
        ...

class VQHFileReader:
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def run(self, iteration_handler: Callable[[tuple[np.ndarray,...]], None]) -> None:
        with open(self.filename) as f:
            data = json.load(f)
            for iteration in data:
                iteration_handler(iteration)

class VQHProblem(Protocol):
    data: np.ndarray

    def evaluate(self, x: np.ndarray) -> float:
        ...
    def load_data(self, filename: str) -> None:
        ...

class VQHProtocol(Protocol):
    def encode(self, problem: VQHProblem) -> Any:
        ...
    def decode(self, data: Any) -> np.ndarray:
        ...

class VQHProcess(VQHSourceStrategy, Protocol):
    #cost_fn: Callable[[np.ndarray], float]
    problem: VQHProblem
    protocol: VQHProtocol


class VQHSource:
    def __init__(self, strategy: VQHSourceStrategy):
        self.strategy = strategy
        self.queue = Queue()
        self.sentinel = None
        self.is_done = False
        self.thread = Thread(target=self.run_strategy)

    def start_source(self) -> None:
        self.thread.start()
        print("Thread started")


    def iteration_handler(self, iteration: tuple[np.ndarray,...]) -> None:
        self.queue.put(iteration)

    def stop(self) -> None:
        self.thread.join()
        print("Thread finished")


    def run_strategy(self) -> None:
        print("Thread started")
        self.is_done = False
        self.strategy.run(self.iteration_handler)
        self.queue.put(self.sentinel)
        self.is_done = True
