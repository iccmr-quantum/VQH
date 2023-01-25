from supercollider import Synth, Server
import numpy as np
import time


global NOTESDICT
NOTESDICT = {"c":"amp1", "c#":"amp2", "d":"amp3", "d#":"amp4", "e":"amp5", "f":"amp6", "f#":"amp7", "g":"amp8", "g#":"amp9", "a":"amp10", "a#":"amp11", "b":"amp12"}

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

def note_loudness_multiple(loudnessstream):
    global server, NOTESDICT


    labels = ["amp1", "amp2", "amp3", "amp4", "amp5", "amp6", "amp7", "amp8", "amp9", "amp10", "amp11", "amp12"]
    loudness = np.zeros(12)
    args = dict(zip(labels,loudness))
    synth = Synth(server, "vqe_model1_son1", args)

    for state in loudnessstream:
        print(state)
        for k, amp in state.items():
            synth.set(NOTESDICT[k], amp)
        time.sleep(0.2)


def sonify(loudnessstream):
    
    global server

    server = Server()
    note_loudness_multiple(loudnessstream)

def freeall():
    global server

    server._send_msg("/g_freeAll", 0)
