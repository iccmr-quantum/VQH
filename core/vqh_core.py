# Logging and global variables
import logging
import sys
import time

# Global variables
import config

# Quantum Hardware Connection
from hardware.hardware_library import HardwareLibrary

# Encoders, Decoders, Models
from protocols.protocol_library import ProtocolLibrary

# SuperCollider, Sonification and Synthesis part
from synth.sonification_library import SonificationLibrary

# Event Management
import json
from csv import DictReader
import os


level = logging.DEBUG

fmt = logging.Formatter('[%(levelname)s]:%(name)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(fmt)
logger = logging.getLogger(__name__)
logger.setLevel(level)
logger.addHandler(handler)

# ============================ VQH PROCESS CLASS ===============================


class VQHProcess:

    def __init__(self, protocol_name, rt_mode=False):

        self.protocol_library = ProtocolLibrary()


        self.protocol = self.protocol_library.get_protocol(protocol_name)
        config.PROTOCOL = self.protocol
        print(f'Encoding/Decoding protocol: {self.protocol}')

        self.rt_mode = rt_mode




# ============================= VQH CORE CLASS =================================

class VQH:

    def __init__(self, protocol_name, hwi_name, soni_name=None):
        self.hardware_library = HardwareLibrary()
        self.protocol_library = ProtocolLibrary()
        self.sonification_library = SonificationLibrary()
#        self.operator_library = OperatorLibrary()
        
        self.protocol = self.protocol_library.get_protocol(protocol_name)
        config.PROTOCOL = self.protocol
        print(f'Encoding protocol: {self.protocol}')
        
        self.hardware_interface = self.hardware_library.get_hardware_interface(hwi_name)
        self.hardware_interface.connect()
        self.hardware_interface.get_backend()
        config.PLATFORM = self.hardware_interface

        #print(f'Connected to HWI: {self.hardware_interface}, {self.hardware_interface.provider}, {self.hardware_interface.backend}')
        
        self.session_name = None
        self.synth = None

        self.data = None

    def runvqe(self, sessionname = "Default"):

        self.session_name = sessionname
        # The function below is the main function inside your protocol class
        self.data = self.protocol.run(self.session_name)
        self.datafile = None
    
    # Play sonification from a previously generated file
    def playfile(num, folder, son_type=1):
        path = f"{folder}/Data_{num}"
        with open(f"{path}/aggregate_data.json") as afile:
            dist = json.load(afile)
        with open(f"{path}/exp_values.txt") as efile:
            vals = [float(val.rstrip()) for val in efile]
        sc.sonify(dist, vals, son_type)
                
    def play(self, son_type=1):
        generated_quasi_dist, generated_values = self.data
        sc.sonify(generated_quasi_dist, generated_values, son_type)

    def mapfile(self, num, folder, son_type=1, **kwargs):
        path = f"{folder}_Data/Data_{num}"
        with open(f"{path}/aggregate_data.json") as afile:
            dist = json.load(afile)

        with open(f"{path}/exp_values.txt") as efile:
            vals = [float(val.rstrip()) for val in efile]

        states = []
        with open(f"{path}/max_prob_states.txt", 'r') as file:
            for line in file:
                #state_list = [int(char) for char in line.strip()]
                #states.append(state_list)
                states.append(line.rstrip())

        self.datafile = (dist, vals, states)
        self.synth, method = self.sonification_library.get_mapping(son_type)
        self.synth.map_data(method, self.datafile, **kwargs)


    def map_sonification(self, son_type=1, **kwargs):
        self.synth, method = self.sonification_library.get_mapping(son_type)
        self.synth.map_data(method, self.data, **kwargs)

    def stop_sc_sound(self):
        self.synth.freeall()

