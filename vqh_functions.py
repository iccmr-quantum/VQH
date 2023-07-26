from qiskit.algorithms.minimum_eigensolvers import VQE
from qiskit.algorithms.optimizers import COBYLA
from qiskit.primitives import Estimator, Sampler
from qiskit.circuit.library import EfficientSU2
from qiskit_optimization import QuadraticProgram
from qiskit.algorithms.optimizers import COBYLA, NFT, SPSA
from qiskit.algorithms.minimum_eigensolvers import NumPyMinimumEigensolver
from qiskit.quantum_info import Operator, SparsePauliOp
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

def build_operators_from_csv(n_of_ham=2, n_of_notes=8):

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
        matrix = np.zeros((n_of_notes, n_of_notes))
        for key, value in matrix_dict.items():
            matrix[variables_index[key[0]], variables_index[key[1]]] = value
        operator = SparsePauliOp.from_operator(Operator(matrix))
        operators_variables_index.append((operator, variables_index))

    return operators_variables_index


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


def qubo_to_operator(qubo, linear_pauli='Z', external_field=0.):
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
    # external magnetic field in X direction
    pauli_list.append(('X'*num_qubits, external_field))
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


def run_sampling_vqe(ansatz, operator, optimizer, initial_point):
    binary_probabilities = []
    expectation_values = []

    def cost_function(ansatz, params, operator):
        ansatz_temp = copy.deepcopy(ansatz)
        result_estimator = estimator.run(ansatz_temp, operator, parameter_values=params).result()
        expectation_value = np.real(result_estimator.values[0])
        ansatz_temp = copy.deepcopy(ansatz)
        ansatz_temp.measure_all()
        sample = sampler.run(circuits=ansatz_temp,
                             parameter_values=params).result()
        sample_binary_probabilities = sample.quasi_dists[0].binary_probabilities(
        )
        binary_probabilities.append(sample_binary_probabilities)
        expectation_values.append(expectation_value)
        return expectation_value


    estimator = Estimator(options = {'shots': 1024})
    sampler = Sampler(options = {'shots': 1024})

    result = optimizer.minimize(lambda x: cost_function(
        ansatz=ansatz, params=x, operator=operator), x0=initial_point)

    return result, binary_probabilities, expectation_values


def binary_probabilities_to_loudness(binary_probabilities, variables_index):
    '''Convert binary probabilities to loudness'''

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
    '''Convert loudnesses to list of dicts, where each dict contains the loudness of each note for a given iteration'''
    loudness_list_of_dicts = []
    for note, loudness_list in loudnesses.items():
        for i, loudness in enumerate(loudness_list):
            if len(loudness_list_of_dicts) <= i:
                loudness_list_of_dicts.append({})
            loudness_list_of_dicts[i][note] = loudness
    return loudness_list_of_dicts


def harmonize(operators_variables_index, **kwargs):
    '''Run harmonizer algorithm for list of qubos and list of iterations. VQE is performed for the i-th qubo for i-th number of iterations.'''
    # loop over qubos
    global PATH
    QD = []
    max_state = []
    valuess = []
    loudnesses = {}
    for count, (operator, variables_index) in enumerate(operators_variables_index):
        print(f'Working on hamiltonian #{count}')
        #logger.debug(f'operator: {operator}')
        optimizer = return_optimizer(
            kwargs['optimizer_name'], kwargs['iterations'][count])
        ansatz = EfficientSU2(num_qubits=operator.num_qubits, reps=kwargs['reps'], entanglement=kwargs['entanglement'])
        if count == 0:
            initial_point = np.zeros(ansatz.num_parameters)
        # copy ansatz to avoid VQE changing it
        ansatz_temp = copy.deepcopy(ansatz)
        result, binary_probabilities, expectation_values = run_sampling_vqe(
            ansatz_temp, operator, optimizer, initial_point)
        valuess.extend(expectation_values)
        for binary_probability in binary_probabilities:
            QD.append(binary_probability)
            max_state.append(
                max(binary_probability, key=binary_probability.get))
        if count == 0:
            loudnesses = binary_probabilities_to_loudness(
                binary_probabilities, variables_index)
        else:
            loudnesses_temp = binary_probabilities_to_loudness(
                binary_probabilities, variables_index)
            for key, value in loudnesses_temp.items():
                loudnesses[key] = np.append(loudnesses[key], value)
        # set initital point for next qubo to be the optimal point of the previous qubo
        initial_point = result.x

        os.makedirs(PATH, exist_ok=True)

        with open(f"{PATH}/rawdata.json", 'w') as rawfile:
            json.dump(QD, rawfile, indent=4)
        with open(f"{PATH}/max_prob_states.txt", 'w') as maxfile:
            maxfile.write('\n'.join(max_state))
        with open(f"{PATH}/exp_values.txt", 'w') as expfile:
            for value in valuess:
                expfile.write(f"{value}\n")

    return loudnesses, valuess


def plot_values(values):
    global PATH
    plt.figure()
    # print(values)
    plt.plot(values, color='sandybrown')
    plt.savefig(f"{PATH}/values_plot", dpi=300)
    # plt.show()


def plot_loudness(loudnesses):
    global PATH
    # print(loudnesses)
    for k in loudnesses:
        plt.plot(loudnesses[k])
    plt.legend(list(loudnesses.keys()))
    plt.savefig(f"{PATH}/loudness_plot", dpi=300)
    # plt.show()


def run_vqh(sessionname):
    global PATH
    with open("vqe_conf.json") as cfile:
        config = json.load(cfile)

    PATH = f"{sessionname}/Data_{config['nextpathid']}"
    if config['interface'] == 'qubo':
        qubos = build_qubos_from_csv(config["sequence_length"], config["size"])
        operators_variables_index = [qubo_to_operator(qubo) for qubo in qubos]
    elif config['interface'] == 'operator':
        operators_variables_index = build_operators_from_csv(config["sequence_length"], config["size"])
    loudnesses, values = harmonize(operators_variables_index, **config)
    loudness_list_of_dicts = loudnesses_to_list_of_dicts(loudnesses)
    # logger.debug(loudness_list_of_dicts)

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

    return loudness_list_of_dicts, values


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
    # logger.debug(qubos)
    loudnesses, values = harmonize(qubos, **config)
    loudness_list_of_dicts = loudnesses_to_list_of_dicts(loudnesses)

    return loudness_list_of_dicts

def compute_exact_solution(operator):
    '''Minimum eigenvalue computed using NumPyMinimumEigensolver'''
    eigensolver = NumPyMinimumEigensolver()
    result = eigensolver.compute_minimum_eigenvalue(operator)
    
    return result

