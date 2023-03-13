import librosa as lr
import numpy as np
import soundfile as sf
def generate_mel_filters():

    melfb = lr.filters.mel(sr=48000, n_fft=2048, n_mels=12, norm=np.inf)

    for i, fil in enumerate(melfb):
        print(i, fil)
        sf.write(f"/home/itaborala/melfb{i}.wav", fil[:-1], 48000)


if __name__ == "__main__":
    generate_mel_filters()
