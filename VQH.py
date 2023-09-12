#===========================================
# VQH: Variational Quantum Harmonizer
# Sonification of the VQE Algorithm
# Authors: Paulo Itaborai and Tim Schwägerl
#
#
# ICCMR, University of Plymouth, UK
# CQTA, DESY Institut, Germany
#
# Jan 2023
#===========================================
# VQE and Quantum Computing part
from qiskit import IBMQ
import vqh_functions as vqh

# SuperCollider, Sonification and Synthesis part
import sc_functions as sc

# Logging and global variables
import logging
import sys
import time

# Global variables
import ibmqglobals
import globalsvqh

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

VALID_COMMANDS = ['play', 'runvqe', 'q', 'quit', 'stop', 'testvqe', 'playfile']

# Future work: creating, managing music compositions, rehearsal and performance ----------------------------
# def update_compfile():

    # comp_events = DictReader(open("comp_events_template.csv"), skipinitialspace=True)
    # with open('composition_template.json', 'w') as compfile:

        # comp = {arg.pop('eventid'):{key:float(arg[key]) for key in arg} for arg in comp_events}
        # #logger.debug(f'COMP EVENTS F/ CSV: {comp}')
        # lastevent = len(comp)
        # comp[str(-lastevent)] = comp.pop(str(lastevent))
        # json.dump(comp, compfile, indent=4)

# ----------------------------------------------------------------------------------------------------------

# Play sonification from a previously generated file
def playfile(num, folder, son_type=1):
    path = f"{folder}/Data_{num}"
    with open(f"{path}/aggregate_data.json") as afile:
        dist = json.load(afile)
    with open(f"{path}/exp_values.txt") as efile:
        vals = [float(val.rstrip()) for val in efile]
    sc.sonify(dist, vals, son_type)

# Future work: creating, managing music compositions, rehearsal and performance ----------------------------
# def run_event(event):

    # global comp_events

    # logger.info(f'RUNNING EVENT {event}')
    # print(f'RUNNING EVENT {comp_events[0]} {event}')
    # logger.debug(f'DOING NOTHING FOR NOW')
# ----------------------------------------------------------------------------------------------------------

def is_command(cmd):
    return cmd.split(' ')[0] in VALID_COMMANDS
    
def CLI():
    global progQuit, comp, last, reset, generated_quasi_dist, comp_events
    generated_quasi_dist = []
    
    #print("here")
# Future work: creating, managing music compositions, rehearsal and performance ----------------------------
    # try:
        # ce = DictReader(open("comp_events_template.csv"), skipinitialspace=True)
        # #print(ce)
        # open('composition_template.json', 'w')
    # except:
        # print("not successfulk")
    # if os.path.exists('composition_template.json'):
        # update_compfile()
        # with open('composition_template.json') as compfile:
            # composition = json.load(compfile)
            # comp_events = deque([int(x) for x in composition])
            # #logger.debug(f'LOADED COMPOSITION: {composition}')
            # reset = True
# ----------------------------------------------------------------------------------------------------------
    #print("here")
    # prompt preparation
    session = PromptSession()
    validator = Validator.from_callable(is_command, error_message='This command does not exist. Check for mispellings.')

    while not progQuit:

# Future work: creating, managing music compositions, rehearsal and performance ----------------------------
        # if comp:
            # if comp_events[0] > 0:
                # current_event = int(comp_events[0])
            # elif comp_events[0] < 0:
                # current_event = -int(comp_events[0])
            # if last:
                # current_event = len(comp_events)+1
        # else:
            # current_event = 0

        # current_event -= 1
        # # --- PROMPT ---
        # x = session.prompt(f'({current_event}) VQH=> ', validator=validator, validate_while_typing=False)
# ----------------------------------------------------------------------------------------------------------
        

        #CLI Commands
        x = session.prompt(f' VQH=> ', validator=validator, validate_while_typing=False)
        x = x.split(' ')
        if x[0] == 'next' or x[0] == 'n':
            print(f'Score Features not implemented yet for the VQH!')


# Future work: creating, managing music compositions, rehearsal and performance ----------------------------
            # if reset:
                # reset = False
            # if last:
                # comp_events.clear()
                # comp = False
            # try:
                # print(comp_events[0])
                # logger.debug(f'EVENT : {comp_events[0]} {type(comp_events[0])}')
            # except:
                # print(f'Score ended! type "reset" to reload')
                # continue
            # run_event(composition[str(comp_events[0])])

            # if comp_events[0] < 0:
                # print('END OF SCORE')
                # last = True
            # comp_events.rotate(-1)
        # elif x[0] == 'previous':
            # if not comp:
                # print(f'Score ended! type "reset" to reload')
                # continue
            # if not reset:
                # comp_events.rotate(2)
                # if comp_events[0] < 0:
                    # print('You are in the beginning! Cannot go back!')
                    # continue
                # logger.debug(f'EVENT : {comp_events[0]} {type(comp_events[0])}')
                # run_event(composition[str(comp_events[0])])
                # last = False
                # comp_events.rotate(-1)
            # else:
                # print('The score was reset! type "next" to begin')

        # elif x[0] == 'reset':
            # print(f'Resetting Score...')
            # comp_events = deque([int(x) for x in composition])
            # last = False
            # comp = True
        # elif x[0] == 'repeat':
            # if not comp:
                # print(f'Score ended! type "reset" to reload')
                # continue
            # if not reset:
                # comp_events.rotate(1)
                # logger.debug(f'EVENT : {comp_events[0]} {type(comp_events[0])}')
                # run_event(composition[str(comp_events[0])])
                # comp_events.rotate(-1)
            # else:
                # print('The score was reset! type "next" to begin')
        # elif x[0] == 'updatecomp':
            # update_compfile()
            # with open('composition.json') as compfile:
                # composition = json.load(compfile)
                # comp_events = deque([int(x) for x in composition])
                # logger.debug(f'UPDATED COMPOSITION: {composition}')
                # reset = True
# ----------------------------------------------------------------------------------------------------------

        elif x[0] == 'quit' or x[0] == 'q':
            progQuit=True
            continue

        # Deprecated
        # elif x[0] == 'testvqe':
            # generated_quasi_dist = vqh.test_harmonize()
        
        # Main VQH Command
        elif x[0] == 'runvqe':
            if len(x) == 1:
                print("running VQE")
                generated_quasi_dist, generated_values = vqh.run_vqh(globalsvqh.SESSIONPATH)
            else:
                print('Error! Try Again')
        
        # Sonify From a previously generated VQE result in the session folder
        elif x[0] == 'playfile':
            son_type = 1
            if len(x) == 3:
                son_type = int(x[2])
            playfile(x[1], globalsvqh.SESSIONPATH, son_type)
        
        # Same as using ctrl+. in SuperCollider
        elif x[0] == 'stop':
            sc.freeall()
        
        # Sonify the last generated VQE result
        elif x[0] == 'play':
            if generated_quasi_dist != []:
                son_type = 1
                if len(x) == 2:
                    son_type = int(x[1])
                sc.sonify(generated_quasi_dist, generated_values, son_type)
            else:
                print("Quasi Dists NOT generated!")

# Future work: creating, managing music compositions, rehearsal and performance ----------------------------
        # elif x[0] == 'set':
            # if len(x) != 2:
                # print('The "set" function expects one argument. ex:"=> set 2" goes to event 2. Type again.')
                # continue
            # e_id = int(x[1])
            # if e_id > len(comp_events):
                # print(f'Error. There is no event {e_id} in the score. Type again.')
                # continue
            # print(f'Setting Score. type "next" to go to event {x[1]}.')
            # comp_events = deque([int(x) for x in composition])
            # if e_id < 0:
                # e_id = -e_id
                # last=True
            # if e_id == 1:
                # reset=True
            # comp_events.rotate(-e_id+1)
            # comp = True
# ----------------------------------------------------------------------------------------------------------
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

    p.add_argument('sessionpath', type=str, nargs='?', default='Session_', help="Folder name where VQE data will be stored/read")
    args = p.parse_args()
    logger.debug(args)


    globalsvqh.SESSIONPATH = args.sessionpath

    print('=====================================================')
    print('      VQH: Variational Quantum Harmonizer  - v1.0    ') 
    print('          by itaborala and schwaeti, 2023            ')
    print('                             ICCMR + DESY            ') 
    print('     https://github.com/iccmr-quantum/VQH            ')
    print('=====================================================')

    # Run CLI
    CLI()