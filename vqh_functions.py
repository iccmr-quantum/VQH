from qiskit.algorithms.minimum_eigensolvers import SamplingVQE
from qiskit.algorithms.optimizers import COBYLA
from qiskit.primitives import Sampler
from qiskit.circuit.library import EfficientSU2
from qiskit_optimization import QuadraticProgram
from qiskit.algorithms.optimizers import COBYLA, NFT, SPSA
import numpy as np
import copy
import copy


def qubo_to_operator(qubo):
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
    sampler = Sampler()
    vqe = SamplingVQE(sampler, ansatz, optimizer, initial_point=initial_point,
                      callback=store_intermediate_result)
    result = vqe.compute_minimum_eigenvalue(operator)
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


def harmonize(qubos, iterations, **kwargs):
    '''Run harmonizer algorithm for list of qubos and list of iterations. VQE is performed for the i-th qubo for i-th number of iterations.'''
    # loop over qubos
    for count, qubo in enumerate(qubos):
        operator, variables_index = qubo_to_operator(qubo)
        optimizer = return_optimizer(
            kwargs['optimizer_name'], iterations[count])
        ansatz = EfficientSU2(num_qubits=len(
            variables_index), reps=kwargs['reps'], entanglement=kwargs['entanglement'])
        if count == 0:
            initial_point = np.zeros(ansatz.num_parameters)
        # copy ansatz to avoid VQE changing it
        ansatz_temp = copy.deepcopy(ansatz)
        result, intermediate_info = run_sampling_vqe(
            ansatz_temp, operator, optimizer, initial_point)
        parameterss = intermediate_info['parameterss']
        quasi_dists = []
        # compute quasi distributions for each iteration of VQE
        for parameters in parameterss:
            ansatz_temp = copy.deepcopy(ansatz)
            ansatz_temp.measure_all()
            quasi_dist = intermediate_parameters_to_quasi_dist(
                ansatz_temp, parameters)
            quasi_dists.append(quasi_dist)
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
    return loudnesses


def test_harmonize():

    # specify all possible notes. This is one octave. For more octaves, just add more notes.
    notes = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
    config = {
        'reps': 1,
        'entanglement': 'linear',
        'optimizer_name': 'COBYLA'
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
    iterations = [64, 64, 64, 64]

    loudnesses = harmonize(qubos, iterations, **config)
    loudness_list_of_dicts = loudnesses_to_list_of_dicts(loudnesses)

    return loudness_list_of_dicts



