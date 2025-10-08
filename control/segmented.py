from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import json
import numpy as np


class RTController():
    def __init__(self, conf_file='rt_conf.json', ip='127.0.0.1', port=1452, parent_core=None):
        self.ip = ip
        self.port = port
        self.conf_file = conf_file
        self.conf = {}
        self.server = None
        self.server_thread = None

        if parent_core is None:
            raise ValueError("parent_core must be provided")
        self.parent_core = parent_core
        
    def start(self):
        dispatcher = Dispatcher()

        dispatcher.map("/vqh/rt/next", self.handle_next)


        self.server = BlockingOSCUDPServer((self.ip, self.port), dispatcher)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        print(f"RT Controller started on {self.ip}:{self.port}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            if self.server_thread:
                self.server_thread.join()
            print("RT Controller stopped")

    def handle_next(self, address, *args):
        
        self.parent_core.problem_event.set()

        #try:
        #    with open("rt_conf.json", 'r') as f:
        #        conf = json.load(f)

        #    conf["next_problem"] = True
        #    with open("rt_conf.json", 'w') as f:
        #        json.dump(conf, f)
        #except Exception as e:
        #    print(f"Error updating configuration: {e}")







