from abstract_classes import SonificationInterface
from synth.sc import SuperColliderMapping
from synth.zen import ZenMapping

class SonificationLibrary():
    def __init__(self):
        self._sl_interfaces = {
            "sc": SuperColliderMapping,
            "zen": ZenMapping
        }
    def get_sonification_interface(self, interface_name: str) -> QuantumHardwareInterface:
        """Returns: sonification interface class associated with name.
        """
        son_i = self._sl_interfaces.get(interface_name)
        if not son_i:
            raise ValueError(f'"{interface_name}" is not a valid name. Valid names are: {list(self._sl_interfaces.keys())}')
        return son_i()


