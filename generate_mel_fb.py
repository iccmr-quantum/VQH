import librosa as lr
import numpy as np
import soundfile as sf
def generate_mel_filters():

    melfb = lr.filters.mel(sr=96000, n_fft=2048, n_mels=12, norm=np.inf)

    for i, fil in enumerate(melfb):
        print(i, fil)
        sf.write(f"/home/itabora_/melfb{i}.wav", fil[:-1], 96000)


if __name__ == "__main__":
    generate_mel_filters()
