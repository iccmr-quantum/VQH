from core.vqh_source import VQHSource, VQHSourceStrategy, VQHFileSource, VQHProblem, VQHProtocol, VQHProcess
from core.vqh_mapper import VQHMapper, VQHMappingStrategy
from core.vqh_process_test import ProcessTest, ProblemTest, ProtocolTest, MappingTest
from problem.qubo import QUBOProblem
from protocols.basis import BasisProtocol
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
        "qubo": (VQHProcess, VQEAlgorithm, QUBOProblem, BasisProtocol)
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


def init_vqh_file_strategy(sessionname, filenumber=None) -> VQHFileSource:
    if filenumber:
        return VQHFileSource(VQHDataFileManager(sessionname), filenumber)

    return VQHFileSource(VQHDataFileManager(sessionname))

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
            print("Ending Waiter Thread")
            break

class VQHCore:

    def __init__(self, strategy_type, method_name, hwi_name, son_type, rt_mode_name='fixed', session_name="Default"):
        
        self.problem_event = Event()
        self.strategy_type = strategy_type
        self.method_name = method_name
        self.rt_mode = REALTIME_MODES[rt_mode_name]
        self.session_name = session_name
        self.strategy = None
        self.queue = Queue()

        self.hardware_library = HardwareLibrary()
        self.sonification_library = SonificationLibrary()
        
        self.hardware_interface = self.hardware_library.get_hardware_interface(hwi_name)

        self.son_type = son_type

        self.source = None
        self.mapper = None

    def init_hardware_interface(self):
        print("Connecting to hardware interface")

        self.hardware_interface.connect()
        self.hardware_interface.get_backend()
        config.PLATFORM = self.hardware_interface


    def init_strategy(self, method_name=None):

        print("Initializing strategy")
        print(f"Strategy type: {self.strategy_type}")
        if self.strategy_type == "file":
            if isinstance(self.method_name, type(None)):
                return init_vqh_file_strategy(self.session_name)

            else:
                try:
                    file_number = int(self.method_name)
                except ValueError as e:
                    print(e)
                    print(f"File method names should be valid integers for accessing an existing data folder. Using 'None' instead, for latest experiment in the database.")
                    return init_vqh_file_strategy(self.session_name)
                return init_vqh_file_strategy(self.session_name, file_number)


        elif self.strategy_type == "process":
            if self.method_name not in PROCESS_LIBRARY.keys() or self.method_name in ['test', None]:
                print(f"This method '{self.method_name}' does not exist (or is deprecated). Use qubo instead")
                raise ValueError
            return init_vqh_process(self.method_name, 'h_setup_rt.csv', self.rt_mode, self.problem_event, self.session_name)
        


    def init_mapper(self):


        print("Initializing mapper")
        synth, mapping = self.sonification_library.get_mapping(self.son_type)

        return VQHMapper(mapping, synth, self.queue, clock_speed=0.1)




class VQHController:

    def __init__(self, core: VQHCore):

        self.core = core
        self.rt_mode = core.rt_mode

        self.waiter = Thread(target=wait_for_source_and_mapper, args=(self.core.source, self.core.mapper))
        

        self.updater = Thread(target=self.update_realtime)

        self.is_active = True


        self.outlet = VQHOutlet()

        self.current_state = {}
        self.current_state["clock_speed"] = 0.05#self.core.mapper.clock_speed


    def update_current_scale(self, scale):

        if scale != self.core.mapper.synthesizer.scale.current_scale:
            self.outlet.bang({"current_scale": scale})
            self.current_state["scale"] = scale

    def update_clock_speed(self, clock_speed):

        if clock_speed != self.core.mapper.clock_speed:
            self.outlet.bang({"clock_speed": clock_speed})
            self.current_state["clock_speed"] = clock_speed

    def update_qubos(self, csv_file):

        json_to_csv('midi/qubo_control.json', csv_file)
        self.outlet.bang({"qubos": csv_file})

    def update_realtime(self, thread=None):
        print(f"Realtime mode: {self.rt_mode}")

        if self.rt_mode == 0 and not thread:
            print("No thread specified. Exiting")
            raise ValueError("No thread specified for fixed mode (should be 'source' or 'mapper')")

        if self.rt_mode == 0 and thread == 'source':
            with open("rt_conf.json", "r") as f:
                rt_config = json.load(f)
            print("FIXED mode: Source")
            print("Outlet: ", self.outlet.inlets)

            for inlet in self.outlet.inlets.values():
                try:
                    getattr(self, f"update_{inlet.name}")(rt_config[inlet.name])
                    print(f"Updated {inlet.name}")
                except Exception as e:
                    print(f"Skipping {inlet.name} update")
                    print(e)

            return

        elif self.rt_mode == 0 and thread == 'mapper':
            print("FIXED mode: Mapper")

            while not self.core.mapper.is_done:
                with open("rt_conf.json", "r") as f:
                    rt_config = json.load(f)

                for inlet in self.outlet.inlets.values():
                    try:
                        getattr(self, f"update_{inlet.name}")(rt_config[inlet.name])
                        print(f"Updated {inlet.name}")
                    except Exception as e:
                        print(f"Skipping {inlet.name} update")
                        print(e)
                sleep(1)
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
                    if self.core.source.busy:
                        print("Source is busy. Don't overload me!")
                        continue
                    #json_to_csv('midi/qubo_control.json', 'h_setup_rt.csv')
                    #sleep(0.05)
                    self.outlet.bang({"qubos": "h_setup_rt.csv"})
                    self.core.problem_event.set()
                    rt_config["next_problem"] = False
                    with open("rt_conf.json", "w") as f:
                        json.dump(rt_config, f)
                sleep(1)

        elif self.rt_mode == 2:
            raise NotImplementedError(f'Mode {self.rt_mode} not implemented yet')
        elif self.rt_mode == 3:
            print("FILE MODE")
            raise NotImplementedError(f'Mode {self.rt_mode} not implemented yet')


    def init_core(self, mode=1):
        self.rt_mode = mode
        self.reset_outlet()
        self.core.strategy = self.core.init_strategy()
        print(f"Strategy: {self.core.strategy}")
        self.core.init_hardware_interface()
        self.core.source = VQHSource(self.core.strategy, self.core.queue)
        self.core.mapper = self.core.init_mapper()
        self.waiter = Thread(target=wait_for_source_and_mapper, args=(self.core.source, self.core.mapper))
        self.updater = Thread(target=self.update_realtime)

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

    def run_source(self, change_type=None, change_name=None, clear_queue=True):
        if change_type:
            self.core.strategy_type = change_type
        if change_name:
            self.core.method_name = change_name

        self.rt_mode = 0
        self.reset_outlet()

        self.core.strategy = self.core.init_strategy()
        self.core.init_hardware_interface()
        self.core.source = VQHSource(self.core.strategy, self.core.queue)
        self.updater = Thread(target=self.update_realtime, args=('source',))
        self.qubos_inlet = VQHInlet(self.core.source.strategy.problem, 'qubos')
        self.outlet.connect(self.qubos_inlet)


        #Update Problem inlets
        self.updater.start()
        self.updater.join()
        self.core.source.start_source()

    def run_mapper(self, change_son=None):
        if change_son:
            self.core.son_type = change_son

        

        self.rt_mode = 0
        self.reset_outlet()

        self.core.mapper = self.core.init_mapper()
        if self.core.queue is None or self.core.queue.empty():
            print("Queue is empty. Run Source first")
            self.core.mapper = None
            return
        self.updater = Thread(target=self.update_realtime, args=('mapper',))
        self.clock_speed_inlet = VQHInlet(self.core.mapper, 'clock_speed')
        self.scale_inlet = VQHInlet(self.core.mapper.synthesizer.scale, 'current_scale')
        self.outlet.connect(self.clock_speed_inlet)
        self.outlet.connect(self.scale_inlet)

        #Update Mapper inlets
        self.core.mapper.thread.start()
        self.updater.start()

    def reset_outlet(self):
        print("Resetting Outlet")
        self.outlet.reset()

    def print_queue(self):
        print(f"Queue: {self.core.queue.queue}")

    def queue_reset(self):
        self.core.queue.queue.clear()

    def queue_length(self):
        print(f"Queue length: {len(self.core.queue.queue)}")

    def print_library(self):
        #print("Hardware Library: ", self.core.hardware_library)
        print("Sonification Library:")
        for key, value in self.core.sonification_library._library.items():
            print(f"{key} => {value['description']} ({value['interface'].upper()})")

    def clean(self):
        print("Cleaning VQHController")
        
        self.core.mapper.synthesizer.free()
        self.core.source.is_done = True
        self.core.mapper.is_done = True
        sleep(1)
        self.is_active = False
        #self.waiter.join()
        #self.updater.join()

        
    def stop_synth(self):
        try:
            self.core.mapper.synthesizer.freeall()
        except Exception as e:
            print(e)
            print("Synth does not have freeall function, or is not initialized yet")


