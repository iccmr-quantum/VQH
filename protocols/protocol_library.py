from abstract_classes import VQHProtocol
from protocols.harp import HarpProtocol
from protocols.amplitude import AmplitudeProtocol

class ProtocolLibrary():
    def __init__(self):
        self._protocols = {
            "harp": HarpProtocol, 
            "amplitude": AmplkitudeProtocol,
        }
    def get_protocol(self, protocol_name: str='harp') -> VQHProtocol:
        """Returns:protocol class associated with name.
        """
        protocol = self._protocols.get(protocol_name)
        if not protocol:
            raise ValueError(f'"{protocol_name}" is not a valid name. Valid names are: {list(self._protocols.keys())}')
        return protocol(protocol_name)


