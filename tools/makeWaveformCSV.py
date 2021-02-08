import numpy as np
from numpy import savetxt
from scipy import signal as sg
from scipy.signal import chirp, sweep_poly

import matplotlib.pyplot as plt

from taborTools.instFunction import *
from taborTools.waveFunction import *

#### Waveform Parameters ####
sclk = 9e9
bits = 8
amplitude = 1
cycles = 10
segmentLen = 4096
frequencyHz = 10e6 # not used in Chirp
cycles = int(frequencyHz * segmentLen / sclk)
# Chirp Specific
chirpRamp = 10e-4
chirpStart = 2900e6
chirpBW = 200E6
# Squarewave Specific
duty = 0.5
# Triangle Specific
width = 0.5
# Guassian Specific
sigma = 10
#### Set Path ####
seg_file_path = '..\segments8bitCSV\chrip-2900MHz-3100MHz-9GS.csv'

#waveform = sineWave(segmentLen, bits, cycles, amplitude)
waveform = chirpWave(sclk, chirpRamp, bits, chirpStart, chirpBW, amplitude)
#waveform = guassianPulse(segmentLen, bits, cycles, sigma, amplitude)
#waveform = squareWave(segmentLen, bits,, cycles, duty, amplitude)
#waveform = triangleWave(segmentLen, bits, cycles, width, amplitude)

print(waveform)

savetxt(seg_file_path, waveform, fmt='%1i', delimiter='\n')

    
    
 
