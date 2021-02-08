import os
import sys
import inspect
import sys
import clr
import ctypes
import time
import numpy as np
from tools.instFunction import *

#prints the current directory
datapath = os.path.dirname(sys.argv[0])
if (datapath):
    datapath = datapath + "\\"
print(datapath)

class Proteus:
    '''This is the class def for the Proteus 1284M/2582M AWG.
    Example of how to call and setup the AWG:
        awg = Proteus()
        awg.sendcommand("") - Send an SCPI command to the awg
        awg.close() - Close the instrument
        Proteus.cleanup() - Close all the session
    '''

    def __init__(self):
        try:
            self.admin = loadDLL()
            self.slotId = self.getSlotId(self.admin)
            if not self.slotId:
                print("Invalid choice!")
            else:
                self.inst = self.admin.OpenInstrument(self.slotId)
                if not self.inst:
                    print("Failed to Open instrument with slot-Id {0}".format(self.slotId))
                    print("\n")
                else:
                    self.instId = self.inst.InstrId
            self.res = self.sendcommand(":SYST:INF:MODel?")
            if self.res.RespStr == "P1284M":
                self.sclk=1.25e9
                self.bits=16
            elif self.res.RespStr == "P2582M":
                self.sclk=2.5e9
                self.bits=16
        except Exception as e:
            print(e)

    def getSlotId(self, admin):
        try:
            admin.Open()
            slotIds = admin.GetSlotIds()
            n = 0
            for i in range(0, slotIds.Length, 1):
                slotId = slotIds[i]
                slotInfo = admin.GetSlotInfo(slotId)
                if slotInfo:
                    if not slotInfo.IsDummySlot:
                        n = n + 1
                        print("Slot-ID {0} -> IDN=\'{1}\' -> Status: IsInUse={2}, IsDummy={3}".
                              format(slotId, slotInfo.GetIdnStr(),
                                     'Yes' if slotInfo.IsSlotInUse != 0 else 'No',
                                     'Yes' if slotInfo.IsDummySlot != 0 else 'No'))
                    else:
                        dummy = 1
                        # print("{0}. Slot-ID {1} - Failed to acquire Slot Information!".format(i + 1,slotId))

            if n == 1:
                sel = slotIds[0]
            else:
                sel = input("Please select slot-Id:")
            slotId = np.uint32(sel)
        except Exception as e:
            print(e)
        return slotId

    def sendcommand(self, command):
        try:
            command = command + "\n"
            inBinDat = bytearray(command, "utf8")
            inBinDatSz = np.uint64(len(inBinDat))
            outBinDatSz = np.uint64([maxScpiResponse])
            outBinDat = bytearray(outBinDatSz[0])
            res = self.inst.ProcessScpi(inBinDat, inBinDatSz, outBinDat, outBinDatSz)
            if (res.ErrCode != 0):
                print("Error {0} ".format(res.ErrCode))
            if (len(res.RespStr) > 0):
                print("{0}".format(res.RespStr))
            #print("\n")
            return res
        except Exception as e:
            print(e)
            return res

    def close(self):
        self.sendcommand("*RST")
        self.admin.CloseInstrument(self.instId)

    def cleanup(self):
        self.admin.Close()

    def Sine(self):
        inst = self.inst
        sclk=self.sclk

        seg_file_path = datapath + '\\segments\\csv\\test.csv'

        # get hw option
        self.sendcommand("*OPT?")
        # reset - must!
        self.sendcommand("*RST")
        # set sampling DAC freq.
        self.sendcommand(":FREQ:RAST {0}".format(sclk))  # takes a long time - not required until power cycle
        # delete all segments in RAM
        # SendScpi(inst, ":TRAC:DEL:ALL") #takes a long time
        self.sendcommand(":TRAC:DEL 1")
        self.sendcommand(":TRAC:DEL 2")
        # common segment defs
        self.sendcommand(":TRAC:DEF:TYPE NORM")

        # load segment
        loadSegment(inst, 1, seg_file_path)

        # select channel
        self.sendcommand(":INST:CHAN 1")
        # Vpp for output = 1V
        self.sendcommand(":SOUR:VOLT 0.5")
        # Arbitrary waveform generation, no trigger
        self.sendcommand(":INIT:CONT ON")
        # define user mode
        self.sendcommand(":SOUR:FUNC:MODE ARB")

        # sel segment 1
        segNum = 1
        self.sendcommand(":SOUR:FUNC:SEG {0}".format(segNum))

        # connect output
        self.sendcommand(":OUTP ON")  # Not required for direct output

        print('Enter 0 to exit')
        while segNum == 1:
            segNum = int(input('Number: '))
            self.sendcommand(":SOUR:FUNC:SEG {0}".format(segNum))

        self.close()