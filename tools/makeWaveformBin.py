import numpy as np
from numpy import savetxt
from scipy import signal as sg
from scipy.signal import chirp, sweep_poly

import matplotlib.pyplot as plt

from taborTools.instFunction import *
from taborTools.waveFunction import *

#### Waveform Parameters ####
sclk = 2.5e9
bits = 16
amplitude = 1
cycles = 4
segmentLen = 2048
#frequencyHz = 10e6 # not used in Chirp
#cycles = int(frequencyHz * segmentLen / sclk)
#### Chirp Specific
#chirpRamp = 10e-4
#chirpStart = 2900e6
#chirpBW = 200E6
#### Squarewave Specific
#duty = 0.5
#### Triangle Specific
#width = 0.5
#### Guassian Specific
#sigma = 10
#### Set Path ####
seg_file_path = '..\Segments\segments16bitBin\FourCyclesSineWave_16Bit.bin'

waveform = sineWave(segmentLen, bits, cycles, amplitude)
#waveform = chirpWave(sclk, chirpRamp, bits, chirpStart, chirpBW, amplitude)
#waveform = guassianPulse(segmentLen, bits, cycles, sigma, amplitude)
#waveform = squareWave(segmentLen, bits,, cycles, duty, amplitude)
#waveform = triangleWave(segmentLen, bits, cycles, width, amplitude)

waveLen = len(waveform)

waveArry = []
for i in range(0,waveLen):
    waveArry.append(waveform[i])

f = open("temp.seg", 'wb')
binary_format = bytearray(waveArry)
f.write(binary_format)
f.close()

f=open("temp.seg","rb")
num=list(f.read())
#print (num)
print (len(num))
f.close()




    
    
 
