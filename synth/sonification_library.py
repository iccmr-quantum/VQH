from abstract_classes import SonificationInterface
from synth.sc import SuperColliderMapping
from synth.zen import ZenMapping

class SonificationLibrary():
    def __init__(self):
        self._interfaces = {
            "sc": SuperColliderMapping,
            "zen": ZenMapping
        }
        self._library = {
            1: {
                "description": "Additive Synthesis with 12 chromatic notes",
                "interface": "sc",
                "mapping": "note_loudness_multiple"
            },
            2: {
                "description": "Additive Synthesis with 8 chromatic notes",
                "interface": "sc",
                "mapping": "note_loudness_multiple_8_qubits"
            },
            3: {
                "description": "Pitchshifted Arpeggios instead of chords",
                "interface": "sc",
                "mapping": "note_cluster_intensity"
            },
            4: {
                "description": "Send data to Zen, to be stored as a new Book",
                "interface": "zen",
                "mapping": "post_book"
            },
            5: {
                "description": "Send data to Zen, to be stored as a new Book, and send data to Processing to be displayed",
                "interface": "zen",
                "mapping": "post_book_and_update_display"
            },
            6: {
                "description": "Additive Synthesis with 6 chromatic notes",
                "interface": "sc",
                "mapping": "note_loudness_multiple_6_qubits"
            },
            7: {
                "description": "Additive Synthesis with 4 chromatic notes",
                "interface": "sc",
                "mapping": "note_loudness_multiple_4_qubits"
            },
            8: {
                "description": "Subtractive synthesis with Pitchshift (dentist)",
                "interface": "sc",
                "mapping": "note_loudness_multiple_rs"
            },
        }
    def get_mapping(self, son_type: int) -> SonificationInterface:
        """Returns: sonification interface class associated with name.
        """

        son = self._library.get(son_type)
        if not son:
            raise ValueError(f'"{son_type}" is not a valid number. Valid names are: {list(self._library.keys())}')

        son_interface = self._interfaces.get(son["interface"])
        son_mapping = son["mapping"]

        #return getattr(son_interface, son_mapping)
        return son_interface(), son_mapping


