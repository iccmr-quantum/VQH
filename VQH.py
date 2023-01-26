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

#VALID_COMMANDS = ['n', 'next', 'repeat', 'previous', 'reset', 'set', 'play', 'updatecomp', 'runvqe', 'changebackend', 'changehub', 'changegroup', 'changeproject', 'loadaccount', 'q', 'quit']
VALID_COMMANDS = ['play', 'runvqe', 'q', 'quit', 'stop', 'testvqe']

def update_compfile():

    comp_events = DictReader(open("comp_events_template.csv"), skipinitialspace=True)
    with open('composition_template.json', 'w') as compfile:

        comp = {arg.pop('eventid'):{key:float(arg[key]) for key in arg} for arg in comp_events}
        logger.debug(f'COMP EVENTS F/ CSV: {comp}')
        lastevent = len(comp)
        comp[str(-lastevent)] = comp.pop(str(lastevent))
        json.dump(comp, compfile, indent=4)


def run_event(event):

    global comp_events

    logger.info(f'RUNNING EVENT {event}')
    print(f'RUNNING EVENT {comp_events[0]} {event}')
    logger.debug(f'DOING NOTHING FOR NOW')

def is_command(cmd):
    return cmd.split(' ')[0] in VALID_COMMANDS
    
def CLI(BACKEND):
    global progQuit, comp, last, reset, generated_quasi_dist, comp_events
    generated_quasi_dist = []
    
    print("here")
    try:
        ce = DictReader(open("comp_events_template.csv"), skipinitialspace=True)
        print(ce)
        open('composition_template.json', 'w')
    except:
        print("not successfulk")
    if os.path.exists('composition_template.json'):
        update_compfile()
        with open('composition_template.json') as compfile:
            composition = json.load(compfile)
            comp_events = deque([int(x) for x in composition])
            logger.debug(f'LOADED COMPOSITION: {composition}')
            reset = True

    print("here")
    # prompt preparation
    session = PromptSession()
    validator = Validator.from_callable(is_command, error_message='This command does not exist. Check for mispellings.')

    while not progQuit:

        if comp:
            if comp_events[0] > 0:
                current_event = int(comp_events[0])
            elif comp_events[0] < 0:
                current_event = -int(comp_events[0])
            if last:
                current_event = len(comp_events)+1
        else:
            current_event = 0

        current_event -= 1
        # --- PROMPT ---
        x = session.prompt(f'({current_event}) VQH=> ', validator=validator, validate_while_typing=False)

        x = x.split(' ')
        if x[0] == 'next' or x[0] == 'n':
            if reset:
                reset = False
            if last:
                comp_events.clear()
                comp = False
            try:
                print(comp_events[0])
                logger.debug(f'EVENT : {comp_events[0]} {type(comp_events[0])}')
            except:
                print(f'Score ended! type "reset" to reload')
                continue
            run_event(composition[str(comp_events[0])])

            if comp_events[0] < 0:
                print('END OF SCORE')
                last = True
            comp_events.rotate(-1)
        elif x[0] == 'previous':
            if not comp:
                print(f'Score ended! type "reset" to reload')
                continue
            if not reset:
                comp_events.rotate(2)
                if comp_events[0] < 0:
                    print('You are in the beginning! Cannot go back!')
                    continue
                logger.debug(f'EVENT : {comp_events[0]} {type(comp_events[0])}')
                run_event(composition[str(comp_events[0])])
                last = False
                comp_events.rotate(-1)
            else:
                print('The score was reset! type "next" to begin')

        elif x[0] == 'reset':
            print(f'Resetting Score...')
            comp_events = deque([int(x) for x in composition])
            last = False
            comp = True
        elif x[0] == 'repeat':
            if not comp:
                print(f'Score ended! type "reset" to reload')
                continue
            if not reset:
                comp_events.rotate(1)
                logger.debug(f'EVENT : {comp_events[0]} {type(comp_events[0])}')
                run_event(composition[str(comp_events[0])])
                comp_events.rotate(-1)
            else:
                print('The score was reset! type "next" to begin')
        elif x[0] == 'updatecomp':
            update_compfile()
            with open('composition.json') as compfile:
                composition = json.load(compfile)
                comp_events = deque([int(x) for x in composition])
                logger.debug(f'UPDATED COMPOSITION: {composition}')
                reset = True


        elif x[0] == 'quit' or x[0] == 'q':
            progQuit=True
            continue


        elif x[0] == 'testvqe':
            generated_quasi_dist = vqh.test_harmonize()
        elif x[0] == 'runvqe':
            if len(x) == 1:
                print("running VQE")
                generated_quasi_dist = vqh.run_vqh()
            else:
                print('Error! Try Again')

        elif x[0] == 'stop':
            sc.freeall()
        elif x[0] == 'play':
            if generated_quasi_dist != []:
                sc.sonify(generated_quasi_dist)
            else:
                print("Quasi Dists NOT generated!")

        elif x[0] == 'changebackend':
            if len(x) == 2:
                BACKEND = x[1]
            else:
                print('Error! Try Again')
        elif x[0] == 'changehub':
            if len(x) == 2:
                config.HUB = x[1]
            else:
                print('Error! Try Again')
        elif x[0] == 'changegroup':
            if len(x) == 2:
                config.GROUP = x[1]
            else:
                print('Error! Try Again')
        elif x[0] == 'changeproject':
            if len(x) == 2:
                config.PROJECT = x[1]
            else:
                print('Error! Try Again')
        elif x[0] == 'loadaccount':
            IBMQ.load_account()
        elif x[0] == 'set':
            if len(x) != 2:
                print('The "set" function expects one argument. ex:"=> set 2" goes to event 2. Type again.')
                continue
            e_id = int(x[1])
            if e_id > len(comp_events):
                print(f'Error. There is no event {e_id} in the score. Type again.')
                continue
            print(f'Setting Score. type "next" to go to event {x[1]}.')
            comp_events = deque([int(x) for x in composition])
            if e_id < 0:
                e_id = -e_id
                last=True
            if e_id == 1:
                reset=True
            comp_events.rotate(-e_id+1)
            comp = True

        else:
            print(f'Not a valid input - {x}')



if __name__ == '__main__':


    descr = 'Variational Quantum Harmonizer\n\
CSV score syntax and rules:\n\
- File name MUST BE "comp_events.csv"\n\
- File must contain a header exactly as the one below:\n\
    event_id, recordsec, sequence, newnotes, delay\n\
- Each line contains 4 integer values. For example:\n\
    1, 5, 2, 10, 2\n\
- 1 == Event number\n\
  5 == Record duration\n\
  2 == Training sequences length\n\
  10 == Number of notes to generate\n\
  3 == Time delay before playing results \n\n\
internal VQH functions:\n\
  Composition (automatic) mode:\n\
=> next, n              Runs the next composition event from score (i+1).\n\
=> repeat               Repeats the current composition event (i)\n\
=> previous             Runs the previous composition event (i-1)\n\
=> reset                Resets the composition score.\n\
=> set [EVENTID]        Sets score so that the next event is EVENTID.\n\
=> updatecomp           Re-generates event dictionary for on-the-fly CSV score updates.\n\n\
  Manual mode:\n\
=> runvqe               Runs VQE.\n\
=> changebackend        Changes backend positional argument on-the-fly.\n\
=> changehub            Changes IBMQ --hub argument (only if --loadaccount is on) on-the-fly.\n\
=> changegroup          Changes IBMQ --group argument (only if --loadaccount is on) on-the-fly.\n\
=> changeproject        Changes IBMQ --project argument (only if --loadaccount is on) on-the-fly.\n\
=> loadaccount          Same as --loadaccount flag, on-the-fly.\n\n\
=> quit, q              Exits the program.\n\
    '


    p = argparse.ArgumentParser(description=descr, formatter_class=RawDescriptionHelpFormatter)

    p.add_argument('backend', type=str, nargs='?', default='Aer', help="IBM Quantum backend. Use 'Aer' for simulation ('aer_simulator'). Use 'least_busy' for real hardware, it will find the least busy IBMQ backend to run the job. Or use a custom backend name such as 'ibmq_belem'. NOTE: You need to load your IBMQ account to use real hardware. Run this script with the flag '--loadaccount'.")
    p.add_argument('--loadaccount', nargs='?', type=bool, const=True, default=False, help="Loads the locally stored IBMQ Account (IBMQ.load_account() python function). You need to use this flag if you intend to generate notes using real quantum hardware. Similar to the QuSequencer internal function 'loadaccount'. The script will take a few more seconds to start. For more information on how to store your IBMQ account, visit https://quantum-computing.ibm.com/lab/docs/iql/manage/account/ibmq")
    p.add_argument('--hub', nargs='?', type=str, default=None, help="IBM Quantum Provider's 'hub' argument, for backends with restricted access. Note: You NEED to use '--loadaccount' together with this flag!")
    p.add_argument('--group', nargs='?', type=str, default=None, help="IBM Quantum Provider's 'group' argument. Use this ONLY if you have multiple groups in the same IBMQ hub. Note: You NEED to use '--loadaccount' together with this flag!")
    p.add_argument('--project', nargs='?', type=str, default=None, help="IBM Quantum Provider's 'project' argument. Use this ONLY if you have multiple projects inside your group Or hub. Note: You NEED to use '--loadaccount' together with this flag!")
    args = p.parse_args()
    logger.debug(args)


    if args.hub != None:
        config.HUB = args.hub
    if args.group != None:
        config.GROUP = args.group
    if args.project != None:
        config.PROJECT = args.project
    if args.loadaccount:
        IBMQ.load_account()

    print('=====================================================')
    print('         VQH: Variational Quantum Harmonizer         ')
    print('=====================================================')

    if args.loadaccount:
        logger.debug(f'config.HUB = {config.HUB}')
        logger.debug(f'config.GROUP = {config.GROUP}')
        logger.debug(f'config.PROJECT = {config.PROJECT}')
        print(f'Loaded provider: {IBMQ.get_provider(hub=config.HUB, group=config.GROUP, project=config.PROJECT)}')

    CLI(args.backend)
