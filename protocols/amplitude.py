from abstract_classes import VQHProtocol, QuantumHardwareInterface


#import other libraries and packages

# Declare any important functions

# the function below was copied from the 'new_encodings' branch

'''
def build_operators_from_csv(n_of_ham=2, n_of_notes=8):

    with open("operator_setup.csv", 'r') as hcsv:
        hsetup = list(csv.reader(hcsv, delimiter=','))

    #header = hsetup.pop(0)
    #logger.debug(f'CSV Header: {header}')
    #n_of_ham = int(header[1])
    #n_of_notes = int(header[2])
    operators_variables_index = []

    for h in range(n_of_ham):
        notes = hsetup.pop(h*n_of_notes)[1:]
        matrix_dict = {(row[0], notes[i]): float(
            n) for row in hsetup[h*n_of_notes:h*n_of_notes+n_of_notes] for i, n in enumerate(row[1:])}
        #logger.debug(f'QUBOS: {qubos}')
        variables_index = {notes[i]: i for i in range(n_of_notes)}

        print(matrix_dict)

        matrix = np.zeros((n_of_notes, n_of_notes))
        for key, value in matrix_dict.items():
            matrix[variables_index[key[0]], variables_index[key[1]]] = value

        print(matrix)
        operator = SparsePauliOp.from_operator(Operator(matrix))
        print(operator)
        operators_variables_index.append((operator, variables_index))

    return operators_variables_index

'''

def run_vqh_amplitude(sessionname):
    #This is your main function
    # ...
    # Your code here
    # ...
    # return any data you wish
    return probabilities, expectation_values

class AmplitudeProtocol(VQHProtocol):

    def __init__(self, name):
        self.name = name

    def run(self, sessionname):
        #config.PLATFORM = hwi
        self.data = run_vqh_amplitude(sessionname)
        return self.data

    def encode(self):
        pass

    def decode(self):
        pass

