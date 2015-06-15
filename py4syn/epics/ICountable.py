"""Countable Interface

Python interface to support Abstract methods related to Counting process.

:platform: Unix
:synopsis: Python Interface with Abstract methods for Counting process (Countable Devices). 

.. moduleauthor:: Hugo Henrique Slepicka <hugo.slepicka@lnls.br>
    .. note:: 22/07/2014 [hugo.slepicka]  first version released

"""

from abc import ABCMeta, abstractmethod
import sys

class ICountable:
    """
    Python interface to be implemented in all devices in order to create default methods for Counting process

    A countable is any device in which a counting process is feasible to be performed.

    """
    SECONDS = "seconds"
    INFINITY_TIME = (2**32)-1
    
    @abstractmethod
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

        raise NotImplementedError

    @abstractmethod
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

        raise NotImplementedError

    @abstractmethod
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

        raise NotImplementedError

    @abstractmethod
    def startCount(self):
        """
        Abstract method trigger a count in a counter

        """

        raise NotImplementedError
        
    @abstractmethod
    def stopCount(self):
        """
        Abstract method stop a count in a counter

        """

        raise NotImplementedError

    @abstractmethod
    def canMonitor(self):
        """
        Abstract method to check if the device can or cannot be used as monitor.

        Returns
        -------
        out : `bool`
        """        
        raise NotImplementedError

    @abstractmethod
    def canStopCount(self):
        """
        Abstract method to check if the device can or cannot stop the count and return values.

        Returns
        -------
        out : `bool`
        """        
        raise NotImplementedError
    
    
    @abstractmethod
    def isCounting(self):
        """
        Abstract method to check if the device is counting or not.

        Returns
        -------
        out : `bool`
        """        
        raise NotImplementedError
    
    @abstractmethod
    def wait(self):
        """
        Abstract method to wait for a count to finish.

        Returns
        -------
        out : `bool`
        """        
        raise NotImplementedError
        
