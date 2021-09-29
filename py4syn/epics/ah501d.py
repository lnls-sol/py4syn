from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
import epics
from time import sleep, time


class AH501D(StandardDevice, ICountable):
    """
    Class to control CAEN AH501D via EPICS.
    --------
    """

    def onAcquireChange(self, value, **kw):
        self._done = (value == 0)

    def __init__(self, mnemonic, pv, trigger):
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
        self._done = 1
        self.pvAcquire = epics.PV(
            pv + ':Acquire', callback=self.onAcquireChange)
        self.pvAcquireMode = epics.PV(pv + ':AcquireMode')
        self.pvCurrent = epics.PV(pv + ':Current1:MeanValue_RBV')
        self.pvNumCounter = epics.PV(pv + ':NumAcquired')
        self.pvAveragingTime = epics.PV(pv + ':AveragingTime')
        self.pvTriggerMode = epics.PV(pv + ':TriggerMode')

        self.pvReadData = epics.PV(pv + ':ReadData')
        self.clearBuffer()

        # define acquiremode and trigger Mode
        if trigger == 'External':
            self.pvAcquireMode.put(0)  # Continuous
            self.pvTriggerMode.put(1)  # Ext. gate
            self.pvAcquire.put(1)
        else:
            self.pvAcquireMode.put(2, wait=True)  # Single
            self.pvTriggerMode.put(0, wait=True)  # Free run

    def close(self):
        """
        Stops an ongoing acquisition, if any, and puts the EPICS IOC in idle state.
        """
        self._done = 1

    def clearBuffer(self):
        self.pvReadData.put(1)
        sleep(0.1)
        self.pvReadData.put(0)

    def getIntensity(self):
        return self.pvCurrent.get()

    def getValue(self, **kwargs):
        value = self.getIntensity()
        return value

    def setCountTime(self, t):
        """
        Sets the acquisition time.
        Parameters
        ----------
        t : `float`
            Acquisition time
        """
        self.pvAveragingTime.put(t, wait=True)

#    def getAcquireTime(self):
#        pass

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
        self.pvAcquire.put(1)
        self._done = 0

    def stopCount(self):
        """
        Stops acquiring. This method simply calls :meth:`close`.

        See: :meth:`close`
        """
        # self.pvAcquire.put(0)
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
