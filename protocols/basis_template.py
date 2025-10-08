import numpy as np

class TemplateProtocol:
    
    def __init__(self):
        pass


    #TODO: what to do with variables_index?
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


    def decode(self, data):
        sample = data[0]
        variables_index = data[1]
        loudnesses = self.binary_probabilities_to_loudness(sample, variables_index)
        loudnesses_list_of_dicts = self.loudnesses_to_list_of_dicts(loudnesses)
        #print(sample, loudnesses, loudnesses_list_of_dicts)
        return loudnesses_list_of_dicts









