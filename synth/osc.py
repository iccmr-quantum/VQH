from core.vqh_interfaces import MappingInterface
import numpy as np
import time
from pythonosc.udp_client import SimpleUDPClient
import json
from synth.sc import MusicalScale

class OSCMapping(MappingInterface):
    def __init__(self, ip:str="127.0.0.1", port:int=1450) -> None:
        self.client = SimpleUDPClient(ip, port)
        self.scale = MusicalScale()

    def publish_data(self, data, **kwargs):
        print(f'Publishing data: {data}')
        serialized_data = json.dumps(data)
        self.client.send_message("/vqh/expval", data[1])
        self.client.send_message("/vqh/mprob", serialized_data)

    def update_client(self, ip:str, port:int):
        self.client = SimpleUDPClient(ip, port)

    def freeall(self):
        pass
    def free(self):
        pass
