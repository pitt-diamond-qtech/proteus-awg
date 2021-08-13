import numpy as np
from scipy import signal as sg

def squareWave(segmentLength, bits, cycles, duty, amp):
    
    time = np.linspace(0, segmentLength-1, segmentLength)
    omega = 2 * np.pi * cycles
    rawSignal = amp*sg.square(omega*time/segmentLength, duty)
    
    dacSignal = scaleWaveform(rawSignal, bits)
    
    return(dacSignal);
    
def sineWave(segmentLength, bits, cycles, amp):
    
    time = np.linspace(0, segmentLength-1, segmentLength)
    omega = 2 * np.pi * cycles
    rawSignal = amp*np.sin(omega*time/segmentLength)

    dacSignal = scaleWaveform(rawSignal, bits)
    
    return time,rawSignal

def triangleWave(segmentLength, bits, cycles, width, amp):
    
    time = np.linspace(0, segmentLength-1, segmentLength)
    omega = 2 * np.pi * cycles
    rawSignal = amp*sg.sawtooth(omega*time/segmentLength, width)

    dacSignal = scaleWaveform(rawSignal, bits)
    
    return(dacSignal);      
    
def guassianPulse(segmentLength, bits, cycles, sigma, amp):
    
    time = np.linspace(-(segmentLength)/2, (segmentLength)/2, segmentLength)
    omega = 2 * np.pi * cycles
    variance=np.power(sigma, 2.) # is the pulse half-duration
    rawPulse = amp*(np.exp(-np.power((omega*time/segmentLength), 2.) / (2 * variance)))

    dacSignal = scaleWaveform(rawPulse, bits)
    
    return(dacSignal);
    
    
def scaleWaveform(rawSignal, bits):
    
    maxSig = max(rawSignal)
    verticalScale = ((pow(2, bits))/2)-1
    vertScaled = (rawSignal/maxSig) * verticalScale
    dacSignal = (vertScaled + verticalScale)
    dacSignal = dacSignal.astype(int)
    
    if max(dacSignal) > 256:
        dacSignal16 = []
        for i in range(0,len(dacSignal)*2):
            dacSignal16.append(0)
            
        j=0
        for i in range(0,len(dacSignal)):
            dacSignal16[j] = dacSignal[i] & 0x0f
            dacSignal16[j+1] = dacSignal[i] >> 8
            j=j+2
        dacSignal = dacSignal16
    
    return dacSignal