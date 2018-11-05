import scipy
import scipy.signal
import subprocess
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

wavfile = "../input_ex.wav"
command = "ffmpeg -i ../input_ex.mp4 -ab 160k -ac 2 -ar 44100 -y -vn "+ wavfile
subprocess.call(command, shell=True)

import scipy.io.wavfile as wav
fs, sig = wav.read(wavfile) #fs=Sample Rate, sig=gelesenes Signal
print("[i] Das Eingangssignal hat eine Rate von",fs,"samples/sec. Bei",
      sig.shape[1],"Kanälen à",sig.shape[0],"Samples ergeben sich insgesamt",
      sig.size,"Samples bzw.",sig.shape[0]/fs,"Sekunden.")


#T=Transpose: Signal-Achsen vertauschen und dann die erste Reihe nehmen
signal = sig.T[0]
signal = abs(signal)
print(signal.shape)
print(signal)
pdsig = pd.Series(signal)
pdsig_r = pdsig.rolling(window=900000)
pdsig_r_mean = pdsig_r.mean()
pdsig_r_mean.plot(style='k')
#sig2 = np.convolve(signal,np.ones(30000,dtype=int),'valid')
#yhat = scipy.signal.savgol_filter(signal, 51, 3) # window size 51, polynomial order 3

##################

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