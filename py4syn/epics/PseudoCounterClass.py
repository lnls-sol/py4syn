"""Pseudo counter class

Python class that creates a pseudo counter that has, as value, the result of a
calculation based on the values of other counters.

:platform: Unix
:synopsis: Python Class for Pseudo counters

.. moduleauthor:: Hugo Slepicka <hugo.slepicka@lnls.br>

"""

from epics import ca
from math import *
import numpy
from py4syn import *
from py4syn.epics.ICountable import ICountable
from py4syn.epics.StandardDevice import StandardDevice

class counterValue():
    """
    Class to globally retrieve value of counters
    """

    def __getitem__(self, m):
        """
        Get current value of the requested counter

        Parameters
        ----------
        m : `dictionary`
            Represents the counter, in the `counterDB` dictionary

        Returns
        -------
        `double`
            Read the current value
        """

        global counterDB

        v = counterDB[m]
        dev = v['device']
        cnt = 0
        if(v['channel'] is not None):
            cnt = dev.getValue(channel=v['channel'])
        else:
            cnt = dev.getValue()

        return cnt

class PseudoCounter(ICountable, StandardDevice):
    """
    Class to control Pseudo-Counter (virtual counter).

    Examples
    --------
    >>> # Create a Simulated Counter    
    >>> scaler = SimCountable("SOL:SCALER01", 2)
    >>>
    >>> # Create two channels: det and mon
    >>> createCounter("mon", scaler, 1)
    >>> createCounter("det", scaler, 2)
    >>>
    >>> # Create a Pseudo counter with the formula
    >>> pseudoCounter = PseudoCounter("relation", "C[det]/C[mon]")
    >>>
    >>> # Create a new channel based on this pseudo-counter
    >>> createCounter("relation", pseudoCounter)
    >>>
    >>> # Start a count process
    >>> ct(1)
    >>>
    """

    def __init__(self, mnemonic, backwardFormula):
        """
        **Pseudo Counter class Constructor**

        Parameters
        ----------
        mnemonic : `string`
            Counter mnemonic

        backwardFormula : `string`
            Mathematical Formula used to calculate the Pseudo counter value position based on other counters
        """
        StandardDevice.__init__(self, mnemonic)
        self.name = mnemonic
        self.backFormula = backwardFormula

    def __str__(self):
        return self.getMnemonic()

    def __defineCounters(self):
        """
        Define a set of virtual counters based on devices in the global `mtrDB`

        Returns
        -------
        `string`
            A command which combines all devices in `mtrDB`

        """

        global mtrDB
        cmd = '\n'.join(['%s = "%s"' % (c, c) for c in counterDB])
        return cmd

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
        global counterDB
        global C
        exec(self.__defineCounters())
        try:
            return eval(self.backFormula)
        except Exception as ex:
            print('Warning while getting pseudo counter value:', ex)
            return 0.0

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


C = counterValue()
