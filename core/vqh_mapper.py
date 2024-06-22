from typing import Protocol
from time import sleep
from threading import Thread, Lock
from queue import Queue, Empty
import numpy as np

class VQHMappingStrategy(Protocol):

    def map(self, iteration: tuple[np.ndarray,...]) -> None:
        ...


class VQHMapper:

    def __init__(self, strategy, synthesizer, queue, clock_speed: int=2, timeout: int=1) -> None:
        self.queue = queue
        self.thread = Thread(target=self.run_mapper)
        self.clock_lock = Lock()
        self.strategy = strategy
        self.synthesizer = synthesizer
        self.timeout = timeout
        self.is_done = False

        self._clock_speed = clock_speed

    @property
    def clock_speed(self) -> int:
        with self.clock_lock:
            return self._clock_speed

    @clock_speed.setter
    def clock_speed(self, speed: int) -> None:
        with self.clock_lock:
            self._clock_speed = speed
            print(f"Clock speed updated to {speed}")
        

    def start_mapper(self) -> None:
        self.thread.start()
        print("Mapper started")

    def run_mapper(self) -> None:
        while not self.is_done:
            try:
                iteration = self.queue.get(timeout=self.timeout)
            except Empty:
                print("Waiting for data...")
                continue

            if iteration is None:
                print("Mapper found sentinel, stopping...")
                self.is_done = True
                break
           
            self.synthesizer.map_data(self.strategy, iteration)
            
            sleep(self.clock_speed)


    def stop(self) -> None:
        self.thread.join()
        self.synthesizer.freeall()
        print("Mapper finished")
