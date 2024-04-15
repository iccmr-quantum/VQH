import csv

class QUBOProblem:
    def __init__(self, filename):
        self.qubos = []

        self.load_data(filename)


    def load_data(self, filename="h_setup_rt.csv"):

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

        with open(filename, 'r') as hcsv:
            hsetup = list(csv.reader(hcsv, delimiter=','))

        #header = hsetup.pop(0)
        #logger.debug(f'CSV Header: {header}')
        #n_of_ham = int(header[1])
        n_of_ham = 1
        n_of_notes = 4
        self.qubos = []
        #n_of_notes = int(header[2])
        for h in range(n_of_ham):
            notes = hsetup.pop(h*n_of_notes)[1:]
            self.qubos.append({(row[0], notes[i]): float(n) for row in hsetup[h*n_of_notes:h*n_of_notes+n_of_notes] for i, n in enumerate(row[1:])})

        return self.qubos[-1]

