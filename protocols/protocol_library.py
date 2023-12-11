from abstract_classes import VQHProtocol
from protocols.harp import HarpProtocol

class ProtocolLibrary():
    def __init__(self):
        self._protocols = {
            "harp": HarpProtocol, 
        }
    def get_protocol(self, protocol_name: str='harp') -> VQHProtocol:
        """Returns: hardware interface class associated with name.
        """
        protocol = self._protocols.get(protocol_name)
        if not protocol:
            raise ValueError(f'"{prptocol_name}" is not a valid name. Valid names are: {list(self._protocols.keys())}')
        return protocol(protocol_name)


