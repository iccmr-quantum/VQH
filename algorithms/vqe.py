import numpy as np
import importlib
import os
import copy
import json
from qiskit.algorithms.optimizers import COBYLA, NFT, SPSA, TNC, SLSQP, ADAM


class VQE4Lattice:
    def __init__(self):

        self.anstz = None
        self.cost_history_dict = {}
        self.config = {}
        self.algorithm_args = {}


    def load_estimator(self, module_name):
        try:
            print('Importing module:', module_name)

            est_module = importlib.import_module(module_name)
            estimator = getattr(est_module, 'Estimator')
            return estimator()
        except ModuleNotFoundError:
            print(f"Module {module_name} not found")
        except AttributeError:
            print(f"Estimator class not found in module {module_name}")
        except TypeError as te:
            print(f"Estimator class not instantiated: {te}")
        except Exception as e:
            print(f"Error while loading estimator: {e}")



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

