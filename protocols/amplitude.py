#This file contains the new encoding protocol for the VQH. Now the notes are not encoded in qubits, but in basis statevectors of the space. Simple example: |00> = C, |01> = D, |10> = E, |11> = F. 


# -------- IMPORTS -------- (WE HAVE TO CLEAN THIS UP)

from qiskit.algorithms.minimum_eigensolvers import VQE
from qiskit.primitives import Estimator, Sampler
from qiskit.circuit.library import EfficientSU2
from qiskit_optimization import QuadraticProgram
from qiskit.algorithms.optimizers import COBYLA, NFT, SPSA, TNC, SLSQP
from qiskit.algorithms.minimum_eigensolvers import NumPyMinimumEigensolver
from qiskit.quantum_info import SparsePauliOp
from qiskit.opflow.primitive_ops import PauliSumOp
from qiskit.opflow import X, Z, I, Y
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from cycler import cycler
import numpy as np
import copy
import csv
import json
import logging
import os
import config
from shutil import copy2

from abstract_classes import VQHProtocol, QuantumHardwareInterface

mpl.rcParams['toolbar'] = 'None'
mpl.rcParams['lines.linewidth'] = .8

level = logging.WARNING

fmt = logging.Formatter('[%(levelname)s]:%(name)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(fmt)
logger = logging.getLogger(__name__)
logger.setLevel(level)
logger.addHandler(handler)


global PATH

from abstract_classes import VQHProtocol, QuantumHardwareInterface


# -------- FUNCTION DECLARATIONS --------


# STEP 1: BUILD THE HAMILTONIAN OPERATOR FROM THE CSV FILE
# The function below was copied from the 'new_encodings' branch. It may contain bugs. Needs to be tested.

def build_operators_from_csv(n_of_ham=2, n_of_notes=8):
    # Function that builds the Hamiltonian operator from the CSV file
    
    with open("operator_setup.csv", 'r') as hcsv:
        hsetup = list(csv.reader(hcsv, delimiter=','))

    #header = hsetup.pop(0)
    #logger.debug(f'CSV Header: {header}')
    #n_of_ham = int(header[1])
    #n_of_notes = int(header[2])
    operators_variables_index = []

    for h in range(n_of_ham):
        notes = hsetup.pop(h*n_of_notes)[1:]
        matrix_dict = {(row[0], notes[i]): float(
            n) for row in hsetup[h*n_of_notes:h*n_of_notes+n_of_notes] for i, n in enumerate(row[1:])}
        #logger.debug(f'QUBOS: {qubos}')
        variables_index = {notes[i]: i for i in range(n_of_notes)}

        print(matrix_dict)

        matrix = np.zeros((n_of_notes, n_of_notes))
        for key, value in matrix_dict.items():
            matrix[variables_index[key[0]], variables_index[key[1]]] = value

        print(matrix)
        operator = SparsePauliOp.from_operator(Operator(matrix))
        print(operator)
        operators_variables_index.append((operator, variables_index))

    return operators_variables_index


# STEP 2: CONVERT THE BINARY PROBABILITIES TO LOUDNESSES IN THE PRINT FORMAT

def binary_probabilities_to_loudness(binary_probabilities, variables_index):
    # Function that converts the binary probabilities to loudnesses without using marginal probabilities. It returns the loudnesses in what we call the "Print Format", which is a dictionary of lists

    # Create empty dict of lists
    loudnesses = {v: np.zeros(len(binary_probabilities)) for v in variables_index}

    # Take the coefficients of each state and create directly the loudnesses dict of lists
    for iteration, binary_probability in enumerate(binary_probabilities):
        for key, value in binary_probability.items():
            note = key
            loudnesses[note][iteration] += value
    return loudnesses

# STEP 3: CONVERT THE LOUDNESSES TO A LIST OF DICTS IN THE SONIFICATION FORMAT

def loudnesses_to_list_of_dicts(loudnesses):
    # Function that coverts loudnesses (a dict of lists) to list of dicts ("Sonification format") where each dict contains the loudness of each note/label for a given iteration

    loudness_list_of_dicts = []
    for note, loudness_list in loudnesses.items():
        for i, loudness in enumerate(loudness_list):
            if len(loudness_list_of_dicts) <= i:
                loudness_list_of_dicts.append({})
            loudness_list_of_dicts[i][note] = loudness
    return loudness_list_of_dicts

# STEP 4: PLOTS

# Plotting colorschemes
#color_mode = 'quadratic_debug'
color_mode = 'isqcmc'
#color_mode = 'isqcmc_cmajor'
#color_mode = 'isqcmc_iivvi'
global COLORSCHEME
with open('plot_colors.json', 'r') as f:
    COLORSCHEME = json.load(f)[color_mode]

def plot_values(values):
    '''Plot expectation values'''
    global PATH
    global COLORSCHEME
    vfig = plt.figure()
    # print(values)
    plt.plot(values, color=COLORSCHEME['valuecolor'])
    plt.xlabel('Iteration')
    plt.ylabel('Expectation Value <H>')
    plt.savefig(f"{PATH}/values_plot", dpi=300)
    vfig.clear()
    # plt.show()


def plot_loudness(loudnesses):
    '''Plot marginal probabilities/loudnesses'''
    global PATH
    global COLORSCHEME
    # print(loudnesses)
    fig = plt.figure()
    plt.ioff()
    rect = fig.patch
    #rect.set_alpha(0.5)
    rect.set_facecolor(COLORSCHEME['background'])
    ax = fig.add_subplot(111)
    ax.patch.set_facecolor(COLORSCHEME['facecolor'])
    ax.patch.set_alpha(COLORSCHEME['alpha'])

    # Different color styles for Debugging, Dependent Origination and ISQCMC Paper
    #ax.set_prop_cycle(cycler('color', ['#a0dece', '#f7f7c1', '#f7f797', '#f5f56c', '#26c2d4', '#f883fc', '#baba2f', '#b4d4dc', '#96961b', '#bf1fc4', '#6b6b05', '#595900']))
    ax.set_prop_cycle(cycler('color', COLORSCHEME['chordcolors']))
    #ax.set_prop_cycle(cycler('color', ['#a0dece', '#f7f7c1', '#f7f797', '#f5f56c', '#26c2d4', '#d6d649', '#baba2f', '#b4d4dc', '#96961b', '#80800d', '#6b6b05', '#595900']))
    #ax.set_prop_cycle(cycler('color', ['#93abbe', '#202a23', '#c4c9d5', '#425547', '#336068', '#577b7d', '#4e656f', '#b4d4dc']))
    
    # Save plot
    for k in loudnesses:
        plt.plot(loudnesses[k])
    plt.legend(list(loudnesses.keys()), facecolor=COLORSCHEME['legendfacecolor'], edgecolor=COLORSCHEME['legendedgecolor'], loc='lower center', bbox_to_anchor=(0.5, 0), ncols=6, fontsize=9)
    plt.xlabel('Iteration')
    plt.ylabel('"Loudnesses"')
    print(plt.ylim())

    ylimit = plt.ylim()
    yrange = ylimit[1] - ylimit[0]
    plt.ylim(bottom=ylimit[0] - 0.1*yrange)

    
    #plt.title('Marginal Distribution Evolution')
    plt.savefig(f"{PATH}/loudness_plot", dpi=300, bbox_inches='tight')
    plt.show()
    fig.clear()

# STEP 5: HARMONIZE (NEEDS CLEANING)

def harmonize(qubos, **kwargs):
    '''Run harmonizer algorithm for list of qubos and list of iterations. VQE is performed for the i-th qubo for i-th number of iterations.'''
    global PATH
    QD = []
    max_state = []
    valuess = []
    loudnesses = {}
    operatorss = []
    # loop over qubos
    os.makedirs(PATH, exist_ok=True)
    for count, qubo in enumerate(qubos):
        print(f'Working on hamiltonian #{count}')
        
        # Qubo to Hamiltonian
        operator, variables_index = qubo_to_operator(qubo, count)
        #logger.debug(f'operator: {operator}')
        
        #Optimizer
        optimizer = return_optimizer(
            kwargs['optimizer_name'], kwargs['iterations'][count])
        ansatz = EfficientSU2(num_qubits=len(
            variables_index), reps=kwargs['reps'], entanglement=kwargs['entanglement'])
        #print(f'ansatz: {ansatz.decompose().draw()}')
        #ansatz.draw()
        #ansatz.draw(output='mpl', filename=f'{PATH}/ansatz_{count}.png')
        #print(f'variables_index: {variables_index}')
        
        # Initial point
        if count == 0:
            initial_point = np.zeros(ansatz.num_parameters)
            #initial_point[0] = -np.pi*1.5
            #initial_point[0:12] = np.pi/2
            #initial_point[4] = np.pi
            #initial_point[7] = np.pi
            #initial_point[12:24] = np.pi/2
            #initial_point[24:36] = np.pi/2
            #initial_point[36:48] = np.pi/2
            #initial_point = (np.pi/4)*np.ones(ansatz.num_parameters)
            print(initial_point)
        # copy ansatz to avoid VQE changing it
        ansatz_temp = copy.deepcopy(ansatz)
        #print(f'inital point: {initial_point}')
        result, binary_probabilities, expectation_values = run_sampling_vqe(
                ansatz_temp, operator, optimizer, initial_point)
        valuess.extend(expectation_values)
        # Classical expectation value solution
        numpy_result = compute_exact_solution(operator)
        print("VQE RESULT", result.fun)
        #print("VQE BIN PROB", binary_probabilities)
        #print("VQE EXPECTATION VALUES", expectation_values)
        print("CLASSICAL SOLUTION",numpy_result.eigenvalue)

        # For each itetation, the most probable state is collected.
        # Also used for sonification mapping
        for binary_probability in binary_probabilities:
            QD.append(binary_probability)
            max_state.append(
                max(binary_probability, key=binary_probability.get))
        # Obtain probabilities
        #print("Eigenvector", binary_probabilities[:-1])
        if count == 0: 
            loudnesses = binary_probabilities_to_loudness(
                binary_probabilities, variables_index)
        else:
            loudnesses_temp = binary_probabilities_to_loudness(
                binary_probabilities, variables_index)
            for key, value in loudnesses_temp.items():
                loudnesses[key] = np.append(loudnesses[key], value)

        # Set initital point for next qubo to be the optimal point of the previous qubo
        initial_point = result.x

        operatorss.append([[n.to_instruction().params[0], operator.coeffs[i]] for i, n in enumerate(operator.to_pauli_op().oplist)])

        
        # Save data

        with open(f"{PATH}/rawdata.json", 'w') as rawfile:
            json.dump(QD, rawfile, indent=4)
        with open(f"{PATH}/max_prob_states.txt", 'w') as maxfile:
            maxfile.write('\n'.join(max_state))
        with open(f"{PATH}/exp_values.txt", 'w') as expfile:
            for value in valuess:
                expfile.write(f"{value}\n")

    with open(f"{PATH}/vqe_operators.txt", 'w') as maxfile:
        for op in operatorss:
            for pauli in op:
                maxfile.write(f'{pauli}\n')
            maxfile.write('\n')
        #json.dump(operatorss, maxfile, indent=4)
            
    return loudnesses, valuess, max_state


# STEP 6: RUN VQH. MAIN LOOP. (NEEDS CLEANING)
    
def run_vqh_amplitude(sessionname): # Function called by the main script for experiments and performance sessions
    global PATH

    # Load latest config file
    with open("vqe_conf.json") as cfile:
        config = json.load(cfile)

    PATH = f"{sessionname}_Data/Data_{config['nextpathid']}"
    # Read QUBOs from 'h_setup.csv'
    qubos = build_qubos_from_csv(config["sequence_length"], config["size"])
    # Obtain sonification parameters
    loudnesses, values, states = harmonize(qubos, **config)
    loudness_list_of_dicts = loudnesses_to_list_of_dicts(loudnesses)
    # logger.debug(loudness_list_of_dicts)


    # Save data
    with open(f"{PATH}/aggregate_data.json", 'w') as aggfile:
        json.dump(loudness_list_of_dicts, aggfile, indent=4)

    with open(f"{PATH}/vqe_conf.json", 'w') as cfile:
        json.dump(config, cfile, indent=4)

    copy2("h_setup.csv", f"{PATH}")

    norm_values = (values - min(values))/(abs(max(values)-min(values)))
    #print(type(states), type(norm_values.tolist()), loudnesses)

    """
    # Dependent Origination related code --------------------
    corrected_loudnesses = [list(i.values()) for i in loudness_list_of_dicts]
    corrected_states = [[int(j) for j in i] for i in states]
    origination = {"states": corrected_states, "amps": corrected_loudnesses, "values": norm_values.tolist()}
    
    if not os.path.exists(f"{sessionname}_Data/to_pete"):
        os.mkdir(f"{sessionname}_Data/to_pete")
    
    if not os.path.exists(f"{sessionname}_Data/to_pete/dependent_origination.json"):
        with open(f"{sessionname}_Data/to_pete/dependent_origination.json", 'w') as dofile:
        json.dump({}, dofile, indent=4)
    
    with open(f"{sessionname}_Data/to_pete/dependent_origination.json", 'r') as dofile:
        old_data = json.load(dofile)

    #print(old_data)
    #old_data[f"data_{config['nextpathid']}"] = origination
    old_data=origination
    with open(f"{sessionname}_Data/to_pete/dependent_origination.json", 'w') as dofile:
        json.dump(old_data, dofile, indent=4)
    # -------------------------------------------------------
    """
    # Prepare next run
    config['nextpathid'] += 1
    with open("vqe_conf.json", 'w') as cfile:
        json.dump(config, cfile, indent=4)

    # Plot loudnesses (Dependent Origination)
    plot_loudness(loudnesses)
    plot_values(values)
    return loudness_list_of_dicts, values


# --------------------------------------------

class AmplitudeProtocol(VQHProtocol):

    def __init__(self, name):
        self.name = name

    def run(self, sessionname):
        #config.PLATFORM = hwi
        self.data = run_vqh_amplitude(sessionname)
        return self.data

    def encode(self):
        pass

    def decode(self):
        pass

