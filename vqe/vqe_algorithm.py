from qiskit_aer import AerSimulator
import numpy as np
import copy
import config
import json
from qiskit.primitives import Estimator, Sampler
from vqe.vqe_experiments import SamplingVQE
from qiskit.circuit.library import EfficientSU2
from qiskit_algorithms.optimizers import COBYLA, NFT, SPSA, TNC, SLSQP, ADAM
from qiskit import transpile

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

    def iteration_callback(self, sample, exp_value, mls, handler):
    

        amps = self.protocol.decode(([sample], self.variables_index))
        #print(sample)
        #print(amps)
        #for handler in handlers:
        #    handler((amps, exp_value))
        if mls is None:
            handler((amps, exp_value))
        else:
            handler((amps, exp_value, mls))

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
        
        son_mode = kwargs['son_mode']

        algorithm_params = {
            'ansatz': ansatz,
            'operator': operator,
            'optimizer': optimizer,
            'son_mode': son_mode
        }

        return algorithm_params

    def run_algorithm(self, initial_point, iteration_handler, **algorithm_params):

        ansatz_temp = copy.deepcopy(algorithm_params['ansatz'])
        vqe_experiment = SamplingVQE(algorithm_params['son_mode'])
        result, binary_probabilities, expectation_values = vqe_experiment.run_vqe(
                ansatz_temp, algorithm_params['operator'], algorithm_params['optimizer'], initial_point, callback=(self.iteration_callback, iteration_handler))

        return result.x



    def run_sampling_only(self, current_point, shots=1024, **algorithm_params):
        """Run sampling experiment using given parameters without optimization"""
        
        print(f"Running sampling experiment with {shots} shots...")
        
        ansatz = algorithm_params['ansatz']
        operator = algorithm_params['operator']
        
        # Setup sampler and estimator
        estimator = Estimator(options = {'backend': config.PLATFORM.backend, 'shots': shots})


        # Run estimation
        ansatz_temp = copy.deepcopy(ansatz)
        result_estimator = estimator.run(ansatz_temp, operator, parameter_values=current_point).result()
        expectation_value = np.real(result_estimator.values[0])
        
        # Run sampling
        ansatz_temp = copy.deepcopy(ansatz)
        ansatz_temp.assign_parameters(current_point, inplace=True)
        ansatz_temp.measure_all()

        simulator = AerSimulator()
        ansatz_temp = transpile(ansatz_temp, simulator)

        result = simulator.run(ansatz_temp, shots=shots, memory=True).result()


        sample_binary_probabilities = {bitstring: count/shots for bitstring, count in result.get_counts().items()}
        
        print(f"Sample result Counts: {result.get_counts()}")
        memory = result.get_memory()
        # Create results dictionary
        sampling_results = {
            'expectation_value': expectation_value,
            'binary_probabilities': sample_binary_probabilities,
            'current_point': current_point.tolist(),
            'shot_memory': memory,
            'shots': shots,
            'num_qubits': ansatz.num_qubits
        }
        
        # Save to file
        sampling_filename = 'sampling_experiment.json'
        with open(sampling_filename, 'w') as f:
            json.dump(sampling_results, f, indent=4)
        
        print(f"Sampling results saved to {sampling_filename}")
        print(f"Expectation value: {expectation_value}")
        
        return sampling_results
