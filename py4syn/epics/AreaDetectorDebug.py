"""AreaDetector debug class

An areaDetector class for debugging scan-utils calls.

:platform: Unix
:synopsis: Python3 class for debugging scan-utils calls to areaDetector

.. moduleauthor:: Carlos Doro Neto <carlos.doro@lnls.br>
"""

from random import random
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable


class AreaDetectorClass(StandardDevice, ICountable):

    def __init__(self, *args, **kwargs):
        print("constructor")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        super().__init__(args[0])

    def getNframes(self, *args, **kwargs):
        print("getNframes")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return int(1000*random())

    def setNframes(self, *args, **kwargs):
        print("setNframes")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def getFileName(self, *args, **kwargs):
        print("getFileName")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return "AreaDetectorDebug"

    def setFileName(self, *args, **kwargs):
        print("setFileName")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def getFilePath(self, *args, **kwargs):
        print("getFilePath")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return "/tmp/"

    def setFilePath(self, *args, **kwargs):
        print("setFilePath")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def getImageMode(self, *args, **kwargs):
        print("getImageMode")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return 0

    def setImageMode(self, *args, **kwargs):
        print("setImageMode")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def getTriggerMode(self, *args, **kwargs):
        print("getTriggerMode")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return 0

    def setTriggerMode(self, *args, **kwargs):
        print("setTriggerMode")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def getEnableCallback(self, *args, **kwargs):
        print("getEnableCallback")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return True

    def setEnableCallback(self, *args, **kwargs):
        print("setEnableCallback")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def getAutoSave(self, *args, **kwargs):
        print("getAutoSave")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return True

    def setAutoSave(self, *args, **kwargs):
        print("setAutoSave")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def getNextraDim(self, *args, **kwargs):
        print("getNextraDim")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return 2

    def setNextraDim(self, *args, **kwargs):
        print("setNextraDim")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def getDimX(self, *args, **kwargs):
        print("getDimX")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return int(1000*random())

    def setDimX(self, *args, **kwargs):
        print("setDimX")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def getDimY(self, *args, **kwargs):
        print("getDimY")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return int(1000*random())

    def setDimY(self, *args, **kwargs):
        print("setDimY")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def getWriteMode(self, *args, **kwargs):
        print("getWriteMode")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return 0

    def setWriteMode(self, *args, **kwargs):
        print("setWriteMode")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def getOutputFormat(self, *args, **kwargs):
        print("getOutputFormat")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return "%s%s_%04d.txt"

    def setOutputFormat(self, *args, **kwargs):
        print("setOutputFormat")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def getRepeatNumber(self, *args, **kwargs):
        print("getRepeatNumber")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return int(1000*random())

    def setRepeatNumber(self, *args, **kwargs):
        print("setRepeatNumber")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def startCapture(self, *args, **kwargs):
        print("startCapture")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def stopCapture(self, *args, **kwargs):
        print("stopCapture")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def setParams(self, *args, **kwargs):
        print("setParams")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def getAcquireTime(self, *args, **kwargs):
        print("getAcquireTime")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return int(1000*random())

    def setWriteParams(self, *args, **kwargs):
        print("setWriteParams")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def close(self, *args, **kwargs):
        print("close")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def getIntensity(self, *args, **kwargs):
        print("getIntensity")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return int(1000*random())

    # ICountable methods overriding

    def getValue(self, *args, **kwargs):
        print("getValue")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return int(1000*random())

    def setCountTime(self, *args, **kwargs):
        print("setCountTime")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def setPresetValue(self, *args, **kwargs):
        print("setPresetValue")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def startCount(self, *args, **kwargs):
        print("startCount")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def stopCount(self, *args, **kwargs):
        print("stopCount")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")

    def canMonitor(self, *args, **kwargs):
        print("canMonitor")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return True

    def canStopCount(self, *args, **kwargs):
        print("canStopCount")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return True

    def isCounting(self, *args, **kwargs):
        print("isCounting")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
        return False

    def wait(self, *args, **kwargs):
        print("wait")
        print("args = ", args)
        print("kwargs = ", kwargs)
        print("---")
