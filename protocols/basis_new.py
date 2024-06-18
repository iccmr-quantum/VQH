import numpy as np 

class BasisProtocol:

    def __init__(self):
        pass

    def decode(self, binary_probabilities):
        """Converts binary probabilities to a numpy array."""
        # sort the binary strings by their integer value
        binary_probabilities_sorted = dict(sorted(binary_probabilities.items(), key=lambda x: int(x[0], 2)))
        array = np.array(binary_probabilities_sorted.values())
        return array
