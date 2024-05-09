from abstract_classes import SonificationInterface
import numpy as np
import time
from pythonosc.udp_client import SimpleUDPClient
import json

class OSCMapping(SonificationInterface):
    def __init__(self, ip:str="127.0.0.1", port:int=1450) -> None:
        self.client = SimpleUDPClient(ip, port)

    def publish_data(self, data, **kwargs):
        print(f'Publishing data: {data}')
        serialized_data = json.dumps(data)
        self.client.send_message("/vqh/expval", data[1])
        self.client.send_message("/vqh/mprob", serialized_data)

    def update_client(self, ip:str, port:int):
        self.client = SimpleUDPClient(ip, port)
