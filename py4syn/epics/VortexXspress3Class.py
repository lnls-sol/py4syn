"""
Vorter XSPRESS3 class

Python class for Vortex using EPICS area detector IOC.

:platform: Unix
:synopsis: Python class for Vortex with xspress3

.. moduleauthor:: Douglas Araujo<douglas.araujo@lnls.br>
                  Luciano Carneiro Guedes<luciano.guedes@lnls.br>
"""

from threading import Event

from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
from epics import PV, ca, caput

from time import sleep, time


class VortexXspress3(StandardDevice, ICountable):
    """
    Class to control Vortex via EPICS.
    Examples
    --------
    """


    RESPONSE_TIMEOUT = 15
    WAIT_ACQUIRING = 0.005


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
        self.pvAcquire = PV(pv + ':Acquire')
        self.pvStatus = PV(pv + ':Acquire_RBV', callback=self.onAcquireChange)
        self.pvAcquireTime = PV(pv + ':AcquireTime')
        self.pvClear = PV(pv + ':ERASE')

        self.pvMcaCounters = []
        self.pvStatusScan = PV(pv + ':Acquire_RBV.SCAN')
        self.pvStatusScan.put(9)

        self.inicio = time()
        self.fim = 0

        # Channels 1-4
        for i in range(1, 5):
            for j in range(1, 5):            
               self.pvMcaCounters.append(PV(pv + ':C' + str(j) + '_ROI'+str(i)+':Value_RBV'))
        self.pvClear.put(1, wait=True)
        
	
    def close(self):
        """
        Stops an ongoing acquisition, if any, and puts the EPICS IOC in idle state.
        """
        pass


    def getIntensity(self, channel=1):
        return self.pvMcaCounters[channel-1].get()


    def getValue(self, **kwargs):
        if(kwargs):                 
            count = 0            
            a=self.getIntensity(kwargs['channel'])
            while (a==0 and count < 3):
                sleep(.05) 
                a = self.getIntensity(kwargs['channel'])
                count+=1
            return a


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
        self.pvClear.put(1, wait=True) # clear the ROI value before start a new acquire
        self.pvAcquire.put(1)
        self._done = 0 # force the confirmation that the detector has already received acquire function
        


    def stopCount(self):
        """
        Stops acquiring. This method simply calls :meth:`close`.
        
        See: :meth:`close`
        """
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
            sleep(self.WAIT_ACQUIRING)
        sleep(0.2)
