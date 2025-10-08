import os
import numpy as np
import copy
import config
import json
import csv

from qiskit.circuit.library import EfficientSU2
from qiskit.algorithms.optimizers import COBYLA, NFT, SPSA

from core.vqh_interfaces import QuantumHardwareInterface

class AlgorithmTemplate:
    def __init__(self, protocol, real_time=0, problem_event=None, **kwargs):

        self.num_parameters = 0
        self.variables_index = []#Temporary Backward compatibility
        self.protocol = None #Temporary Backward compatibility

    def return_optimizer(self, optimizer_name, maxiter):
        '''Convenience function to return optimizer object'''

        if optimizer_name == 'SPSA':
            optimizer = SPSA(maxiter=maxiter)
        elif optimizer_name == 'COBYLA':
            optimizer = COBYLA(maxiter=maxiter)
        elif optimizer_name == 'NFT':
            optimizer = NFT(maxiter=maxiter)

        return optimizer

    def evaluate(self, sample): #TODO: check what this function does
        pass
    def compute_extra_observables(self, sample, obs_list): #TODO: check if this function is necessary
        pass
    def get_arguments(self, instance): #TODO: check consistency with old protocol.encode function
        pass
    def iteration_callback(self, sample, exp_value, handler):

        #TODO: This is where we could implement additional observables
        additional_observ = self.compute_extra_observables(sample, problem.obs_list)
        structured_sample = self.protocol.decode(sample)
        # Broadcasts the data to the Mapper
        handler((structured_sample, exp_value))

    def init_point(self):
        if self.num_parameters == 0:
            print("No parameters found")
            raise ValueError

        return np.zeros(self.num_parameters)


    def cost_function(ansatz, params, operator, callback=None):
        #TODO: This is a template
        print(f'Hardware Interface: {config.PLATFORM}')
        hardware_interface = config.PLATFORM

        ansatz_temp = copy.deepcopy(ansatz)
        ansatz_temp.measure_all()
        #TODO: This is a template. Implement necessary arguments
        #Check the file `vqh_interfaces.py` and `hardware/local_template.py` for more information
        result = hardware_interface.run_sampler() # result = hardware_interface.run_estimator()
        expectation_value = 0 #TODO: implement this
        binary_probabilities = None #TODO: implement this
        # for sonification
        if callback:
            # Broadcast decoded sample
            callback[0](binary_probabilities, expectation_value, callback[1])
        return expectation_value



    def prepare(self, problem, count=0):#could be named get_arguments

        with open("vqe_conf.json") as cfile:
            kwargs = json.load(cfile)

        operator = self.get_arguments(problem.instance) #qubo_to_operator, qubo_to_array, etc.. previously part of protocol.encode

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

        optimizer = algorithm_params['optimizer']
        ansatz = algorithm_params['ansatz']
        operator = algorithm_params['operator']

        #TODO: This is a template. The cost function should be implemented
        result = optimizer.minimize(lambda x: self.cost_function(ansatz=ansatz, params=x, operator=operator, callback=(self.iteration_callback, iteration_handler)), x0=initial_point)


        return result.x

