import os
import sys
import inspect
import sys
import clr  # allows to interact with .NET common language runtime
import ctypes  # allows C compatible data types and calling functions in DLLs or shared libraries
import time
import numpy as np
from tools.instFunction import *

maxScpiResponse = 65535
root = os.path.dirname(os.path.abspath(__file__))
dllpath = root + '\\admin\\TEPAdmin.dll'
datapath = root + '\\data\\'


class Proteus:
    """This is the class def for the Proteus 1284M/2582M AWG.
    Example of how to call and setup the AWG:
        awg = Proteus()
        awg.sendcommand("command") - Send an SCPI command to the awg
        awg.close() - Close the instrument
        awg.cleanup() - Close all the sessions
    """

    def __init__(self):
        try:
            self.admin = self.loadDLL()  # Initializes the DLL file
            self.slotId = self.getslotID(self.admin)  # Uses the DLL file to call the instruments
            if not self.slotId:
                print("Error in Obtaining SlotID: Please check the connection and restart!")
                sys.exit()
            else:
                self.inst = self.admin.OpenInstrument(self.slotId)
                if not self.inst:
                    print(f"Error in Initializing instrument with slot-Id {self.slotId}\n")
                else:
                    self.instId = self.inst.InstrId
            self.resp = self.sendcommand(":SYST:INF:MODel?")
            if self.resp == "P1284M":
                self.sclk = 1.25e9
                self.bits = 16
        except Exception as e:
            print(e)

    def loadDLL(self):
        # This function loads the .NET DLL into memory
        clr.AddReference(dllpath)
        from TaborElec.Proteus.CLI.Admin import CProteusAdmin
        from TaborElec.Proteus.CLI.Admin import IProteusInstrument
        return CProteusAdmin()

    def getslotID(self, admin):
        try:
            admin.Open()
            slotIds = admin.GetSlotIds()
            n = 0
            for i in range(0, slotIds.Length, 1):
                slotId = slotIds[i]
                slotInfo = admin.GetSlotInfo(slotId)
                if slotInfo:
                    if not slotInfo.IsDummySlot:
                        n += 1
                        print(f"{slotInfo.GetIdnStr()} in Slot {slotId} -> IsInUse={'Yes' if slotInfo.IsSlotInUse != 0 else 'No'}")
            if n == 1:
                sel = slotIds[0]
            else:
                sel = input("Please select slot-Id:")
            if sel == 0:
                self.admin.Close()
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
            resp = res.RespStr
            if res.ErrCode != 0:
                print(f"Error {res.ErrCode}")
            return resp
        except Exception as e:
            print(e)
            return resp

    def find_file_type(self, seg_file):
        if ".csv" in seg_file:
            file_type = "csv"
        if ".bin" in seg_file:
            file_type = "bin"
        if ".seg" in seg_file:
            file_type = "bin"
        return file_type

    def readfile(self, seg_file):
        file_type = self.find_file_type(seg_file)
        if file_type == "bin":
            bin_dat = np.fromfile(file=seg_file, dtype=np.uint8)
        else:
            bin_dat = np.loadtxt(fname=seg_file, dtype=np.uint16, delimiter=',')
        bin_dat = bin_dat.view(dtype=np.uint8)
        seg_len = int(len(bin_dat) / 2)
        return bin_dat, seg_len

    def loadsegment(self, seg_num, seg_file_path):
        bin_dat, seg_len = self.readfile(seg_file_path)
        self.sendcommand(f":TRACe:DEF {seg_num},{seg_len}")
        self.sendcommand(f":TRACe:SEL {seg_num}")

        inDatLength = len(bin_dat)
        inDatOffset = 0
        res = self.inst.WriteBinaryData(":TRAC:DATA 0,#", bin_dat, inDatLength, inDatOffset)

        if res.ErrCode != 0:
            print("Error {0} ".format(res.ErrCode))
        else:
            if len(res.RespStr) > 0:
                print("{0}".format(res.RespStr))

    def sendfile(self):
        pass

    def green_on(self):
        self.sendcommand(":INST:CHAN 2")
        self.sendcommand(":MARK:SEL 1")
        self.sendcommand(":MARK:ON")

    def green_off(self):
        self.sendcommand(":INST:CHAN 2")
        self.sendcommand(":MARK:SEL 1")
        self.sendcommand(":MARK:OFF")

    def close(self):
        self.sendcommand("*RST")
        self.admin.CloseInstrument(self.instId)

    def cleanup(self):
        self.admin.Close()

    def sample_wave(self):
        seg_file_path = datapath + 'segments\\csv\\FiveCyclesSine_16Bit2048pts.csv'
        seg_file_path = r"C:\Users\Duttlab\Desktop\Waveform_1.seg"

        # Reset AWG to Factory settings
        self.sendcommand("*RST")

        # Set sampling DAC freq.
        self.sendcommand(f":FREQ:RAST {self.sclk}")  # takes a long time - not required until power cycle

        # Delete all segments in RAM
        self.sendcommand(":TRAC:DEL:ALL")

        # Common segment defs
        self.sendcommand(":TRAC:DEF:TYPE NORM")

        # load segment
        self.loadsegment(1, seg_file_path)

        # Select Channel
        self.sendcommand(":INST:CHAN 1")
        # Vpp for output = 1V
        self.sendcommand(":SOUR:VOLT 1.0")
        # Arbitrary waveform generation, no trigger
        self.sendcommand(":INIT:CONT ON")
        # define user mode
        self.sendcommand(":SOUR:FUNC:MODE ARB")

        # Select the segment number
        segNum = 1
        self.sendcommand(f":SOUR:FUNC:SEG {segNum}")

        # connect output
        self.sendcommand(":OUTP ON")  # Not required for direct output

        print('Enter 0 to exit')
        while segNum == 1:
            segNum = int(input('Number: '))
            self.sendcommand(":SOUR:FUNC:SEG {0}".format(segNum))

        self.close()
        self.cleanup()
