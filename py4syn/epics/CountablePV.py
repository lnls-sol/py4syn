from time import sleep, time

from epics import PV
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable

class CountablePV(StandardDevice, ICountable):
        '''Adds fake ICountable support for generic PV'''
        def __init__(self, pvName, mnemonic):
                StandardDevice.__init__(self, mnemonic)
                self.pvName = pvName
                self.pv = PV(pvName)
                self._count_start = 0.0
        
        def getValue(self, **kwargs):
                return self.pv.get()

        def setCountTime(self, t):
                self.countTime = t
        
        def setPresetValue(self, channel, val):
                pass
        
        def startCount(self):
                # sleep(self.countTime)
                self._count_start = time()
        
        def stopCount(self):
                pass
        
        def canMonitor(self):
                return False
        
        def canStopCount(self):
                return True
        
        def isCounting(self):
                return False
        
        def wait(self):
                while(time() - self._count_start < self.countTime):
                        pass
                return

