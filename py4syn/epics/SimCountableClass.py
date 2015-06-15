import random
import datetime
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable

"""SimCountable Class

Python class to add simulated ICountable support

:platform: Unix
:synopsis: Python Class to add simulated ICountable object

.. moduleauthor:: Hugo Henrique Slepicka <hugo.slepicka@lnls.br>  

"""
class SimCountable(StandardDevice, ICountable):
    """
    Class to add simulated ICountable support.

    Examples
    --------
    >>> from py4syn.epics.SimCountableClass import SimCountable
    >>>
    >>> myCountable = SimCountable('TEST:FAKE_COUNTER','myCounter')
    >>> myCountable.getValue()
    >>>     
    """
    def __init__(self, pvName, mnemonic):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`
        See :class:`py4syn.epics.ICountable`
        
        Parameters
        ----------
        pvName : `string`
            PV name (Process Variable)
        mnemonic : `string`
            Mnemonic
        """        
        StandardDevice.__init__(self, mnemonic)
        self.pvName = pvName
        self.countTime = 1
        self.value = 0
    
    def getValue(self, **kwargs):
        """
        Get the current value of a countable device.

        Parameters
        ----------
        kwargs : value
            Where needed informations can be passed, e.g. select which channel must be read.

        Returns
        -------
        out : value
            Returns the current value of the device. Type of the value depends on device settings.
        """
        return self.value

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
        self.countTime = t
    
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
        pass
    
    def startCount(self):
        """
        Abstract method trigger a count in a counter

        """
        self.startTime = datetime.datetime.now()
        self.value = int(random.random()*100*self.countTime) 
    
    def stopCount(self):
        """
        Abstract method stop a count in a counter

        """
        self.endTime = datetime.datetime.now()

    def canMonitor(self):
        """
        Abstract method to check if the device can or cannot be used as monitor.

        Returns
        -------
        out : `bool`
        """        
        return False

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
        try:
            if((datetime.datetime.now()-self.startTime).total_seconds() < self.countTime):
                return True
        except:
            pass
        return False
        
    def wait(self):
        """
        Abstract method to wait for a count to finish.

        Returns
        -------
        out : `bool`
        """
        import time
        while(self.isCounting()):
            time.sleep(0.0001)
        