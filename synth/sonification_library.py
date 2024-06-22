from core.vqh_interfaces import MappingInterface
from synth.sc import SuperColliderMapping
from synth.zen import ZenMapping
from synth.osc import OSCMapping
from synth.score import ScoreBuilderMapping

class SonificationLibrary():
    def __init__(self):
        self._interfaces = {
            "sc": SuperColliderMapping,
            "zen": ZenMapping,
            "osc": OSCMapping,
            "score": ScoreBuilderMapping
        }
        self._library = {
            1: {
                "description": "Send data to Zen, to be stored as a new Book",
                "interface": "zen",
                "mapping": "post_book"
            },
            2: {
                "description": "Send data to Zen, to be stored as a new Book, and send data to Processing to be displayed",
                "interface": "zen",
                "mapping": "post_book_and_update_display"
            },
            3: {
                "description": "Subtractive synthesis with Pitchshift (dentist)",
                "interface": "sc",
                "mapping": "note_loudness_multiple_rs"
            },
            4: {
                "description": "RealTime Arpeggios",
                "interface": "sc",
                "mapping": "note_cluster_intensity_rt"
            },
            5: {
                "description": "Gereral RealTime OSC Mapping",
                "interface": "osc",
                "mapping": "publish_data"
            },
            6: {
                "description": "Gerenal RealTime Additive Synthesis",
                "interface": "sc",
                "mapping": "note_loudness_rt"
            },
            7: {
                "description": "Score Measure Manipulation Test",
                "interface": "score",
                "mapping": "update_stream"
            },
            8: {
                "description": "Circular Book",
                "interface": "zen",
                "mapping": "post_page"
            },
        }
    def get_mapping(self, son_type: int) -> MappingInterface:
        """Returns: sonification interface class associated with name.
        """

        son = self._library.get(son_type)
        if not son:
            raise ValueError(f'"{son_type}" is not a valid number. Valid names are: {list(self._library.keys())}')

        son_interface = self._interfaces.get(son["interface"])
        son_mapping = son["mapping"]

        #return getattr(son_interface, son_mapping)
        return son_interface(), son_mapping


