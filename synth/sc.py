from core.vqh_interfaces import MappingInterface
import asyncio
import numpy as np
from supercollider import Synth, Server, Group, AudioBus
import time
# from threading import Lock

global NOTESDICT
NOTESDICT = {"c":"amp1", "c#":"amp2", "d":"amp3", "d#":"amp4", "e":"amp5", "f":"amp6", "f#":"amp7", "g":"amp8", "g#":"amp9", "a":"amp10", "a#":"amp11", "b":"amp12", "new":"amp13"}
global FREQDICT
FREQDICT = {"c":60, "c#":61, "d":62, "d#":63, "e":64, "f":65, "f#":66, "g":67, "g#":68, "a":69, "a#":70, "b":71}

class MusicalScale:
    def __init__(self):
        self.scales:dict = {
            "major": lambda x: [0, 2, 4, 5, 7, 9, 11][x % 7] + 60 + 12 * (x // 7),
            "minor": lambda x: [0, 2, 3, 5, 7, 8, 10][x % 7] + 60 + 12 * (x // 7),
            "pentatonic": lambda x: [0, 2, 4, 7, 9][x % 5] + 60 + 12 * (x // 5),
            "blues": lambda x: [0, 3, 5, 6, 7, 10][x % 6] + 60 + 12 * (x // 6),
            "chromatic": lambda x: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11][x % 12] + 60 + 12 * (x // 12),
            "maj7chord": lambda x: [0, 4, 7, 11][x % 4] + 60 + 12 * (x // 4)
        }

        self._current_scale = self.scales["chromatic"]

    @property
    def current_scale(self):
        return self._current_scale

    @current_scale.setter
    def current_scale(self, scale_name):
        self._current_scale = self.scales[scale_name]

    #def select_scale(self, scale):
    #    self.current_scale = self.scales[scale]

    def get_note(self, x):
        if self.current_scale:
            return self.current_scale(x)
        else:
            print("Warning: No scale selected")
            return x


class SuperColliderMapping(MappingInterface):
    def __init__(self):
        self.server = Server()
        notesd = {"c":"amp1", "c#":"amp2", "d":"amp3", "d#":"amp4", "e":"amp5", "f":"amp6", "f#":"amp7", "g":"amp8", "g#":"amp9", "a":"amp10", "a#":"amp11", "b":"amp12", "new":"amp13"}
        self.rt_synth = None
        self.scale = MusicalScale()
        self.notes = []
        self._gain = 0.1
        # self.lock = Lock()

    @property
    def gain(self):
        # with self.lock:
        return self._gain

    @gain.setter
    def gain(self, value):
        # with self.lock:
        self._gain = value

    # TODO: Refactor this deprecated function for v0.3
    def note_loudness_multiple_rs(self, data, **kwargs):
        raise ValueError("Old Subractive synthesis function is now deprecated.")
        global NOTESDICT
        loudnessstream = data[0]
        expect_values = data[1]

        labels = ["amp1", "amp2", "amp3", "amp4", "amp5", "amp6", "amp7", "amp8", "amp9", "amp10", "amp11", "amp12"]
        loudness = np.zeros(12)
        args = dict(zip(labels,loudness))
        synth = Synth(self.server, "vqe_son3", args)

        for v, state in enumerate(loudnessstream):
            print(state)
            for k, amp in state.items():
                synth.set(NOTESDICT[k], amp)
            synth.set("shift", expect_values[v])
            time.sleep(0.04)


    def note_loudness_rt(self, data, **kwargs):
        loudnesses = data[0]


        nnotes = len(loudnesses[0])

        if not self.rt_synth:

            silence = np.zeros(nnotes)
            self.notes =[]
            self.rt_synth = []
            for i in range(nnotes): 
                note = self.scale.get_note(i)
                self.rt_synth.append(Synth(self.server, "vqh_rt_add_sin", {"amp":0.0, "idx":note}))
                self.notes.append(note)

        state = loudnesses[0]
        print(state)
        print(f'Synth: {self.rt_synth}')
        print(f"Mapper: (", end="")
        for i, (k, amp) in enumerate(state.items()):
            self.rt_synth[i].set("amp", amp)
            note = self.scale.get_note(i)
            print(i, note)
            print(self.notes[i])
            if note != self.notes[i]:
                self.rt_synth[i].set("idx", note)
                self.notes[i] = note
            print(f"{k}:{amp:.1f},", end="")
        print(")", end="\r")


    # TODO: Remove dependency on global variables
    def note_cluster_intensity_rt(self, data, **kwargs):
        global FREQDICT
        loudnessstream = data[0]
        expect_values = data[1]

        state = loudnessstream[0]
        print(f"STATE: {state}")
        sorted_state = dict(sorted(state.items(), key=lambda item: item[1]))
        print(sorted_state)
        print(f" expected value: {expect_values}")
        print(f" shifted value: {(expect_values - (-32))/100}")
        shifted_value = (expect_values - (-32))/400
        for i, (k, amp) in enumerate(sorted_state.items()):
            sy = Synth(self.server, "vqe_son2_rt", {"note": FREQDICT[k], "amp":amp})
            # sy = Synth(server, "vqe_son2", {"note": FREQDICT[k]+expect_values[v]-3, "amp":amp})
            time.sleep(0.004+shifted_value)
        #time.sleep(0.2)

# Ctrl - . equivalent to kill sounds in SC
    def freeall(self):
        self.server = Server()
        self.server._send_msg("/g_freeAll", 0)

    def free(self):

        if type(self.rt_synth) == list:
            for synth in self.rt_synth:
                synth.free()
        else:
            self.rt_synth.free()

        self.rt_synth = None

