from abstract_classes import VQHOperator


class VQHOperatorQUBO(VQHOperator):
    def __init__(self):
        self.type = 'qubo'
        self.operators = []
        self.variables_indexes = []
        self.qubos = []


    def load_from_file(self, filename):

        '''Builds a list of qubos from a csv file. 
        The csv file must be in the same folder as this script and must be named 
        "h_setup.csv". The csv file must have the following format:
        
        h1,label1,label2,label3,...,labeln
        label1,c11,c12,c13,...,c1n
        label2,c21,c22,c23,...,c2n
        label3,c31,c32,c33,...,c3n
        ...
        labeln,cn1,cn2,cn3,...,cnn
        h2,label1,label2,label3,...,labeln
        label1,c11,c12,c13,...,c1n
        ...
        
        where h1, h2, ... are the QUBO matrices names and label1, label2, ... are the
        note labels used by the sonification.

        The function returns a list of qubos of the form:
        [{(note_1, note_2): coupling, ...}, ...]
        where note_1 and note_2 are the note labels with its corresponding coupling
        coefficients.
        '''

        with open("h_setup.csv", 'r') as hcsv:
            hsetup = list(csv.reader(hcsv, delimiter=','))

        #header = hsetup.pop(0)
        #logger.debug(f'CSV Header: {header}')
        #n_of_ham = int(header[1])
        #n_of_notes = int(header[2])
        for h in range(n_of_ham):
            notes = hsetup.pop(h*n_of_notes)[1:]
            self.qubos.append({(row[0], notes[i]): float(n) for row in hsetup[h*n_of_notes:h*n_of_notes+n_of_notes] for i, n in enumerate(row[1:])})
        logger.debug(f'QUBOS: {qubos}')

        #return qubos


    def qubo_to_operator(qubo, linear_pauli='Z', external_field=+0):
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
                    logging.info(
                        'Ignoring term (i, j) because (j, i) is already in qubo')
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

        
    def build_operators(self, **kwargs):

        for qubo in self.qubos:
            operator, variables_index = qubo_to_operator(qubo)

            self.operators.append(operator)
            self.variables_indexes.append(vqriables, index)
