import numpy as np 

class AmplitudeProtocol:

    def __init__(self):
        pass

    def decode(self, binary_probabilities):
        """Converts binary probabilities to a numpy array."""
        array = np.zeros(len(list(binary_probabilities.keys())[0]))
        for binary_string, probability in binary_probabilities.items():
            for bit in binary_string:
                array[int(bit)] += probability
        # normalize
        array /= np.sum(array)
        return array
