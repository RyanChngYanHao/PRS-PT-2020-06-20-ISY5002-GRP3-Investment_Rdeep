# Fast Fourier Transformation to get wL a suggestion
import importlib as imp
import matplotlib.pyplot as plt
import numpy as np
import cDB; imp.reload(cDB)
import DataPrep; imp.reload(DataPrep)

from DataSource import dR, wL, wF, tL, mS
from DataPrep import df
from scipy.fftpack import fft
from scipy.signal import find_peaks as findPeaks

# setup
samplingFrequency   = 256                                                      # works well with power 2
wave                = df['Close'].iloc[-samplingFrequency:]
waveM               = wave - wave.mean()

fourierTransform    = np.fft.fft(waveM)/len(waveM)                             # Normalize amplitude
fourierTransform    = fourierTransform[range(int(len(waveM)/2))]               # Exclude sampling frequency 

tpCount             = len(waveM)
values              = np.arange(int(tpCount/2))
timePeriod          = tpCount/samplingFrequency
frequencies         = values/timePeriod

def wLsuggest():
    # catch the first suitable frequency in range, else return default
    (peaks ,_) = findPeaks(abs(fourierTransform))
    for i in peaks:
        period = samplingFrequency/frequencies[i]
        if  period > 63 or period < 15:
            firstFreqInRng = 1
            print(samplingFrequency/frequencies[i])
        else:
            firstFreqInRng = frequencies[i]
            break
    wLguess = int(round(samplingFrequency/firstFreqInRng,0))
    
    wLcurrent = wL
    if wLguess > 63:
        wLsug = wLcurrent
    else:
        wLsug = wLguess
    return wLsug
wLsug = wLsuggest()

'''
def getVis():
    # Frequency domain representation
    fig, ax = plt.subplots(2, 1)
    plt.subplots_adjust(hspace=1) 
    wave.plot(ax=ax[0])
    ax[0].axhline(y=wave.mean(), color='g', linestyle='--', lw=0.5)
    ax[0].set_title('Last ' + str(samplingFrequency) + ' days')
    ax[1].set_ylabel('Price') 
    ax[1].set_title('Fourier transform depicting the frequency components')
    ax[1].plot(frequencies, abs(fourierTransform))
    ax[1].set_xlabel('Frequency')
    ax[1].set_ylabel('Amplitude')
    return fig
vis = getVis()
'''

# developer check
print('@FFT: ', [wLsug])
