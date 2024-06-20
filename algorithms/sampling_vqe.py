from qiskit_aer.primitives import Sampler
from qiskit_algorithms.optimizers import COBYLA, NFT, SPSA
import copy
import numpy as np


class SamplingVQE:
    def __init__(
        self, ansatz, initial_point, optimizer_name, problem, alpha=0.1, seed=42, shots=1000, maxiter=1000
    ):
        self.alpha = alpha
        self.ansatz = ansatz
        self.binary_probabilities = None
        self.cost = None
        self.energy = None
        self.initial_point = initial_point
        self.optimizer_name = optimizer_name
        self.problem = problem
        # if we want to use other backends, we should pass the sampler as an argument.
        self.sampler = Sampler(
            backend_options={
                "method": "matrix_product_state",
            },
            run_options={"shots": shots, "seed": seed},
        )
        self.result = None

    def binary_string_to_ndarray(binary_string):
        """convert binary string to numpy array"""
        return np.array([int(bit) for bit in binary_string])
    
    def get_optimizer(self):
        if self.optimizer_name == "COBYLA":
            return COBYLA(maxiter=self.maxiter)
        elif self.optimizer_name == "NFT":
            return NFT(maxiter=self.maxiter)
        elif self.optimizer_name == "SPSA":
            return SPSA(maxiter=self.maxiter)
        else:
            raise ValueError(f"Optimizer {self.optimizer_name} not supported")

    def cost_function(self, params):
        """evaluate the CVaR cost function for given ansatz, parameters and problem"""
        # convention: functions should never change the ansatz.
        ansatz = copy.deepcopy(self.ansatz)
        self.result = self.sampler.run(
            circuits=ansatz, parameter_values=params
        ).result()
        self.binary_probabilities = self.result.quasi_dists[0].binary_probabilities(
            num_bits=ansatz.num_qubits
        )
        binary_energies_sorted = dict(
            sorted(
                {
                    binary_string: self.problem.evaluate(
                        self.binary_string_to_ndarray(binary_string)
                    )
                    for binary_string in self.binary_probabilities
                }
            )
        )
        # compute cost and energy
        self.cost = 0.0
        self.energy = 0.0
        accumulated_percent = 0.0
        for binary_string, energy in binary_energies_sorted.items():
            prob = self.binary_probabilities[binary_string]
            self.energy += energy * prob
            if accumulated_percent < self.alpha:
                self.cost += energy * min(prob, self.alpha - accumulated_percent)
                accumulated_percent += prob
        self.cost = np.real(self.cost / self.alpha)
        return self.cost

    def iteration_callback(self):
        return self.binary_probabilities, self.energy

    def run(self):
        """run the algorithm"""
        self.optimizer = self.get_optimizer()
        self.result = self.optimizer.minimize(
            self.cost_function, x0=self.initial_point
        )
        return self.result
