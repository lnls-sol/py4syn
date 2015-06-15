"""
FILENAME... MythenClass.py
USAGE...    Python Class for EPICS Mythen
 
/*
 *      Original Author: Henrique Ferreira Canova
 *      Date: 10/03/2014
 */
"""

from epics import PV
from time import sleep
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable

class Mythen(StandardDevice, ICountable):

    def finish(self, value, **kw):
        if value == 0:
            self.mythenfinish = True
        else:
            self.mythenfinish = False

    def __init__ (self,pvPrefix, mnemonic):
        StandardDevice.__init__(self, mnemonic)
        self.pvAcquire = PV(pvPrefix + ":Acquire")
        self.pvTime = PV(pvPrefix + ":Time")
        self.pvDataRBV = PV(pvPrefix+ ":Data_RBV")
        self.pvAcquireRBV = PV(pvPrefix+":Acquire_RBV")
        self.pvAcquireRBV.add_callback(self.finish)
        self.pvSettings = PV(pvPrefix+":Settings") 
        self.pvFlatfield = PV(pvPrefix+":FlatfieldCorrection")
        self.pvFlatfieldRBV = PV(pvPrefix+":FlatfieldCorrection_RBV")
        self.pvFlip = PV(pvPrefix + ":FlipChannels")
        self.pvFlipRBV = PV(pvPrefix + ":FlipChannels_RBV")
 
        self.mythenfinish = (self.pvAcquireRBV.get() == 0)

    def changeTime(self,tempo):
        self.pvTime.put(tempo*10000000)
    
    def acquire(self):
        self.pvAcquire.put(1)
        self.mythenfinish = False
        #sleep(0.1)
    
    def readout(self):
        return self.pvDataRBV.get()
        
    def waitFinish(self):
        while not self.mythenfinish:
            sleep(0.001)
        
    def settings(self,settings=""):
        self.pvSettings.put(settings)

    def setFlatfield(self,bool):
        if ((bool != 0) and (bool != 1)):
            self.pvFlatfield.put(0)
        else:
            self.pvFlatfield.put(bool)

    def readFlatfield(self):
        return self.pvFlatfieldRBV.get()

    def setFlip(self,bool):
        if ((bool != 0) and (bool != 1)):
            self.pvFlip.put(1)
        else:
            self.pvFlip.put(bool)

    def readFlip(self):
        return self.pvFlipRBV.get()
        
    def getValue(self, **kwargs):
        """
        Abstract method to get the current value of a countable device.

        Parameters
        ----------
        kwargs : value
            Where needed informations can be passed, e.g. select which channel must be read.

        Returns
        -------
        out : value
            Returns the current value of the device. Type of the value depends on device settings.
        """
        return self.readout()

    def setCountTime(self, t):
        """
        Abstract method to set the count time of a countable target device.

        Parameters
        ----------
        t : value
            The target count time to be set.

        Returns
        -------
        out : None
        """
        self.changeTime(abs(t))

    def setPresetValue(self, channel, val):
        """
        Abstract method to set the preset count of a countable target device.

        Parameters
        ----------
        channel : `int`
            The monitor channel number
        val : `int`
            The preset value

        Returns
        -------
        out : None
        """
        self.changeTime(abs(val))
        
    def startCount(self):
        """
        Abstract method trigger a count in a counter

        """
        self.acquire()
        
    def stopCount(self):
        """
        Abstract method stop a count in a counter

        """
        pass

    def canMonitor(self):
        """
        Abstract method to check if the device can or cannot be used as monitor.

        Returns
        -------
        out : `bool`
        """        
        return True

    def canStopCount(self):
        """
        Abstract method to check if the device can or cannot stop the count and return values.

        Returns
        -------
        out : `bool`
        """        
        return True
    
    
    def isCounting(self):
        """
        Abstract method to check if the device is counting or not.

        Returns
        -------
        out : `bool`
        """
        return (not self.mythenfinish)
    
    def wait(self):
        """
        Abstract method to wait for a count to finish.

        Returns
        -------
        out : `bool`
        """        
        self.waitFinish()
            
