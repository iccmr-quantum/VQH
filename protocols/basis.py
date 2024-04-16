from qiskit.quantum_info import SparsePauliOp
from qiskit.opflow.primitive_ops import PauliSumOp
from qiskit.opflow import I, X, Z, Y
import numpy as np
from threading import Lock

class BasisProtocol:
    
    def __init__(self):
        pass


    def qubo_to_operator(self, qubo, linear_pauli='Z', external_field=0):

        '''Translates qubo problems of format {(note_1, note_2): coupling, ...} to operators to be used in VQE.
        This function can yield non-diagonal Hamiltonians.
        
        The resulting Hamitonian H is equal to the QUBO Q up to a constant factor 
        and a constant shift that do not impact the optimization
        H = 4*Q + const
        Q = H/4 - const/4 = operator + offset
        
        '''
       # First, we need to create a dictionary that maps the variables to their index in the operator
       # We make sure that the qubo is symmetric and that we only have one term for each pair of variables
        qubo_index = {}
        variables_index = {}
        count_index = 0
        for key, value in qubo.items():
            if key[0] not in variables_index:
                variables_index[key[0]] = count_index
                count_index += 1
            if key[1] not in variables_index:
                variables_index[key[1]] = count_index
                count_index += 1
            if key[0] == key[1]:
                i = variables_index[key[0]]
                qubo_index[(i, i)] = value
            elif key[0] != key[1]:
                i = variables_index[key[0]]
                j = variables_index[key[1]]
                if (j, i) in qubo_index and qubo_index[(j, i)] != value:
                    raise ValueError(
                        'QUBO is not symmetric. (i, j) and (j, i) have different values')
                if (j, i) in qubo_index:
                    pass
                    #print('Ignoring term (i, j) because (j, i) is already in qubo')
                else:
                    qubo_index[(i, j)] = value
        # Now, we can create the Hamiltonian in terms of pauli strings
        num_qubits = len(variables_index)
        paulis = {}
        const = 0
        for key, value in qubo_index.items():
            if key[0] == key[1]:
                i = key[0]
                pauli = 'I'*(num_qubits-i-1) + linear_pauli + 'I'*i
                if pauli in paulis:
                    paulis[pauli] += -2*value
                else:
                    paulis[pauli] = -2*value
                const += -2*value
            elif key[0] != key[1]:
                i = key[0]
                j = key[1]
                if i > j:
                    i, j = j, i
                pauli = 'I'*(num_qubits-j-1) + 'Z' + \
                    'I'*(j-i-1) + 'Z' + 'I'*i
                paulis[pauli] = value
                pauli = 'I'*(num_qubits-i-1) + linear_pauli + 'I'*i
                if pauli in paulis:
                    paulis[pauli] += -value
                else:
                    paulis[pauli] = -value
                pauli = 'I'*(num_qubits-j-1) + linear_pauli + 'I'*j
                if pauli in paulis:
                    paulis[pauli] += -value
                else:
                    paulis[pauli] = -value
                const += -value
        pauli_list = [(k, v) for k, v in paulis.items()]
        # external magnetic field in X direction
        for i in range(num_qubits):
            paulix = 'I'*i + 'X' + 'I'*(num_qubits-i-1)
            pauli_list.append((paulix, external_field))
        operator = PauliSumOp(SparsePauliOp.from_list(pauli_list))
        offset = -const/4 # for future reference
        print(f'Operator: \n{operator}')
         
        # Compare H with Arianna's Ising operator
        #operator2 = H_Ising(12, 1, external_field)
        
        return operator, variables_index

            



    def binary_probabilities_to_loudness(self, binary_probabilities, variables_index):
        ''' Obtain marginal probabilities for each note, interpreted as loudnesses'''

        loudnesses = {v: np.zeros(len(binary_probabilities))
                      for v in variables_index}
        variables_index_invert = {v: k for k, v in variables_index.items()}
        for iteration, binary_probability in enumerate(binary_probabilities):
            for key, value in binary_probability.items():
                for index, bit in enumerate(key[::-1]):
                    if bit == '1':
                        note = variables_index_invert[index]
                        loudnesses[note][iteration] += value
        return loudnesses


    def loudnesses_to_list_of_dicts(self, loudnesses):
        '''Convert marginal probabilities/loudnesses (a dict of lists) to list of dicts,
        where each dict contains the loudness of each note/label for a given iteration'''
        loudness_list_of_dicts = []
        for note, loudness_list in loudnesses.items():
            for i, loudness in enumerate(loudness_list):
                if len(loudness_list_of_dicts) <= i:
                    loudness_list_of_dicts.append({})
                loudness_list_of_dicts[i][note] = loudness
        return loudness_list_of_dicts



    def encode(self, problem):

        with Lock():
            qubo = problem.qubos[0]

        operator, variables_index = self.qubo_to_operator(qubo)

        return operator, variables_index



    def decode(self, data):
        sample = data[0]
        variables_index = data[1]
        loudnesses = self.binary_probabilities_to_loudness(sample, variables_index)
        loudnesses_list_of_dicts = self.loudnesses_to_list_of_dicts(loudnesses)
        #print(sample, loudnesses, loudnesses_list_of_dicts)
        return loudnesses_list_of_dicts









