from core.vqh_source import VQHSource, VQHSourceStrategy, VQHFileReader, VQHProblem, VQHProtocol, VQHProcess
from core.vqh_mapper import VQHMapper, VQHMappingStrategy
from core.vqh_process_test import ProcessTest, ProblemTest, ProtocolTest, MappingTest
from problem.qubo import QUBOProblem
from protocols.basis import BasisProtocol
from vqe.vqe_process import VQEProcess
from time import sleep
from threading import Thread
import numpy as np
from queue import Queue
import config


# Quantum Hardware Connection
from hardware.hardware_library import HardwareLibrary

# SuperCollider, Sonification and Synthesis part
from synth.sonification_library import SonificationLibrary

# Event Management
import json
from csv import DictReader
import os


PROCESS_LIBRARY = {
        "test": (ProcessTest, ProblemTest, ProtocolTest),
        "qubo": (VQEProcess, QUBOProblem, BasisProtocol),
}

REALTIME_MODES = {
        'fixed': 0,
        'segmented': 1,
        'full': 2,
}

def init_vqh_process(name, filename, rt_mode, queue2) -> VQHProcess:
    
    process, problem, protocol = PROCESS_LIBRARY[name]
    return process(problem(filename), protocol(), rt_mode, queue2)


def init_vqh_file_reader(filename) -> VQHFileReader:

    return VQHFileReader(filename)

def init_vqh_source(process: VQHProcess) -> VQHSource:

    source = VQHSource(process)
    source.thread.start()
    return source

def wait_for_source_and_mapper(source: VQHSource, mapper: VQHMapper):

    source_finished = False
    mapper_finished = False

    while True:
        sleep(1)
        if source.is_done and not source_finished:
            source.stop()
            source_finished = True
        
        if mapper.is_done and not mapper_finished:
            mapper.stop()
            mapper_finished = True

        if source_finished and mapper_finished:
            break




class VQHCore:

    def __init__(self, strategy_type, strategy_name, hwi_name, son_type, rt_mode_name='fixed'):
        
        self.queue2 = Queue()
        self.strategy_type = strategy_type
        self.strategy_name = strategy_name
        self.rt_mode = REALTIME_MODES[rt_mode_name]
        self.strategy = self.init_strategy()

        self.hardware_library = HardwareLibrary()
        self.sonification_library = SonificationLibrary()
        
        self.hardware_interface = self.hardware_library.get_hardware_interface(hwi_name)
        self.hardware_interface.connect()
        self.hardware_interface.get_backend()
        config.PLATFORM = self.hardware_interface
        
        self.session_name = None

        self.son_type = son_type

        self.source = VQHSource(self.strategy)

        self.mapper = self.init_mapper()

        self.waiter = Thread(target=wait_for_source_and_mapper, args=(self.source, self.mapper))
        

        self.updater = Thread(target=self.update_realtime) 


    def init_strategy(self):

        print("Initializing strategy")
        if self.strategy_type == "file":
            return init_vqh_file_reader(self.strategy_name)
        elif self.strategy_type == "process":
            return init_vqh_process(self.strategy_name, 'h_setup_rt.csv', self.rt_mode, self.queue2)
        


    def init_mapper(self):


        print("Initializing mapper")
        synth, mapping = self.sonification_library.get_mapping(self.son_type)

        return VQHMapper(mapping, synth, [self.source.queue, self.queue2], clock_speed=0.1)


    def update_realtime(self):
        print(f"Realtime mode: {self.rt_mode}")
        if self.rt_mode == 0:
            return
        elif self.rt_mode == 1:
            while True:
                with open("rt_conf.json", "r") as f:
                    rt_config = json.load(f)
                self.mapper.update_clock_speed(rt_config["clock_speed"])
                if rt_config["end"]:
                    print("Ending UPDATER")
                    break
                sleep(1)


    def start(self):

        print("Starting VQHCore")
        self.source.thread.start()
        self.mapper.thread.start()
        self.waiter.start()
        self.updater.start()






"""
if __name__ == '__main__':
    process = init_vqh_process("test", "test.json")

    source = VQHSource(process)

    mapping_strategy = MappingTest()
    mapper = VQHMapper(mapping_strategy, source.queue)

    source.thread.start()
    mapper.thread.start()
    
    Thread(target=wait_for_source_and_mapper, args=(source, mapper)).start()

    sleep(5)
    mapper.update_clock_speed(0.2)

"""
