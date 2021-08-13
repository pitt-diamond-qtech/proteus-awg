import numpy as np
from numpy import savetxt
from scipy import signal as sg
from scipy.signal import chirp, sweep_poly

from tools.waveFunction import *
import matplotlib.pyplot as plt

# Define Waveform Parameters
sclk = 1.25e9
bits = 16
amplitude = 1
cycles = 5
segmentLen = 2048

# frequencyHz = 1e6
# cycles = int(frequencyHz * segmentLen / sclk)

# Squarewave Specific
duty = 0.5
# Triangle Specific
width = 0.5
# Guassian Specific
sigma = 10

t,y = sineWave(segmentLen, bits, cycles, amplitude)
#waveform = guassianPulse(segmentLen, bits, cycles, sigma, amplitude)
#waveform = squareWave(segmentLen, bits,, cycles, duty, amplitude)
#waveform = triangleWave(segmentLen, bits, cycles, width, amplitude)

# print(waveform)
plt.plot(t,y)
plt.show()

# should define the seg. file. path
# savetxt(seg_file_path, waveform, fmt='%1i', delimiter='\n')
