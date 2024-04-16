import os
import numpy as np
import copy
import config
import json

from vqe.vqe_experiments import SamplingVQE
from qiskit.circuit.library import EfficientSU2
from qiskit.algorithms.optimizers import COBYLA, NFT, SPSA, TNC, SLSQP, ADAM

from threading import Lock

class VQEProcess:
    def __init__(self, problem, protocol, real_time=0, problem_event=None):

        self.problem = problem
        self.protocol = protocol
        self.variables_index = None
        self.handler = None
        self.rt_mode = real_time
        self.problem_event = problem_event
        self.lock = Lock()

        self._active = True

    @property
    def active(self):
        with self.lock:
            return self._active

    @active.setter
    def active(self, value):
        with self.lock:
            self._active = value



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

    def vqe_callback(self, sample, exp_value, handler):
    

        amps = self.protocol.decode(([sample], self.variables_index))
        #print(amps)
        handler((amps, exp_value))


    def run_fixed(self, iteration_handler):

        '''Run harmonizer algorithm for list of qubos and list of iterations. VQE is performed for the i-th qubo for i-th number of iterations.'''
        #global PATH
        print('DIFERRED TIME')

        # Load latest config file
        with open("vqe_conf.json") as cfile:
            kwargs = json.load(cfile)

        self.handler = iteration_handler
        # loop over qubos
        #os.makedirs(config.PATH, exist_ok=True)
        for count, qubo in enumerate(self.problem.qubos):
            print(f'Working on hamiltonian #{count}')
            
            # Qubo to Hamiltonian
            operator, self.variables_index = self.protocol.encode(self.problem)
            
            #Optimizer
            optimizer = self.return_optimizer(
                kwargs['optimizer_name'], kwargs['iterations'][count])
            ansatz = EfficientSU2(num_qubits=len(self.variables_index), reps=kwargs['reps'], entanglement=kwargs['entanglement'])
            
            # Initial point
            if count == 0:
                initial_point = np.zeros(ansatz.num_parameters)
            ansatz_temp = copy.deepcopy(ansatz)
            vqe_experiment = SamplingVQE()
            vqe_experiment.update_config()
            result, binary_probabilities, expectation_values = vqe_experiment.run_vqe(
                    ansatz_temp, operator, optimizer, initial_point, callback=(self.vqe_callback, iteration_handler))


            # Set initital point for next qubo to be the optimal point of the previous qubo
            initial_point = result.x

    def run_segmented(self, iteration_handler):

        '''Run harmonizer algorithm for list of qubos and list of iterations. VQE is performed for the i-th qubo for i-th number of iterations.'''
        #global PATH

        print('SEGMENTED')

        self.handler = iteration_handler
        # loop over qubos
        count = 0
        while self.active:
            
            print(f'Next Segment: #{count}')

            # Load latest config file
            with open("vqe_conf.json") as cfile:
                kwargs = json.load(cfile)
            
            operator, self.variables_index = self.protocol.encode(self.problem)
            
            #Optimizer
            optimizer = self.return_optimizer(
                kwargs['optimizer_name'], kwargs['iterations'][count])
            ansatz = EfficientSU2(num_qubits=len(self.variables_index), reps=kwargs['reps'], entanglement=kwargs['entanglement'])
            
            # Initial point
            if count == 0:
                initial_point = np.zeros(ansatz.num_parameters)
            ansatz_temp = copy.deepcopy(ansatz)
            vqe_experiment = SamplingVQE()
            vqe_experiment.update_config()
            result, binary_probabilities, expectation_values = vqe_experiment.run_vqe(
                    ansatz_temp, operator, optimizer, initial_point, callback=(self.vqe_callback, iteration_handler))


            # Set initital point for next qubo to be the optimal point of the previous qubo
            initial_point = result.x
            print('Waiting for New Problem...')
            self.problem_event.wait()
            self.problem_event.clear()
            
            count += 1


    def run_realtime(self, iteration_handler):

        '''Run harmonizer algorithm for list of qubos and list of iterations. VQE is performed for the i-th qubo for i-th number of iterations.'''
        #global PATH

        print('REALTIME')
        # Load latest config file
        with open("vqe_conf.json") as cfile:
            kwargs = json.load(cfile)

        self.handler = iteration_handler
        # loop over qubos
        #os.makedirs(config.PATH, exist_ok=True)
        for count, qubo in enumerate(self.problem.qubos):
            print(f'Working on hamiltonian #{count}')
            
            # Qubo to Hamiltonian
            operator, self.variables_index = self.protocol.encode(self.problem)
            
            #Optimizer
            optimizer = self.return_optimizer(
                kwargs['optimizer_name'], kwargs['iterations'][count])
            ansatz = EfficientSU2(num_qubits=len(self.variables_index), reps=kwargs['reps'], entanglement=kwargs['entanglement'])
            
            # Initial point
            if count == 0:
                initial_point = np.zeros(ansatz.num_parameters)
            ansatz_temp = copy.deepcopy(ansatz)
            vqe_experiment = SamplingVQE()
            vqe_experiment.update_config()
            result, binary_probabilities, expectation_values = vqe_experiment.run_vqe(
                    ansatz_temp, operator, optimizer, initial_point, callback=(self.vqe_callback, iteration_handler))


            # Set initital point for next qubo to be the optimal point of the previous qubo
            initial_point = result.x

    def run(self, iteration_handler):
        if self.rt_mode == 2:
            self.run_realtime(iteration_handler)
        elif self.rt_mode == 1:
            self.run_segmented(iteration_handler)
        elif self.rt_mode == 0:
            self.run_fixed(iteration_handler)


