from qiskit.algorithms.minimum_eigensolvers import VQE
from qiskit.algorithms.optimizers import COBYLA
from qiskit.primitives import Estimator, Sampler
from qiskit.circuit.library import EfficientSU2
from qiskit_optimization import QuadraticProgram
from qiskit.algorithms.optimizers import COBYLA, NFT, SPSA
from qiskit.quantum_info import SparsePauliOp
from qiskit.opflow.primitive_ops import PauliSumOp
import matplotlib.pyplot as plt
import numpy as np
import copy
import csv
import json
import logging
import os
from shutil import copy2

level = logging.DEBUG

fmt = logging.Formatter('[%(levelname)s]:%(name)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(fmt)
logger = logging.getLogger(__name__)
logger.setLevel(level)
logger.addHandler(handler)


global PATH
def build_qubos_from_csv(n_of_ham=4, n_of_notes=12):

    with open("h_setup.csv", 'r') as hcsv:
        hsetup = list(csv.reader(hcsv, delimiter=','))

    #header = hsetup.pop(0)
    #logger.debug(f'CSV Header: {header}')
    #n_of_ham = int(header[1])
    #n_of_notes = int(header[2])
    qubos = []
    for h in range(n_of_ham):
        notes = hsetup.pop(h*n_of_notes)[1:]
        qubos.append({(row[0], notes[i]): float(
            n) for row in hsetup[h*n_of_notes:h*n_of_notes+n_of_notes] for i, n in enumerate(row[1:])})
    #logger.debug(f'QUBOS: {qubos}')

    return qubos


def qubo_to_operator_quadratic_program(qubo):
    '''Translate qubo of format {(note_1, note_2): coupling, ...} to operator to be used in VQE this yields diagonal Hamiltonians only'''

    notes = []
    linear = {}
    quadratic = {}
    mod = QuadraticProgram('variational_quantum_harmonizer')
    for key, value in qubo.items():
        if key[0] not in notes:
            notes.append(key[0])
            mod.binary_var(name=key[0])
        if key[1] not in notes:
            notes.append(key[1])
            mod.binary_var(name=key[1])
        if key[0] == key[1]:
            linear.update({key[0]: value})
        else:
            quadratic.update({key: value})
    variables_index = mod.variables_index
    mod.minimize(linear=linear, quadratic=quadratic)
    operator, offset = mod.to_ising()

    return operator, variables_index


def qubo_to_operator(qubo, linear_pauli='Z'):
    '''Translate qubo of format {(note_1, note_2): coupling, ...} to operator to be used in VQE. This function can yield non-diagonal Hamiltonians.'''

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
    # pauli_list = [(k, v) for k, v in paulis.items()]
    # H = PauliSumOp(SparsePauliOp.from_list(pauli_list))
    # This Hamitonian H is equal to the QUBO Q up to a constant factor and a constant shift that do not impact the optimization
    # H = 4*Q + const
    # Q = H/4 - const/4 = operator + offset
    pauli_list = [(k, v/4) for k, v in paulis.items()]
    operator = PauliSumOp(SparsePauliOp.from_list(pauli_list))
    offset = -const/4

    return operator, variables_index


def return_optimizer(optimizer_name, maxiter):
    '''Convenience function to return optimizer object'''

    if optimizer_name == 'SPSA':
        optimizer = SPSA(maxiter=maxiter)
    elif optimizer_name == 'COBYLA':
        optimizer = COBYLA(maxiter=maxiter)
    elif optimizer_name == 'NFT':
        optimizer = NFT(maxiter=maxiter)

    return optimizer


def run_vqe(ansatz, operator, optimizer, initial_point):
    '''Run VQE with given ansatz, operator, optimizer and initial point, store intermediate results for every iteration'''

    eval_counts = []
    parameterss = []
    values = []
    metadatas = []

    def store_intermediate_result(eval_count, parameters, value, metadata):
        eval_counts.append(eval_count)
        parameterss.append(parameters)
        values.append(value)
        metadatas.append(metadata)
    estimator = Estimator()
    vqe = VQE(estimator, ansatz, optimizer, initial_point=initial_point,
              callback=store_intermediate_result)
    result = vqe.compute_minimum_eigenvalue(operator)
    #print(result)
    intermediate_info = {'eval_counts': eval_counts, 'values': values,
                         'parameterss': parameterss, 'metadatas': metadatas}
    return result, intermediate_info


def intermediate_parameters_to_quasi_dist(ansatz, parameters):
    '''Convert intermediate results to quasi distributions. This is done by sampling from the ansatz with the parameters obtained from each iteration of VQE'''
    sampler = Sampler()
    job = sampler.run(ansatz, parameter_values=parameters)
    result = job.result()
    quasi_dist = result.quasi_dists[0]
    quasi_dist = quasi_dist.binary_probabilities()
    return quasi_dist


def quasi_dists_to_loudness(quasi_dists, variables_index):
    '''Convert list of quasi distributions to loudness'''

    loudnesses = {v: np.zeros(len(quasi_dists)) for v in variables_index}
    variables_index_invert = {v: k for k, v in variables_index.items()}
    for iteration, quasi_dist in enumerate(quasi_dists):
        for key, value in quasi_dist.items():
            for index, bit in enumerate(key[::-1]):
                if bit == '1':
                    note = variables_index_invert[index]
                    loudnesses[note][iteration] += value
    return loudnesses


def loudnesses_to_list_of_dicts(loudnesses):
    '''Convert loudnesses to list of dicts, where each dict contains the loudness of each note for a given iteration'''
    loudness_list_of_dicts = []
    for note, loudness_list in loudnesses.items():
        for i, loudness in enumerate(loudness_list):
            if len(loudness_list_of_dicts) <= i:
                loudness_list_of_dicts.append({})
            loudness_list_of_dicts[i][note] = loudness
    return loudness_list_of_dicts


def harmonize(qubos, **kwargs):
    '''Run harmonizer algorithm for list of qubos and list of iterations. VQE is performed for the i-th qubo for i-th number of iterations.'''
    # loop over qubos
    global PATH
    QD = []
    max_state = []
    valuess = []
    for count, qubo in enumerate(qubos):
        print(f'Working on hamiltonian #{count}')
        operator, variables_index = qubo_to_operator(qubo)
        #logger.debug(f'operator: {operator}')
        optimizer = return_optimizer(
            kwargs['optimizer_name'], kwargs['iterations'][count])
        ansatz = EfficientSU2(num_qubits=len(
            variables_index), reps=kwargs['reps'], entanglement=kwargs['entanglement'])
        if count == 0:
            initial_point = np.zeros(ansatz.num_parameters)
        # copy ansatz to avoid VQE changing it
        ansatz_temp = copy.deepcopy(ansatz)
        result, intermediate_info = run_vqe(
            ansatz_temp, operator, optimizer, initial_point)
        parameterss = intermediate_info['parameterss']
        valuess.extend(intermediate_info['values'])
        quasi_dists = []
        # compute quasi distributions for each iteration of VQE
        for parameters in parameterss:
            ansatz_temp = copy.deepcopy(ansatz)
            ansatz_temp.measure_all()
            quasi_dist = intermediate_parameters_to_quasi_dist(
                ansatz_temp, parameters)
            quasi_dists.append(quasi_dist)
            max_state.append(max(quasi_dist, key=quasi_dist.get))
            #logger.debug(f'Max value state: {max(quasi_dist, key=quasi_dist.get)}')
            QD.append(quasi_dist)
        if count == 0:
            loudnesses = quasi_dists_to_loudness(
                quasi_dists, variables_index)
        else:
            loudnesses_temp = quasi_dists_to_loudness(
                quasi_dists, variables_index)
            for key, value in loudnesses_temp.items():
                loudnesses[key] = np.append(loudnesses[key], value)
        # set initital point for next qubo to be the optimal point of the previous qubo
        initial_point = result.optimal_point
        
        os.makedirs(PATH, exist_ok=True)

        with open(f"{PATH}/rawdata.json", 'w') as rawfile:
            json.dump(QD, rawfile, indent=4)
        with open(f"{PATH}/max_prob_states.txt", 'w') as maxfile:
            maxfile.write('\n'.join(max_state))
    return loudnesses, valuess

def plot_values(values):
    global PATH
    plt.figure()
    #print(values)
    plt.plot(values, color='sandybrown')
    plt.savefig(f"{PATH}/values_plot", dpi=300)
    #plt.show()

def plot_loudness(loudnesses):
    global PATH
    #print(loudnesses)
    for k in loudnesses:
        plt.plot(loudnesses[k])
    plt.legend(list(loudnesses.keys()))
    plt.savefig(f"{PATH}/loudness_plot", dpi=300)
    #plt.show()

def run_vqh(sessionname):
    global PATH
    with open("vqe_conf.json") as cfile:
        config = json.load(cfile)

    PATH = f"{sessionname}/Data_{config['nextpathid']}"
    qubos = build_qubos_from_csv(config["sequence_length"], config["size"])
    loudnesses, values = harmonize(qubos, **config)
    loudness_list_of_dicts = loudnesses_to_list_of_dicts(loudnesses)
    #logger.debug(loudness_list_of_dicts)

    plot_loudness(loudnesses)
    plot_values(values)
    with open(f"{PATH}/aggregate_data.json", 'w') as aggfile:
        json.dump(loudness_list_of_dicts, aggfile, indent=4)

    with open(f"{PATH}/vqe_conf.json", 'w') as cfile:
        json.dump(config, cfile, indent=4)

    copy2("h_setup.csv", f"{PATH}")

    config['nextpathid'] += 1
    with open("vqe_conf.json", 'w') as cfile:
        json.dump(config, cfile, indent=4)

    return loudness_list_of_dicts


def test_harmonize():

    global PATH

    PATH = "Data/Test"
    # specify all possible notes. This is one octave. For more octaves, just add more notes.
    notes = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
    config = {
        'reps': 1,
        'entanglement': 'linear',
        'optimizer_name': 'COBYLA',
        'iterations': [64, 64, 64, 64]
    }
    # example simple c major. Different Hamiltonians with superposition of chords as ground state are possible.
    # beneficial negative weights for desired notes
    c_major = {
        ('c', 'c'): -1.,
        ('e', 'e'): -1.,
        ('g', 'g'): -1.,
    }
    # penalty for other notes
    # make sure all notes are defined in the qubo
    notes = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
    for note in notes:
        if (note, note) not in c_major:
            c_major[(note, note)] = 1.

    f_major = {
        ('f', 'f'): -1.,
        ('a', 'a'): -1.,
        ('c', 'c'): -1.,
    }
    for note in notes:
        if (note, note) not in f_major:
            f_major[(note, note)] = 1.

    g_major = {
        ('g', 'g'): -1.,
        ('b', 'b'): -1.,
        ('d', 'd'): -1.,
    }
    for note in notes:
        if (note, note) not in g_major:
            g_major[(note, note)] = 1.

    qubos = [c_major, g_major, f_major, c_major]
    #logger.debug(qubos)
    loudnesses, values = harmonize(qubos, **config)
    loudness_list_of_dicts = loudnesses_to_list_of_dicts(loudnesses)

    return loudness_list_of_dicts
