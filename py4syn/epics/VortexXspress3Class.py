"""
Vorter XSPRESS3 class

Python class for Vortex using EPICS area detector IOC.

:platform: Unix
:synopsis: Python class for Vortex with xspress3

.. moduleauthor:: Douglas Araujo<douglas.araujo@lnls.br>
                  Luciano Carneiro Guedes<luciano.guedes@lnls.br>
"""

from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
import epics

from time import sleep, time


class VortexXspress3(StandardDevice, ICountable):
    """
    Class to control Vortex via EPICS.
    Examples
    --------
    """

    def onAcquireChange(self, value, **kw):
        self._done = (value == 0)


    def __init__(self, mnemonic, pv):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`
        Parameters
        ----------
        mnemonic : `string`
            A mnemonic for the detector
        pv : `string`
            Base name of the EPICS process variable
        """
        super().__init__(mnemonic)
        self.pvAcquire = epics.PV(pv + ':Acquire')
        self.pvStatus = epics.PV(pv + ':Acquire_RBV', callback=self.onAcquireChange)
        self.pvAcquireTime = epics.PV(pv + ':AcquireTime')
        self.pvClear = epics.PV(pv + ':ERASE')

        self.pvMcaCounters = []
        self.pvStatusScan = epics.PV(pv + ':Acquire_RBV.SCAN')
        self.pvStatusScan.put(2)

	
    def close(self):
        """
        Stops an ongoing acquisition, if any, and puts the EPICS IOC in idle state.
        """
        self._done = 1


    def getIntensity(self, channel=1):
        return self.pvMcaCounters[channel-1].get()


    def getValue(self, **kwargs):
        return True


    def setCountTime(self, t):
        """
        Sets the image acquisition time.
        Parameters
        ----------
        t : `float`
            Acquisition time
        """
        self.pvAcquireTime.put(t, wait=True)


    def getAcquireTime(self):
        return self.pvAcquireTime.get()


    def setPresetValue(self, channel, val):
        """
        Dummy method to set initial counter value.
        """
        pass


    def startCount(self):
        """
        Starts acquiring 
        """
        if not self._done:
            raise RuntimeError('Already counting')
        self.pvClear.put(1) # clear the ROI value before start a new acquire
        self.pvAcquire.put(1)
        self._done = 0 # force the confirmation that the detector has already received acquire function


    def stopCount(self):
        """
        Stops acquiring. This method simply calls :meth:`close`.
        
        See: :meth:`close`
        """
        self.pvAcquire.put(0)
        self.close()


    def canMonitor(self):
        """
        Returns false indicating that vortex cannot be used as a counter monitor.
        """
        return False


    def canStopCount(self):
        """
        Returns true indicating that vortex has a stop command.
        """
        return True


    def isCounting(self):
        """
        Returns true if the detector is acquiring, or false otherwise.
        Returns
        -------
        `bool`
        """
        return not self._done


    def wait(self):
        """
        Blocks until the acquisition completes.
        """
        while not self._done:
            epics.poll(evt=1.e-5, iot=0.1)