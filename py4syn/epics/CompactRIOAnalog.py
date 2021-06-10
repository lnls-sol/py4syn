"""CompactRIO Analog Acquisition

Class for acquiring CompactRIO analog inputs (via PV or file) with automated
control of downsampling rate (averaging time).

:platform: Unix
:synopsis: Python3 class for hexapods using Symetrie"s proprietary IOC

.. moduleauthors:: Carlos Doro Neto <carlos.doro@lnls.br>
"""


from os.path import join
from time import sleep
from epics import PV
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable


class CompactRIOAnalog(StandardDevice, ICountable):

    # Change tdms to True to use NI tdms files instead of EPICS PVs.
    def __init__(self, mnemonic, pvName, tdms=False):

        super().__init__(mnemonic)

        self.tdms = tdms

        pvPrefix = pvName[:12]

        self._pv = PV(pvName)
        self._pvAvgTime = PV(pvPrefix + "PvAvgTime")
        self._fileAvgTime = PV(pvPrefix + "FileAvgTime")
        self._acquireTrigger = PV(pvPrefix + "AnalogAcqSwTrigger")
        self._filedir = PV(pvPrefix + "AnalogAcqFilepath")
        self._filename = PV(pvPrefix + "AnalogAcqFilename")

        self._pv.wait_for_connection()
        self._pvAvgTime.wait_for_connection()
        self._fileAvgTime.wait_for_connection()
        self._acquireTrigger.wait_for_connection()
        self._filedir.wait_for_connection()
        self._filename.wait_for_connection()

    # ICountable methods overriding

    def getValue(self, **kwargs):
        if self.tdms:
            return self._fileGetValue()
        else:
            return self._pv.get()

    def setCountTime(self, t):
        if self.tdms:
            self._fileAvgTime.put(t, wait=True)
        else:
            self._pvAvgTime.put(t, wait=True)

    def setPresetValue(self, channel, val):
        pass

    def startCount(self):
        self._acquireTrigger.put(1, wait=True)

    def stopCount(self):
        self._acquireTrigger.put(0, wait=True)

    def canStopCount(self):
        return False

    def canMonitor(self):
        return False

    def isCounting(self):
        return self._acquireTrigger.get()

    def wait(self):
        #EMA:B:RIO01:AnalogSaving2File
        if self.tdms:
            sleep(self._fileAvgTime.get())
        else:
            sleep(self._pvAvgTime.get())
        self.stopCount()

    # CompactRIOAnalog specific functions

    def _fileGetValue(self):
        raise NotImplementedError
        # from nptdms import TdmsFile

    def _fileGetPath(self):
        return join(self._filedir.get(), self._filename.get())
