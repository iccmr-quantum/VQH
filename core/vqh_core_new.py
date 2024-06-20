from core.vqh_source import VQHSource, VQHSourceStrategy, VQHFileStrategy, VQHProblem, VQHProtocol, VQHProcess
from core.vqh_mapper import VQHMapper, VQHMappingStrategy
from core.vqh_process_test import ProcessTest, ProblemTest, ProtocolTest, MappingTest
from problem.qubo import QUBOProblem, QUBOProblemRT
from protocols.basis import BasisProtocol
from vqe.vqe_process import VQEProcess
from vqe.vqe_algorithm import VQEAlgorithm
from time import sleep
from threading import Thread, Event
import numpy as np
from queue import Queue
import config

import sys
from util.inlets import VQHInlet, VQHOutlet
from util.data_manager import VQHDataFileManager, VQHDataSet, FileIO, JSONFileIO


# Quantum Hardware Connection
from hardware.hardware_library import HardwareLibrary

# SuperCollider, Sonification and Synthesis part
from synth.sonification_library import SonificationLibrary

# Event Management
import json
from csv import DictReader
import os
from control_to_setup2 import json_to_csv

PROCESS_LIBRARY = {
        "test": (ProcessTest, ProblemTest, ProtocolTest), #Deprecated
        "qubo": (VQEProcess, QUBOProblem, BasisProtocol), #Deprecated
        "qubort": (VQEProcess, QUBOProblemRT, BasisProtocol), #Deprecated
        "qubo_algo": (VQHProcess, VQEAlgorithm, QUBOProblemRT, BasisProtocol)
}


REALTIME_MODES = {
        'fixed': 0,
        'segmented': 1,
        'full': 2,
        'file': 3
}

def init_vqh_process(name, filename, rt_mode, problem_event, sessioname) -> VQHProcess:
    
    process, algorithm, problem, protocol = PROCESS_LIBRARY[name]
    return process(problem(filename), algorithm(protocol()), rt_mode, problem_event, VQHDataFileManager(sessioname))


def init_vqh_file_strategy(sessionname) -> VQHFileStrategy:

    return VQHFileStrategy(VQHDataFileManager(sessionname))

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
        #print(source.is_done, mapper.is_done)
        #print(source_finished, mapper_finished)

        if source_finished and mapper_finished:
            print("Ending Waiter Thread")
            break

class VQHCore:

    def __init__(self, strategy_type, strategy_name, hwi_name, son_type, rt_mode_name='fixed', session_name="Default"):
        
        self.problem_event = Event()
        self.strategy_type = strategy_type
        self.strategy_name = strategy_name
        self.rt_mode = REALTIME_MODES[rt_mode_name]
        self.session_name = session_name
        #self.strategy = self.init_strategy()
        #print(f"Strategy: {self.strategy}")
        self.strategy = None

        self.hardware_library = HardwareLibrary()
        self.sonification_library = SonificationLibrary()
        
        self.hardware_interface = self.hardware_library.get_hardware_interface(hwi_name)
        #self.hardware_interface.connect()
        #self.hardware_interface.get_backend()
        #config.PLATFORM = self.hardware_interface
        #self.init_hardware_interface()
        

        self.son_type = son_type

        #self.source = VQHSource(self.strategy)
        self.source = None

        #self.mapper = self.init_mapper()
        self.mapper = None

    def init_hardware_interface(self):
        print("Connecting to hardware interface")

        self.hardware_interface.connect()
        self.hardware_interface.get_backend()
        config.PLATFORM = self.hardware_interface


    def init_strategy(self):

        print("Initializing strategy")
        print(f"Strategy type: {self.strategy_type}")
        if self.strategy_type == "file":
            return init_vqh_file_strategy(self.session_name)
        elif self.strategy_type == "process":
            if self.strategy_name in ['test', 'qubo', 'qubort']:
                print(f"This strategy '{self.strategy_name}' is deprecated. Use qubo_algo instead")
                raise ValueError
            return init_vqh_process(self.strategy_name, 'h_setup_rt.csv', self.rt_mode, self.problem_event, self.session_name)
        


    def init_mapper(self):


        print("Initializing mapper")
        synth, mapping = self.sonification_library.get_mapping(self.son_type)

        return VQHMapper(mapping, synth, self.source.queue, clock_speed=0.1)




class VQHController:

    def __init__(self, core: VQHCore):

        self.core = core
        self.rt_mode = core.rt_mode

        self.waiter = Thread(target=wait_for_source_and_mapper, args=(self.core.source, self.core.mapper))
        

        self.updater = Thread(target=self.update_realtime)

        self.is_active = True


        self.outlet = VQHOutlet()

        #self.qubos_inlet = VQHInlet(self.core.source.strategy.problem, 'qubos')

        #self.clock_speed_inlet = VQHInlet(self.core.mapper, 'clock_speed')

        #self.scale_inlet = VQHInlet(self.core.mapper.synthesizer.scale, 'current_scale')

        #self.outlet.connect(self.qubos_inlet)
        #self.outlet.connect(self.clock_speed_inlet)
        #self.outlet.connect(self.scale_inlet)


        self.current_state = {}
        self.current_state["clock_speed"] = 0.05#self.core.mapper.clock_speed


        
    def update_realtime(self):
        print(f"Realtime mode: {self.rt_mode}")
        if self.rt_mode == 0:
            print("No RT mode")
            return
        elif self.rt_mode == 1:
            while self.is_active:
                with open("rt_conf.json", "r") as f:
                    rt_config = json.load(f)
                #print(f"Updating {rt_config}")

                try:
                    if rt_config['scale'] != self.core.mapper.synthesizer.scale.current_scale:
                        self.outlet.bang({"current_scale": rt_config['scale']})
                        self.current_state["scale"] = rt_config['scale']
                except Exception as e:
                    print('Synth not ready yet. skipping scale update')
                    continue

                if rt_config["clock_speed"] != self.core.mapper.clock_speed:
                    self.outlet.bang({"clock_speed": rt_config["clock_speed"]})
                    self.current_state["clock_speed"] = rt_config["clock_speed"]
                if rt_config["end"]:
                    print("Ending UPDATER")
                    #self.core.mapper.stop()
                    self.core.mapper.synthesizer.freeall()
                    sys.exit(0)
                    break
                if rt_config["next_problem"]:
                    json_to_csv('midi/qubo_control.json', 'h_setup_rt.csv')
                    #sleep(0.05)
                    self.outlet.bang({"qubos": "h_setup_rt.csv"})
                    self.core.problem_event.set()
                    rt_config["next_problem"] = False
                    with open("rt_conf.json", "w") as f:
                        json.dump(rt_config, f)
                sleep(1)

    def init_core(self):
        self.core.strategy = self.core.init_strategy()
        print(f"Strategy: {self.core.strategy}")
        self.core.init_hardware_interface()
        self.core.source = VQHSource(self.core.strategy)
        self.core.mapper = self.core.init_mapper()

        self.qubos_inlet = VQHInlet(self.core.source.strategy.problem, 'qubos')
        self.clock_speed_inlet = VQHInlet(self.core.mapper, 'clock_speed')
        self.scale_inlet = VQHInlet(self.core.mapper.synthesizer.scale, 'current_scale')

        self.outlet.connect(self.qubos_inlet)
        self.outlet.connect(self.clock_speed_inlet)
        self.outlet.connect(self.scale_inlet)

    def start(self):

        if not self.core.strategy:
            raise RuntimeError("Strategy not initialized!")
        if not self.core.source:
            raise RuntimeError("Source not initialized!")
        if not self.core.mapper:
            raise RuntimeError("Mapper not initialized!")
            

        print("Starting VQHController")
        self.is_active = True
        #self.core.source.thread.start()
        self.core.source.start_source()
        self.core.mapper.thread.start()
        self.waiter.start()
        self.updater.start()

    def clean(self):
        print("Cleaning VQHController")
        
        self.core.mapper.synthesizer.free()
        self.core.source.is_done = True
        self.core.mapper.is_done = True
        sleep(1)
        self.is_active = False
        #self.waiter.join()
        #self.updater.join()

        


