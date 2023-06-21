from supercollider import Synth, Server, Group, AudioBus
import numpy as np
import time


global NOTESDICT
NOTESDICT = {"c":"amp1", "c#":"amp2", "d":"amp3", "d#":"amp4", "e":"amp5", "f":"amp6", "f#":"amp7", "g":"amp8", "g#":"amp9", "a":"amp10", "a#":"amp11", "b":"amp12"}
global FREQDICT
FREQDICT = {"c":60, "c#":61, "d":62, "d#":63, "e":64, "f":65, "f#":66, "g":67, "g#":68, "a":69, "a#":70, "b":71}


def note_loudness(qd): # Deprecated --------------------
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

# Mapping #1 - Simple additive synthesis
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
        time.sleep(0.03)

# Mapping #5 - Atonal additive sysnthesis chords used in "Rasgar, Saber" (2023)
def note_loudness_multiple_rs(loudnessstream, expect_values):
    global server, NOTESDICT


    labels = ["amp1", "amp2", "amp3", "amp4", "amp5", "amp6", "amp7", "amp8", "amp9", "amp10", "amp11", "amp12"]
    loudness = np.zeros(12)
    args = dict(zip(labels,loudness))
    synth = Synth(server, "vqe_son3", args)

    for v, state in enumerate(loudnessstream):
        print(state)
        for k, amp in state.items():
            synth.set(NOTESDICT[k], amp)
        synth.set("shift", expect_values[v])
        time.sleep(0.05)

# Mapping #3 - Mel-Filterbank Spectral Diffusion
def mel_filterbank_loudness_multiple(loudnessstream, inbufnum=12):
    global server, NOTESDICT


    labels = ["amp1", "amp2", "amp3", "amp4", "amp5", "amp6", "amp7", "amp8", "amp9", "amp10", "amp11", "amp12"]
    loudness = np.zeros(12)
    args = dict(zip(labels,loudness))
    args["bufnum"] = 0
    args["inbufnum"] = inbufnum
    synth = Synth(server, "mel_fb_dif1", args)

    for state in loudnessstream:
        print(state)
        #synth.set("gate", 1)
        for k, amp in state.items():
            synth.set(NOTESDICT[k], amp)
        #synth.set("gate", 0)
        time.sleep(0.1)

# Mapping #4 - Mel-Filterbank Spectral Diffusion with Pitchshift
def mel_filterbank_loudness_multiple_decoupled(loudnessstream, expect_values):
    global server, NOTESDICT


    labels = ["amp1", "amp2", "amp3", "amp4", "amp5", "amp6", "amp7", "amp8", "amp9", "amp10", "amp11", "amp12"]
    loudness = np.zeros(12)
    args = dict(zip(labels,loudness))
    args["bufnum"] = 0
    args["inbufnum"] = 12
    srcgroup = Group(server, action=1, target=1)
    fxgroup = Group(server, action=3, target=srcgroup.id)
    srcbus = AudioBus(server, 1)
    args["inbus"] = srcbus.id
    synth = Synth(server, "mel_fb_dif2", args, target=fxgroup)
    #synth2 = Synth(server, "input_signal2", {"bufnum": 12, "out": srcbus.id}, target=srcgroup)

    for v, state in enumerate(loudnessstream):
        print(state)
        print(f" shifted value: {(expect_values[v] - min(expect_values))}")
        #synth.set("gate", 1)
        shifted_value = (expect_values[v] - min(expect_values))
        for k, amp in state.items():
            synth.set(NOTESDICT[k], amp)
        sy = Synth(server, "input_signal2", {"out":srcbus.id}, target=srcgroup)
            #sy = Synth(server, "input_signal3", {"bufnum": 15, "out":srcbus.id, "tgrate":shifted_value}, target=srcgroup)
        #synth.set("gate", 0)
        #time.sleep(0.3)

# Mapping #2 - Pitchshifted Arpeggios instead of chords. Philip Glass vibes.
def note_cluster_intensity(loudnessstream, expect_values):
    global server

    for v, state in enumerate(loudnessstream):
        #print(state)
        sorted_state = dict(sorted(state.items(), key=lambda item: item[1]))
        print(sorted_state)
        print(f" expected value: {expect_values[v]}")
        print(f" shifted value: {(expect_values[v] - min(expect_values))/100}")
        shifted_value = (expect_values[v] - min(expect_values))/100
        for i, (k, amp) in enumerate(sorted_state.items()):
            #sy = Synth(server, "vqe_son2", {"note": FREQDICT[k], "amp":amp})
            sy = Synth(server, "vqe_son2", {"note": FREQDICT[k]+expect_values[v]-3, "amp":amp})
            time.sleep(0.035+shifted_value)
        #time.sleep(0.2)

# Mapping #6 - Granular Synthesis Spatialization 4 qubits
def granular_triggers(loudnessstream, expect_values):
    global server


    labels = ["s0", "s1", "s2", "s3"]
    loudness = np.zeros(4)
    args = dict(zip(labels,loudness))

    synth = Synth(server, "vqgrains", args)

    for v, state in enumerate(loudnessstream):
        print(state)
        print(f" shifted value: {(expect_values[v] - min(expect_values))}")
        shifted_value = (expect_values[v] - min(expect_values))
        #shifted_value = -(shifted_value - max(expect_values)) #Uncomment to change shift direction
        for k, amp in state.items():
            synth.set(k, amp)
            synth.set("rate", shifted_value+0.01)
        time.sleep(0.1)


# Function called by the main script
def sonify(loudnessstream, expect_values, son_type=1):
    
    global server

    server = Server()
    # Parse mapping type
    if son_type == 1:
        note_loudness_multiple(loudnessstream)
    elif son_type == 2:
        note_cluster_intensity(loudnessstream, expect_values)
    elif son_type == 3:
        mel_filterbank_loudness_multiple(loudnessstream, inbufnum=14)
    elif son_type == 4:
        mel_filterbank_loudness_multiple_decoupled(loudnessstream, expect_values)
    elif son_type == 5:
        note_loudness_multiple_rs(loudnessstream, expect_values)
    elif son_type == 6:
        granular_triggers(loudnessstream, expect_values)

# Ctrl - . equivalent to kill sounds in SC
def freeall():
    global server

    server._send_msg("/g_freeAll", 0)
