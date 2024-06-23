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


# Logging and global variables
import logging
import sys
import time

# Global variables
import config

from core.vqh_core import VQHCore, VQHController

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
import multiprocessing
import threading

from control_to_setup2 import json_to_csv

level = logging.WARNING

fmt = logging.Formatter('[%(levelname)s]:%(name)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(fmt)
logger = logging.getLogger(__name__)
logger.setLevel(level)
logger.addHandler(handler)

global progQuit
progQuit = False
comp = True
last = False
reset = True
port = ''

VALID_COMMANDS = ['q', 'quit', 'stop', 'map', 'mapfile', 'realtime', 'rt', 'init', 'source', 'queue']


# Play sonification from a previously generated file
def playfile(num, folder, son_type=1):
    path = f"{folder}/Data_{num}"
    with open(f"{path}/aggregate_data.json") as afile:
        dist = json.load(afile)
    with open(f"{path}/exp_values.txt") as efile:
        vals = [float(val.rstrip()) for val in efile]
    sc.sonify(dist, vals, son_type)



def is_command(cmd):
    return cmd.split(' ')[0] in VALID_COMMANDS
    
def update_qubo_visualization(pquit):
    while not pquit.value:
        try:
            json_to_csv('midi/qubo_control.json', 'output.csv')
            time.sleep(0.1)
        except Exception:
            continue

# Function to print all currently running threads
def list_active_threads():
    for thread in threading.enumerate():
        print(f"Thread Name: {thread.name}, Alive: {thread.is_alive()}")


def CLI(vqh_core, vqh_controller):
    global progQuit, comp, last, reset, generated_quasi_dist, comp_events
    generated_quasi_dist = []
    

    # prompt preparation
    session = PromptSession()
    validator = Validator.from_callable(is_command, error_message='This command does not exist (or is deprecated). Check for mispellings.')

    while not progQuit:
        try:
      
            #CLI Commands
            x = session.prompt(f' VQH=> ', validator=validator, validate_while_typing=False)
            x = x.split(' ')
            if x[0] == 'next' or x[0] == 'n':
                raise NotImplementedError(f'Score Features not implemented yet for the VQH!')


            elif x[0] == 'quit' or x[0] == 'q':
                progQuit=True
                continue

            
            elif x[0] == 'stop':
                vqh_controller.stop_synth()
                print('Stopping Sounds...')


            elif x[0] == 'realtime' or x[0] == 'rt':
                print('')
                vqh_controller.start()

            elif x[0] == 'init':
                print(' Setting up VQH realtime session...')
                print(f' Son:{type(vqh_core.son_type)}')
                if len(x) >= 2:
                    vqh_core.son_type = int(x[1])
                if len(x) >= 3:
                    vqh_core.strategy_type = x[2]
                if len(x) >= 4:
                    if x[2] == 'file':
                        #print(f'Extra argument for file mode: {x[2]}. Ignoring...')
                        vqh_core.method_name = int(x[3])
                    else:
                        vqh_core.method_name = x[3]
                if len(x) >= 5:
                    vqh_core.rt_mode = int(x[4])
                print(f'Sonification type: {vqh_core.son_type}: {vqh_core.sonification_library._library[vqh_core.son_type]["description"]} ({vqh_core.sonification_library._library[vqh_core.son_type]["interface"].upper()})')
                print(f'Strategy type: {vqh_core.strategy_type}')
                print(f'Method name: {vqh_core.method_name}')
                vqh_controller.init_core()

            # Generate sonification data manually from a quantum process
            elif x[0] == 'source':
                if len(x) == 1:
                    vqh_controller.run_source()
                elif len(x) == 2:
                    vqh_controller.run_source(x[1])
                elif len(x) == 3:
                    vqh_controller.run_source(x[1], x[2])

            # Sonify the last generated result
            elif x[0] == 'map':
                if len(x) == 1:
                    vqh_controller.run_mapper()
                elif len(x) == 2:
                    vqh_controller.run_mapper(int(x[1]))

            elif x[0] == 'mapfile':
                if len(x) == 2:
                    print('Mapping last generated file...')
                    vqh_controller.run_source('file')
                    vqh_core.source.thread.join()
                    vqh_controller.run_mapper(int(x[1]))
                elif len(x) == 3:
                    vqh_controller.run_source('file', x[1])
                    vqh_core.source.thread.join()
                    vqh_controller.run_mapper(int(x[2]))

            elif x[0] == 'queue':
                if len(x) == 1:
                    vqh_controller.print_queue()
                elif len(x) == 2 and x[1] == 'reset':
                    vqh_controller.queue_reset()

            else:
                print(f'Not a valid input - {x}')

        except KeyboardInterrupt:

            print('Keyboard Interrupt!')
            try:
                vqh_controller.clean()
            except Exception:
                pass
            progQuit = True
            print('Exiting VQH...')
            time.sleep(1)
            print('Goodbye!')
            

if __name__ == '__main__':


    descr = 'Variational Quantum Harmonizer\n\
- QUBO problem editor can befound at "h_setup_rt.csv"\n\
     \n\n\
Internal VQH functions:\n\
=> source               Generates sonification data from a problem - or.\n\
                        reads data from a file. The first optional argument\n\
                        is the strategy type (file or process). The second\n\
                        argument is the method name (specifies the problem\n\
                        or file).\n\
=> map                  Triggers a sonification method using the current \n\
                        data loaded into the session queue. The first \n\
                        optional argument is the sonification mapping index.\n\
=> mapfile              First runs a source command to load data from a file\n\
                        into the session queue, then triggers a sonification\n\
                        mapping. User can specify the file name and mapping\n\
                        index as optional arguments.\n\
=> queue                Prints the current session queue. The optional\n\
                        argument "reset" clears the queue.\n\
=> init                 Initializes a session in Realtime mode. The first\n\
                        optional argument is the sonification type. The\n\
                        second optional argument is the strategy type. The\n\
                        third optional argument is the method name. The\n\
                        fourth optional argument is the execution mode.\n\
=> realtime, rt         Starts the sonification process in Realtime mode.\n\
=> stop                 Stops all sounds.\n\
=> quit, q              Exits the program.\n '


    p = argparse.ArgumentParser(description=descr, formatter_class=RawDescriptionHelpFormatter)

    p.add_argument('sessionpath', type=str, nargs='?', default='Session', help="Folder name where VQE data will be stored/read")
    p.add_argument('platform', type=str, nargs='?', default='local', help="Quantum Platform provider used (Local, IQM, IBMQ). Default is 'local'.")
    p.add_argument('method', type=str, nargs='?', default='qubo', help="Process method to be sonified, or file index to read from. Default is 'qubo'.")
    p.add_argument('exec_mode', type=str, nargs='?', default='fixed', help="Source execution mode. Default is 'fixed'.")
    p.add_argument('mapping', type=int, nargs='?', default=5, help="Sonification routine. Default is 5 (Raw OSC).")
    args = p.parse_args()
    logger.debug(args)


    config.SESSIONPATH = args.sessionpath
    config.HW_INTERFACE = args.platform

    if args.exec_mode == 'file':
        vqh_core = VQHCore('file', args.method, args.platform, args.mapping, args.exec_mode, args.sessionpath)
    else:
        vqh_core = VQHCore('process', args.method, args.platform, args.mapping, args.exec_mode, args.sessionpath)
    vqh_controlller = VQHController(vqh_core)


    print('=====================================================')
    print('      VQH: Variational Quantum Harmonizer  - v0.3.0  ')
    print('          by itaborala, schwaeti, cephasteom,        ')
    print('               maria-aguado, ariannacrippa           ')
    print('                     2023 - 2024                     ') 
    print('                  DESY + ICCMR + CyI                 ')
    print('               karljansen + iccmr-quantum            ')
    print('         https://github.com/iccmr-quantum/VQH        ')
    print('=====================================================')

    # Run CLI
    pquit = multiprocessing.Value('b', False)
    qubo_vis = multiprocessing.Process(target=update_qubo_visualization, args=(pquit,))
    qubo_vis.start()

    CLI(vqh_core, vqh_controlller)
    pquit.value = True
    print('Exited VQH')
    list_active_threads()
