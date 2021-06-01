"""CompactRIO Analog Acquisition

Class for acquiring CompactRIO analog inputs (via PV or file) with automated
control of downsampling rate (averaging time).

:platform: Unix
:synopsis: Python3 class for hexapods using Symetrie"s proprietary IOC

.. moduleauthors:: Carlos Doro Neto <carlos.doro@lnls.br>
"""

from os import path
from warnings import warn

from epics import PV

from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable


class CompactRIOAnalog(StandardDevice, ICountable):

    def __init__(self, mnemonic, pvName):

        super().__init__(mnemonic)

        # Change this to True to use NI tdms files instead of EPICS PVs.
        self.tdms = False

        pvPrefix = pvName[:12]
        warn("py4syn - CompactRIO debug: pvName = " +  pvName)
        warn("py4syn - CompactRIO debug: pvPrefix = " +  pvPrefix)
        warn("py4syn - CompactRIO debug: mnemonic = " +  mnemonic)

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


    ### ICountable methods overriding ###

    def getValue(self, *args, **kwargs):
        warn("py4syn - CompactRIO debug: getValue args = {}".format(args))
        warn("py4syn - CompactRIO debug: getVAlue kwargs = {}".format(kwargs))
        if self.tdms:
            return self._fileGetValue(*args, **kwargs)
        else:
            return self._pvGetValue(*args, **kwargs)


    def setCountTime(self, *args, **kwargs):
        warn("py4syn - CompactRIO debug: setCountTime args = {}".format(args))
        warn("py4syn - CompactRIO debug: setCountTime kwargs = {}".format(kwargs))
        self._pvAvgTime.put(1)
        self._fileAvgTime.put(1)

    def setPresetValue(self, *args, **kwargs):
        warn("py4syn - CompactRIO debug: setPresetValue args = {}".format(args))
        warn("py4syn - CompactRIO debug: setPresetValue kwargs = {}".format(kwargs))
        pass

    def startCount(self, *args, **kwargs):
        warn("py4syn - CompactRIO debug: startCount args = {}".format(args))
        warn("py4syn - CompactRIO debug: startCount kwargs = {}".format(kwargs))
        self._acquireTrigger.put(1)
        # wait for it to actually begin.
        while not self.isCounting():
            pass

    def canMonitor(self, *args, **kwargs):
        warn("py4syn - CompactRIO debug: canMonitor args = {}".format(args))
        warn("py4syn - CompactRIO debug: canMonitor kwargs = {}".format(kwargs))
        return False

    def canStopCount(self, *args, **kwargs):
        warn("py4syn - CompactRIO debug: canStopCount args = {}".format(args))
        warn("py4syn - CompactRIO debug: canStopCount kwargs = {}".format(kwargs))
        return True

    def isCounting(self, *args, **kwargs):
        warn("py4syn - CompactRIO debug: isCounting args = {}".format(args))
        warn("py4syn - CompactRIO debug: isCounting kwargs = {}".format(kwargs))
        return self._acquireTrigger.get()

    def wait(self, *args, **kwargs):
        warn("py4syn - CompactRIO debug: wait args = {}".format(args))
        warn("py4syn - CompactRIO debug: wait kwargs = {}".format(kwargs))
        while self.isCounting():
            pass

    ### XXX specific functions ###

    def _pvGetValue(self, *args, **kwargs):
        return self._pv.get()

    def _fileGetValue(self, *args, **kwargs):
        #from nptdms import TdmsFile
        raise NotImplementedError

    def stopCount(self, *args, **kwargs):
        warn("py4syn - CompactRIO debug: stopCount args = {}".format(args))
        warn("py4syn - CompactRIO debug: stopCount kwargs = {}".format(kwargs))
        self._acquireTrigger.put(0)

    def _fileGetPath(self, *args, **kwargs):
        warn("py4syn - CompactRIO debug: _fileGetPath args = {}".format(args))
        warn("py4syn - CompactRIO debug: _fileGetPath kwargs = {}".format(kwargs))
        return path.join(self._filedir.get(), self._filename.get())

