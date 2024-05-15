import csv
from util.inlets import VQHInlet
from threading import Lock
import numpy as np

# todo: what is the difference between QUBOProblem and QUBOProblemRT?


class QUBOProblem:
    def __init__(self, filename):
        self.qubos = []

        self.load_data(filename)

    def qubo_to_array(self, qubo: list) -> np.ndarray:
        """Converts a qubo in list format to a numpy array."""
        dim = len(qubo[-1])
        a = np.zeros((dim, dim))
        for row in qubo:
            ind_row = len(row) - 1
            for ind_col, coeff in enumerate(row):
                try:
                    a[ind_row][ind_col] = coeff
                except ValueError:
                    print(
                        "QUBO coeffficient ({}, {}) is not a number! Setting it to 0.".format(
                            ind_row, ind_col
                        )
                    )
        return a

    def load_data(self, filename="h_setup.csv"):

        # design choice: define labels here? allow for different labels for each qubo?
        # I think it's more natural to have fixed labels. Otherwise it's like changing the meaning of notes in the middle of a song.
        # Musicians are crazy, however, so up to you.

        """Builds a list of qubos from a csv file.
        The csv file must be in the same folder as this script and must be named
        "h_setup.csv". The csv file must have the follsowing format:

        # first qubo
        c_{0,0}
        c_{1,0},c_{1,1}
        c_{n-2,0}c_{n-2,1},...,c_{n-2,n-3},c_{n-2,n-2}
        c_{n-1,0}c_{n-1,1},...,c_{n-1,n-2},c_{n-1,n-1}
        # second qubo
        c_{0,0}
        c_{1,0},c_{1,1}
        c_{n-2,0}c_{n-2,1},...,c_{n-2,n-3},c_{n-2,n-2}
        c_{n-1,0}c_{n-1,1},...,c_{n-1,n-2},c_{n-1,n-1}
        # and so on

        The function returns a list of qubos of the form:
        [np.array, np.array, ...]
        where each np.array is a qubo matrix.
        """

        with open(filename, 'r') as f:
            reader = csv.reader(f)
            qubo = [next(reader)]
            for row in reader:
                if len(row) > len(qubo[-1]):
                    qubo.append(row)
                else:
                    self.qubos.append(self.qubo_to_array(qubo))
                    qubo = [row]
            self.qubos.append(self.qubo_to_array(qubo))

        return self.qubos[-1]
    
    def evaluate(self, qubo: np.ndarray, x: np.ndarray) -> float:
        return np.dot(x, np.dot(qubo, x))


class QUBOProblemRT:
    def __init__(self, filename):

        self._qubos = []
        self.lock = Lock()
        self.init_data()
        self.size = 0

    @property
    def qubos(self):
        with self.lock:
            return self._qubos

    def qubo_to_array(self, qubo: list) -> np.ndarray:
        """Converts a qubo in list format to a numpy array."""
        dim = len(qubo[-1])
        a = np.zeros((dim, dim))
        for row in qubo:
            ind_row = len(row) - 1
            for ind_col, coeff in enumerate(row):
                try:
                    a[ind_row][ind_col] = coeff
                except ValueError:
                    print(
                        "QUBO coeffficient ({}, {}) is not a number! Setting it to 0.".format(
                            ind_row, ind_col
                        )
                    )
        return a

    def load_data(self, filename="h_setup_rt.csv"):

        # design choice: define labels here? allow for different labels for each qubo?
        # I think it's more natural to have fixed labels. Otherwise it's like changing the meaning of notes in the middle of a song.
        # Musicians are crazy, howerver, so up to you.

        """Builds a list of qubos from a csv file.
        The csv file must be in the same folder as this script and must be named
        "h_setup.csv". The csv file must have the following format:

        # first qubo
        c_{0,0}
        c_{1,0},c_{1,1}
        c_{n-2,0}c_{n-2,1},...,c_{n-2,n-3},c_{n-2,n-2}
        c_{n-1,0}c_{n-1,1},...,c_{n-1,n-2},c_{n-1,n-1}
        # second qubo
        c_{0,0}
        c_{1,0},c_{1,1}
        c_{n-2,0}c_{n-2,1},...,c_{n-2,n-3},c_{n-2,n-2}
        c_{n-1,0}c_{n-1,1},...,c_{n-1,n-2},c_{n-1,n-1}
        # and so on

        The function returns a list of qubos of the form:
        [np.array, np.array, ...]
        where each np.array is a qubo matrix.
        """

        qubos_aux = []
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            qubo = [next(reader)]
            for row in reader:
                if len(row) > len(qubo[-1]):
                    qubo.append(row)
                else:
                    qubos_aux.append(self.qubo_to_array(qubo))
                    qubo = [row]
            qubos_aux.append(self.qubo_to_array(qubo))

        with self.lock:
            self._qubos = qubos_aux

        # return self.qubos[-1]
        self.size = len(qubos_aux)

    @qubos.setter
    def qubos(self, value):
        if value is None:
            with self.lock:
                self._qubos = None
        self.load_data(value)

    def init_data(self):
        self.qubos = "h_setup_rt.csv"

    def evaluate(self, qubo: np.ndarray, x: np.ndarray) -> float:
        return np.dot(x, np.dot(qubo, x))
