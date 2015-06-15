from epics import PV
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable

"""Countable PV Class

Python class to add fake ICountable support for generic PV

:platform: Unix
:synopsis: Python Class to add ICountable to Generic PV

.. moduleauthor:: Henrique Dante de Almeida <henrique.almeida@lnls.br>  

"""
class CountablePV(StandardDevice, ICountable):
    """
    Class to add fake ICountable support for generic PV.

    Examples
    --------
    >>> from py4syn.epics.CountablePVClass import CountablePV
    >>>
    >>> myCountable = CountablePV('LNLS:ANEL:corrente','corrente')
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
        self.pv = PV(pvName)
    
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
        return self.pv.get()

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
        pass
    
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
        pass
    
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
        return False
        
    def wait(self):
        """
        Abstract method to wait for a count to finish.

        Returns
        -------
        out : `bool`
        """        
        pass
        