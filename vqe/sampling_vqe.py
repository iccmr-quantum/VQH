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
from shutil import copy2

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

def run_sampling_vqe(ansatz, operator, optimizer, initial_point):
    '''Runs VQE and samples the wavefunction at each iteration'''


    binary_probabilities = []
    expectation_values = []

    #VQE Iteration.
    def cost_function(ansatz, params, operator):
        ansatz_temp = copy.deepcopy(ansatz)
        result_estimator = estimator.run(ansatz_temp, operator, parameter_values=params).result()
        expectation_value = np.real(result_estimator.values[0])
        ansatz_temp = copy.deepcopy(ansatz)
        #print(f'Parameters: {params}')
        ansatz_temp.measure_all()
        sample = sampler.run(circuits=ansatz_temp,
                             parameter_values=params).result()
        sample_binary_probabilities = sample.quasi_dists[0].binary_probabilities(
        )
        #print(f'Sample: {sample_binary_probabilities}')
        #for key in sample_binary_probabilities:
            #print(operator.eval(key))
        # The statevector and expectation values are collected at each iteration
        # for sonification
        binary_probabilities.append(sample_binary_probabilities)
        expectation_values.append(expectation_value)
        return expectation_value

    #sampler = Sampler(
    #    backend_options={'method': 'automatic',
    #                     'noise_model': None, 'basis_gates': None, 'coupling_map': None},
    #    run_options={'shots': 1024})

    estimator = Estimator(options = {'shots': 1024})
    sampler = Sampler(options = {'shots': 1024})

    result = optimizer.minimize(lambda x: cost_function(
        ansatz=ansatz, params=x, operator=operator), x0=initial_point)

    return result, binary_probabilities, expectation_values

