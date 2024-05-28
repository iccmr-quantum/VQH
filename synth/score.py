from abstract_classes import SonificationInterface
import numpy as np
import time
import random
import os
from music21 import note, stream
import subprocess
from PIL import Image
import threading


class ScoreBuilderMapping(SonificationInterface):
    def __init__(self):

        self.score = stream.Stream()
        self.update_png()
        self.scale = None
        self.fehp = None
        self.feh_thread = threading.Thread(target=self.run_feh, daemon=True)
        self.feh_thread.start()

        print('ScoreBuilderMapping initialized')
    def update_stream(self, data, **kwargs):
        print(data)
        notes = [random.randint(60, 72) for _ in range(10)]
        for i, d in enumerate(data[0][0].items()):
            print(f'expval: {d}')
            n = note.Note(notes[i])
            n.duration.type = 'half'
            self.score.append(n)


            print(self.score)
        self.update_png()


    def update_png(self):
        self.score.write('musicxml.png', 'vqhscore.png')
        with Image.open('vqhscore-1.png') as im:
            background = Image.new("RGB", im.size, (255, 255, 255))
            background.paste(im, mask=im.split()[3])
            background.save('vqhscore.png')


    def run_feh(self):
        subprocess.Popen(['feh', '-R', '0.05', '-q', '--zoom', '80%', '--image-bg', 'white', 'vqhscore.png', '&'], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)




    def freeall():
        self.fehp.terminate()
    def free():
        self.fehp.terminate()
