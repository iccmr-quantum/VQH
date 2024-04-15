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

class SamplingVQE():


    def __init__(self):
        self.config = {}

    def update_config(self):
        with open("vqe_conf.json", 'r') as cfile:
            self.config = json.load(cfile)



    def run_vqe(self, ansatz, operator, optimizer, initial_point, callback=None):
        '''Runs VQE and samples the wavefunction at each iteration'''


        binary_probabilities = []
        expectation_values = []

        #VQE Iteration.
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
            # The statevector and expectation values are collected at each iteration
            # for sonification
            binary_probabilities.append(sample_binary_probabilities)
            expectation_values.append(expectation_value)
            # DECODE SAMPLE HERE?
            if callback:
                # Broadcast decoded sample
                callback[0](sample_binary_probabilities, expectation_value, callback[1])
            return expectation_value

        print(f'Hardware Interface: {config.PLATFORM}')
        #print(f'Platform: {config.PLATFORM.backend}')

        estimator = Estimator(options = {'backend': config.PLATFORM.backend, 'shots': 1024})

        sampler = Sampler(options = {'shots': 1024})

        result = optimizer.minimize(lambda x: cost_function(
            ansatz=ansatz, params=x, operator=operator), x0=initial_point)

        return result, binary_probabilities, expectation_values

    def compute_exact_solution(self, operator):
        '''Minimum eigenvalue computed using NumPyMinimumEigensolver
        for comparison with VQE'''
        eigensolver = NumPyMinimumEigensolver()
        result = eigensolver.compute_minimum_eigenvalue(operator)

        return result
