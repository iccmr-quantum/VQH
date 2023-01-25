from qiskit import Aer
from qiskit.algorithms.minimum_eigensolvers import VQE
from qiskit.algorithms.optimizers import COBYLA
from qiskit.primitives import BackendEstimator, BackendSampler
from qiskit.circuit.library import EfficientSU2
from qiskit_optimization import QuadraticProgram
import numpy as np
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
    backend = Aer.get_backend('qasm_simulator')
    estimator = BackendEstimator(backend)
    vqe = VQE(estimator, ansatz, optimizer, initial_point=initial_point,
              callback=store_intermediate_result)
    result = vqe.compute_minimum_eigenvalue(operator)
    intermediate_info = {'eval_counts': eval_counts, 'values': values,
                         'parameterss': parameterss, 'metadatas': metadatas}
    return result, intermediate_info


def sample_from_intermediate_info(ansatz, params):

    backend = Aer.get_backend('qasm_simulator')
    sampler = BackendSampler(backend)
    job = sampler.run(ansatz, parameter_values=params)
    result = job.result()
    quasi_dists = result.quasi_dists
    return quasi_dists


def harmonize():

    # example simple c major. Different Hamiltonians with superposition of chords as ground state are possible.
    # beneficial negative weights for desired notes
    c_major = {
        ('c', 'c'): -1.,
        ('e', 'e'): -1.,
        ('g', 'g'): -1.,
    }
    # penalty for other notes
    notes = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
    for note in notes:
        if (note, note) not in c_major:
            c_major[(note, note)] = 1.

    operator, variables_index = qubo_to_operator(c_major)
    # different ansatze different sounds
    ansatz = EfficientSU2(num_qubits=len(notes), reps=1)
    # different optimizers different sound
    optimizer = COBYLA(maxiter=64)
    # start with silence
    initial_point = np.zeros(ansatz.num_parameters)
    ansatz_temp = copy.deepcopy(ansatz)
    result, intermediate_info = run_vqe(
        ansatz_temp, operator, optimizer, initial_point)
    parameterss = intermediate_info['parameterss']
    quasi_dists = []
    for parameters in parameterss:
        ansatz_temp = copy.deepcopy(ansatz)
        ansatz_temp.measure_all()
        quasi_dist = sample_from_intermediate_info(ansatz_temp, parameters)[0]
        quasi_dist = quasi_dist.binary_probabilities()
        quasi_dists.append(quasi_dist)
    print(variables_index)
    print(quasi_dists[-1])
    return quasi_dists

if __name__ == '__main__':
    pass 
