#===========================================
# VQH: Variational Quantum Harmonizer
# Sonification of the VQE Algorithm
# Authors: Paulo Itaborai, Tim Schwägerl,
# María Aguado Yáñez, Arianna Crippa
#
# ICCMR, University of Plymouth, UK
# CQTA, DESY Zeuthen, Germany
# Universitat Pompeu Fabra, Spain
#
# Jan 2023 - Jan 2024
#===========================================
# VQE and Quantum Computing part
from qiskit import IBMQ


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
from collections import deque

# CLI Interface
import argparse
from argparse import RawDescriptionHelpFormatter
from prompt_toolkit import PromptSession
from prompt_toolkit.validation import Validator


level = logging.DEBUG

fmt = logging.Formatter('[%(levelname)s]:%(name)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(fmt)
logger = logging.getLogger(__name__)
logger.setLevel(level)
logger.addHandler(handler)

progQuit = False
comp = True
last = False
reset = True
port = ''

VALID_COMMANDS = ['play', 'runvqe', 'q', 'quit', 'stop', 'playfile', 'map', 'mapfile']


# Play sonification from a previously generated file
def playfile(num, folder, son_type=1):
    path = f"{folder}/Data_{num}"
    with open(f"{path}/aggregate_data.json") as afile:
        dist = json.load(afile)
    with open(f"{path}/exp_values.txt") as efile:
        vals = [float(val.rstrip()) for val in efile]
    sc.sonify(dist, vals, son_type)


class VQH:

    def __init__(self, protocol_name, hwi_name, soni_name=None):
        self.hardware_library = HardwareLibrary()
        self.protocol_library = ProtocolLibrary()
        self.sonification_library = SonificationLibrary() # There will be a sonification library
        
        self.protocol = self.protocol_library.get_protocol(protocol_name)
        config.PROTOCOL = self.protocol
        print(f'Encoding protocol: {self.protocol}')
        
        self.hardware_interface = self.hardware_library.get_hardware_interface(hwi_name)
        self.hardware_interface.connect()
        self.hardware_interface.get_backend()
        config.PLATFORM = self.hardware_interface

        print(f'Connected to HWI: {self.hardware_interface}, {self.hardware_interface.provider}, {self.hardware_interface.backend}')
        
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
        self.datafile = (dist, vals)
        self.synth, method = self.sonification_library.get_mapping(son_type)
        self.synth.map_data(method, self.datafile, **kwargs)


    def map_sonification(self, son_type=1, **kwargs):
        self.synth, method = self.sonification_library.get_mapping(son_type)
        self.synth.map_data(method, self.data, **kwargs)

    def stop_sc_sound(self):
        self.synth.freeall()


def is_command(cmd):
    return cmd.split(' ')[0] in VALID_COMMANDS
    
def CLI(vqh):
    global progQuit, comp, last, reset, generated_quasi_dist, comp_events
    generated_quasi_dist = []
    

    # prompt preparation
    session = PromptSession()
    validator = Validator.from_callable(is_command, error_message='This command does not exist. Check for mispellings.')

    while not progQuit:
      
        #CLI Commands
        x = session.prompt(f' VQH=> ', validator=validator, validate_while_typing=False)
        x = x.split(' ')
        if x[0] == 'next' or x[0] == 'n':
            print(f'Score Features not implemented yet for the VQH!')


        elif x[0] == 'quit' or x[0] == 'q':
            progQuit=True
            continue

        
        # Main VQH Command
        elif x[0] == 'runvqe':
            if len(x) == 1:
                print("running VQE")
                #generated_quasi_dist, generated_values = vqh.run_vqh(globalsvqh.SESSIONPATH)
                vqh.runvqe(config.SESSIONPATH)
            else:
                print('Error! Try Again')
        
        # Sonify From a previously generated VQE result in the session folder
        elif x[0] == 'playfile':
            son_type = 1
            if len(x) == 3:
                son_type = int(x[2])
            #playfile(x[1], config.SESSIONPATH, son_type)
            vqh.playfile(x[1], config.SESSIONPATH, son_type)
        
        # Same as using ctrl+. in SuperCollider
        elif x[0] == 'stop':
            #sc.freeall()
            vqh.stop_sc_sound()
        
        # Sonify the last generated VQE result
        elif x[0] == 'play':
            if generated_quasi_dist != []:
                son_type = 1
                if len(x) == 2:
                    son_type = int(x[1])
                #sc.sonify(generated_quasi_dist, generated_values, son_type)
                vqh.play(son_type)
            else:
                print("Quasi Dists NOT generated!")

        elif x[0] == 'map':
            if vqh.data:
                son_type = 1
                if len(x) == 2:
                    son_type = int(x[1])
                #sc.sonify(generated_quasi_dist, generated_values, son_type)
                vqh.map_sonification(son_type)
                
            else:
                print("Quasi Dists NOT generated!")
        elif x[0] == 'mapfile':
            son_type = 1
            if len(x) == 3:
                son_type = int(x[2])
            #playfile(x[1], config.SESSIONPATH, son_type)
            vqh.mapfile(x[1], config.SESSIONPATH, son_type)

        else:
            print(f'Not a valid input - {x}')

if __name__ == '__main__':


    descr = 'Variational Quantum Harmonizer\n\
CSV QUBOS syntax and rules:\n\
- File name MUST BE "h_setup.csv"\n\
- QUBO matrices should be exactly as the one below.\n\
The header should contain the matrix name and note labels.\n\
NO SPACE between commas for header and labels!\n\
Spaces allowed only for number entries. See "h_setup-Example.csv"\n\
    h1,label1,label2,label3,...,labeln\n\
    label1,c11,c12,c13,...,c1n\n\
    label2,c21,c22,c23,...,c2n\n\
    label3,c31,c32,c33,...,c3n\n\
    ...\n\
    labeln,cn1,cn2,cn3,...,cnn\n\
    h2,label1,label2,label3,...,labeln\n\
    label1,c11,c12,c13,...,c1n\n\
    ... \n\n\
Internal VQH functions:\n\
=> runvqe               Runs VQE and extracts sonification parameters.\n\
=> play                 Triggers a sonification method using the current\n\
                        VQE data extracted from the last call of "runvqe".\n\
                        The first argument is the sonification method.\n\
=> playfile             Triggers a sonification method using data stores in \n\
                        the session folder. The file index is the first \n\
                        argument. The second argument is the sonification \n\
=> stop                 Stops all sound in SuperCollider.\n\
=> quit, q              Exits the program.\n '


    p = argparse.ArgumentParser(description=descr, formatter_class=RawDescriptionHelpFormatter)

    p.add_argument('sessionpath', type=str, nargs='?', default='Session', help="Folder name where VQE data will be stored/read")
    p.add_argument('platform', type=str, nargs='?', default='local', help="Quantum Platform provider used (Local, IQM, IBMQ). Default is 'local'.")
    p.add_argument('protocol', type=str, nargs='?', default='harp', help="Encoding strategy for generating sonification data. Default is 'harp'.")
    args = p.parse_args()
    logger.debug(args)


    config.SESSIONPATH = args.sessionpath
    config.HW_INTERFACE = args.platform

    vqh = VQH(args.protocol, args.platform)

    print('=====================================================')
    print('      VQH: Variational Quantum Harmonizer  - v1.1    ') 
    print('          by itaborala and schwaeti, 2023            ')
    print('                             ICCMR + DESY            ') 
    print('     https://github.com/iccmr-quantum/VQH            ')
    print('=====================================================')

    # Run CLI
    CLI(vqh)
