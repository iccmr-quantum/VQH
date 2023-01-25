from supercollider import Synth, Server
import numpy as np
import time

def note_loudness(qd):
    global server

    labels = ["amp1", "amp2", "amp3", "amp4", "amp5", "amp6", "amp7", "amp8", "amp9", "amp10", "amp11", "amp12"]
    loudness = np.zeros(12)
    args = dict(zip(labels,loudness))
    synth = Synth(server, "vqe_model1_son1", args)
    loudnesses = [loudness]
    for lqd in qd:
        loudness = np.zeros(12)
        for j, f in lqd.items():
            intj = int(j, 2)
            for i in range(12):
                trig= (intj >> i) & 1
                if trig:
                    loudness[i] += f
        for i, amp in enumerate(loudness):
            synth.set(labels[i], amp)
        loudnesses.append(loudness)
        time.sleep(0.2)

def sonify(generated_quasi_dists):
    
    global server

    server = Server()
    note_loudness(generated_quasi_dists)

def freeall():
    global server

    server._send_msg("/g_freeAll", 0)
