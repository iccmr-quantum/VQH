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
from vqe.vqe_experiments import SamplingVQE

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


# --------------------- Plotting colorschemes
#color_mode = 'quadratic_debug'
#color_mode = 'isqcmc'
#color_mode = 'isqcmc_cmajor'
color_mode = 'isqcmc_iivvi'
global COLORSCHEME
with open('protocols/plot_colors.json', 'r') as f:
    COLORSCHEME = json.load(f)[color_mode]

def build_qubos_from_csv(n_of_ham=4, n_of_notes=12):
    '''Builds a list of qubos from a csv file. 
    The csv file must be in the same folder as this script and must be named 
    "h_setup.csv". The csv file must have the following format:
    
    h1,label1,label2,label3,...,labeln
    label1,c11,c12,c13,...,c1n
    label2,c21,c22,c23,...,c2n
    label3,c31,c32,c33,...,c3n
    ...
    labeln,cn1,cn2,cn3,...,cnn
    h2,label1,label2,label3,...,labeln
    label1,c11,c12,c13,...,c1n
    ...
    
    where h1, h2, ... are the QUBO matrices names and label1, label2, ... are the
    note labels used by the sonification.

    The function returns a list of qubos of the form:
    [{(note_1, note_2): coupling, ...}, ...]
    where note_1 and note_2 are the note labels with its corresponding coupling
    coefficients.
    '''

    with open("h_setup.csv", 'r') as hcsv:
        hsetup = list(csv.reader(hcsv, delimiter=','))

    #header = hsetup.pop(0)
    #logger.debug(f'CSV Header: {header}')
    #n_of_ham = int(header[1])
    #n_of_notes = int(header[2])
    qubos = []
    for h in range(n_of_ham):
        notes = hsetup.pop(h*n_of_notes)[1:]
        qubos.append({(row[0], notes[i]): float(n) for row in hsetup[h*n_of_notes:h*n_of_notes+n_of_notes] for i, n in enumerate(row[1:])})
    logger.debug(f'QUBOS: {qubos}')

    return qubos

def H_Ising(N,J,hx):# Arianna Crippa's Ising model implementation for comparison and debugging
    # Ising model H
    H_Ising=0
    for n in range(1,N):
        H_Ising+=-J* ((I^(n-1))^Z^Z^(I^(N-n-1)))
    #H_Ising+=-J*(Z^(I^(N-2))^Z)
    for i in range(N):
        H_Ising+=-hx* ((I^(i))^X^(I^(N-i-1)))
    for i in range(N):
        H_Ising+=-0.1* ((I^(i))^Z^(I^(N-i-1))) 

    return H_Ising

def qubo_to_operator(qubo, count, linear_pauli='Z', external_field=+0):
    '''Translates qubo problems of format {(note_1, note_2): coupling, ...} to operators to be used in VQE.
    This function can yield non-diagonal Hamiltonians.
    
    The resulting Hamitonian H is equal to the QUBO Q up to a constant factor 
    and a constant shift that do not impact the optimization
    H = 4*Q + const
    Q = H/4 - const/4 = operator + offset
    
    '''
   # First, we need to create a dictionary that maps the variables to their index in the operator
   # We make sure that the qubo is symmetric and that we only have one term for each pair of variables
    qubo_index = {}
    variables_index = {}
    count_index = 0
    for key, value in qubo.items():
        if key[0] not in variables_index:
            variables_index[key[0]] = count_index
            count_index += 1
        if key[1] not in variables_index:
            variables_index[key[1]] = count_index
            count_index += 1
        if key[0] == key[1]:
            i = variables_index[key[0]]
            qubo_index[(i, i)] = value
        elif key[0] != key[1]:
            i = variables_index[key[0]]
            j = variables_index[key[1]]
            if (j, i) in qubo_index and qubo_index[(j, i)] != value:
                raise ValueError(
                    'QUBO is not symmetric. (i, j) and (j, i) have different values')
            if (j, i) in qubo_index:
                logging.info(
                    'Ignoring term (i, j) because (j, i) is already in qubo')
            else:
                qubo_index[(i, j)] = value
    # Now, we can create the Hamiltonian in terms of pauli strings
    num_qubits = len(variables_index)
    paulis = {}
    const = 0
    for key, value in qubo_index.items():
        if key[0] == key[1]:
            i = key[0]
            pauli = 'I'*(num_qubits-i-1) + linear_pauli + 'I'*i
            if pauli in paulis:
                paulis[pauli] += -2*value
            else:
                paulis[pauli] = -2*value
            const += -2*value
        elif key[0] != key[1]:
            i = key[0]
            j = key[1]
            if i > j:
                i, j = j, i
            pauli = 'I'*(num_qubits-j-1) + 'Z' + \
                'I'*(j-i-1) + 'Z' + 'I'*i
            paulis[pauli] = value
            pauli = 'I'*(num_qubits-i-1) + linear_pauli + 'I'*i
            if pauli in paulis:
                paulis[pauli] += -value
            else:
                paulis[pauli] = -value
            pauli = 'I'*(num_qubits-j-1) + linear_pauli + 'I'*j
            if pauli in paulis:
                paulis[pauli] += -value
            else:
                paulis[pauli] = -value
            const += -value
    pauli_list = [(k, v) for k, v in paulis.items()]
    #pauli_list = [(k, round(v/4,8)) for k, v in paulis.items()]
    # external magnetic field in X direction
    for i in range(num_qubits):
        paulix = 'I'*i + 'X' + 'I'*(num_qubits-i-1)
        pauli_list.append((paulix, external_field))
        #pauli_list.append((paulix, external_field-0.2*count))
    operator = PauliSumOp(SparsePauliOp.from_list(pauli_list))
    offset = -const/4 # for future reference
    print(f'Operator: \n{operator}')
     
    # Compare H with Arianna's Ising operator
    operator2 = H_Ising(12, 1, external_field)
    
    return operator, variables_index


def return_optimizer(optimizer_name, maxiter):
    '''Convenience function to return optimizer object'''

    if optimizer_name == 'SPSA':
        optimizer = SPSA(maxiter=maxiter)
    elif optimizer_name == 'COBYLA':
        optimizer = COBYLA(maxiter=maxiter)
    elif optimizer_name == 'NFT':
        optimizer = NFT(maxiter=maxiter)
    elif optimizer_name == 'TNC':
        optimizer = NFT(maxiter=maxiter)
    elif optimizer_name == 'SLSQP':
        optimizer = SLSQP(maxiter=maxiter)

    return optimizer


def binary_probabilities_to_loudness(binary_probabilities, variables_index):
    ''' Obtain marginal probabilities for each note, interpreted as loudnesses'''

    loudnesses = {v: np.zeros(len(binary_probabilities))
                  for v in variables_index}
    variables_index_invert = {v: k for k, v in variables_index.items()}
    for iteration, binary_probability in enumerate(binary_probabilities):
        for key, value in binary_probability.items():
            for index, bit in enumerate(key[::-1]):
                if bit == '1':
                    note = variables_index_invert[index]
                    loudnesses[note][iteration] += value
    return loudnesses


def loudnesses_to_list_of_dicts(loudnesses):
    '''Convert marginal probabilities/loudnesses (a dict of lists) to list of dicts,
    where each dict contains the loudness of each note/label for a given iteration'''
    loudness_list_of_dicts = []
    for note, loudness_list in loudnesses.items():
        for i, loudness in enumerate(loudness_list):
            if len(loudness_list_of_dicts) <= i:
                loudness_list_of_dicts.append({})
            loudness_list_of_dicts[i][note] = loudness
    return loudness_list_of_dicts

#def compute_exact_solution(operator):
#    '''Minimum eigenvalue computed using NumPyMinimumEigensolver
#    for comparison with VQE'''
#    eigensolver = NumPyMinimumEigensolver()
#    result = eigensolver.compute_minimum_eigenvalue(operator)
#
#    return result

# Main function
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
        vqe_experiment = SamplingVQE()
        vqe_experiment.update_config()
        result, binary_probabilities, expectation_values = vqe_experiment.run_vqe(
                ansatz_temp, operator, optimizer, initial_point)
        valuess.extend(expectation_values)
        # Classical expectation value solution
        numpy_result = vqe_experiment.compute_exact_solution(operator)
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
        # Obtain marginal probabilities
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
    ax.set_prop_cycle(cycler('color', COLORSCHEME['chordcolors']))
    
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


def run_vqh(sessionname): # Function called by the main script for experiments and performance sessions
    global PATH

    # Load latest config file
    with open("vqe_conf.json") as cfile:
        vqe_config = json.load(cfile)

    PATH = f"{sessionname}_Data/Data_{vqe_config['nextpathid']}"
    # Read QUBOs from 'h_setup.csv'
    qubos = build_qubos_from_csv(vqe_config["sequence_length"], vqe_config["size"])
    # Obtain sonification parameters
    loudnesses, values, states = harmonize(qubos, **vqe_config)
    loudness_list_of_dicts = loudnesses_to_list_of_dicts(loudnesses)
    # logger.debug(loudness_list_of_dicts)


    # Save data
    with open(f"{PATH}/aggregate_data.json", 'w') as aggfile:
        json.dump(loudness_list_of_dicts, aggfile, indent=4)

    with open(f"{PATH}/vqe_conf.json", 'w') as cfile:
        json.dump(vqe_config, cfile, indent=4)

    copy2("h_setup.csv", f"{PATH}")

    norm_values = (values - min(values))/(abs(max(values)-min(values)))
    #print(type(states), type(norm_values.tolist()), loudnesses)

#    # Dependent Origination related code --------------------
#    corrected_loudnesses = [list(i.values()) for i in loudness_list_of_dicts]
#    corrected_states = [[int(j) for j in i] for i in states]
#    origination = {"states": corrected_states, "amps": corrected_loudnesses, "values": norm_values.tolist()}
#    
#    if not os.path.exists(f"{sessionname}_Data/to_pete"):
#        os.mkdir(f"{sessionname}_Data/to_pete")
#    
#    if not os.path.exists(f"{sessionname}_Data/to_pete/dependent_origination.json"):
#        with open(f"{sessionname}_Data/to_pete/dependent_origination.json", 'w') as dofile:
#        json.dump({}, dofile, indent=4)
#    
#    with open(f"{sessionname}_Data/to_pete/dependent_origination.json", 'r') as dofile:
#        old_data = json.load(dofile)
#
#    #print(old_data)
#    #old_data[f"data_{vqe_config['nextpathid']}"] = origination
#    old_data=origination
#    with open(f"{sessionname}_Data/to_pete/dependent_origination.json", 'w') as dofile:
#        json.dump(old_data, dofile, indent=4)

    # -------------------------------------------------------

    # Prepare next run
    vqe_config['nextpathid'] += 1
    with open("vqe_conf.json", 'w') as cfile:
        json.dump(vqe_config, cfile, indent=4)

    # Plot loudnesses (Dependent Origination)
    plot_loudness(loudnesses)
    #plot_values(values)
    return loudness_list_of_dicts, values, states



class HarpProtocol(VQHProtocol):

    def __init__(self, name):
        self.name = name
        self.data = None

    def run(self, sessionname):
        #config.PLATFORM = hwi
        self.data = run_vqh(sessionname)
        return self.data

    def encode(self):
        pass

    def decode(self):
        pass


