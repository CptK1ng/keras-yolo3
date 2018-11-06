#import scipy
#import scipy.signal
#import matplotlib.pyplot as plt
import subprocess
import pandas as pd
import numpy as np
import scipy.io.wavfile as wav


class SoundAnalyzer:
    videopath = None
    wavfile = "../input_ex.wav"
    highvol = []
    samplingrate = 44100

    def __init__(self, videopath):
        self.videopath = videopath

    def analyze(self):
        command = "ffmpeg -i "+str(self.videopath)+" -ab 160k -ac 2 -ar "+str(self.samplingrate)+" -y -vn "+ self.wavfile
        subprocess.call(command, shell=True)
        fs, sig = wav.read(self.wavfile) #fs=Sample Rate, sig=gelesenes Signal
        print("[i] Das Eingangssignal hat eine Rate von",fs,"samples/sec. Bei",
              sig.shape[1],"Kanälen à",sig.shape[0],"Samples ergeben sich insgesamt",
              sig.size,"Samples bzw.",sig.shape[0]/fs,"Sekunden.")
        #T=Transpose: Signal-Achsen vertauschen und dann die erste Reihe nehmen
        signal = sig.T[0]
        signal = abs(signal)
        # sig2 = np.convolve(signal,np.ones(30000,dtype=int),'valid')
        # yhat = scipy.signal.savgol_filter(signal, 51, 3) # window size 51, polynomial order 3
        print(signal.shape)
        print(signal)
        pdsig = pd.Series(signal)
        pdsig_r = pdsig.rolling(window=900000)
        pdsig_r_mean = pdsig_r.mean()
        pdsig_r_mean.plot(style='k')
        mean = np.mean(pdsig_r_mean)
        print("mean",mean)
        for key, value in enumerate(pdsig_r_mean):
            if value > 2*mean:
                self.highvol.append(key)
        """
        # Zeitsignale plotten
        plt.figure(figsize=(15,5),facecolor='w')
        plt.plot(signal, label='Original Input Signal')
        plt.plot(pdsig_r_mean , label='Original Input Signal')
        plt.title("Zeitsignale für Aufgabe 1 (überlappend)",fontsize="xx-large", y=1.12)
        plt.xlim(0, len(signal))
        #plt.ylim(-1, 1)
        plt.grid(axis='y')
        plt.xlabel('Time [samples]')
        plt.ylabel('Amplitude [dB]')
        plt.legend()
        ax2 = plt.twiny() #zusätzliche Achse mit Darstellung in Sekunden statt Samples
        ax2.xaxis.set_ticks(np.arange(0, int(len(signal)/fs)+1, 1))
        ax2.grid(axis='x')
        ax2.set_xlabel("Time [seconds]")
        plt.show()
        """

    def checkFrameHighVolume(self, frame):
        #returns True if frame volume is too high
        #time = frame * framerate
        #self.samplingrate
        return frame in self.highvol


def test_soundanalysis():
    s = SoundAnalyzer("../input_ex.mp4")
    s.analyze()
    print(s.checkFrameHighVolume(12))


test_soundanalysis()
