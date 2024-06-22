import os
import numpy as np
import copy
import config
import json

from vqe.vqe_experiments import SamplingVQE
from qiskit.circuit.library import EfficientSU2
from qiskit.algorithms.optimizers import COBYLA, NFT, SPSA, TNC, SLSQP, ADAM

from threading import Lock

class VQEAlgorithm:
    def __init__(self, protocol, real_time=0, problem_event=None):

        self.protocol = protocol
        self.variables_index = None
        self.num_parameters = 0


    def return_optimizer(self, optimizer_name, maxiter):
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
        elif optimizer_name == 'ADAM':
            optimizer = ADAM(maxiter=maxiter)

        return optimizer

    def iteration_callback(self, sample, exp_value, handler):
    

        amps = self.protocol.decode(([sample], self.variables_index))
        #print(amps)
        #for handler in handlers:
        #    handler((amps, exp_value))
        handler((amps, exp_value))

    def init_point(self):
        if self.num_parameters == 0:
            print('No parameters found')
            raise ValueError


        return np.zeros(self.num_parameters)
            

    def prepare(self, problem, count=0):

        with open("vqe_conf.json") as cfile:
            kwargs = json.load(cfile)

        operator, self.variables_index = self.protocol.encode(problem)

        # TODO: Include the iteration counter somehow
        optimizer = self.return_optimizer(
                kwargs['optimizer_name'], kwargs['iterations'][0])
        ansatz = EfficientSU2(num_qubits=len(self.variables_index), reps=kwargs['reps'], entanglement=kwargs['entanglement'])

        self.num_parameters = ansatz.num_parameters

        algorithm_params = {
            'ansatz': ansatz,
            'operator': operator,
            'optimizer': optimizer
        }

        return algorithm_params

    def run_algorithm(self, initial_point, iteration_handler, **algorithm_params):

        ansatz_temp = copy.deepcopy(algorithm_params['ansatz'])
        vqe_experiment = SamplingVQE()
        result, binary_probabilities, expectation_values = vqe_experiment.run_vqe(
                ansatz_temp, algorithm_params['operator'], algorithm_params['optimizer'], initial_point, callback=(self.iteration_callback, iteration_handler))

        return result.x




