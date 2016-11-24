"""
Vortex MCA class

Python class for Vortex MCA using EPICS area detector IOC.

:platform: Unix
:synopsis: Python class for Vortex MCA

.. moduleauthor:: Douglas Bezerra Beniz <douglas.beniz@lnls.br>

"""
from threading import Event

from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
from epics import PV, ca, caput

from time import sleep


class VortexMCA(StandardDevice, ICountable):
    """
    Class to control Vortex MCA via EPICS.

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
            A mnemonic for the MCA
        pv : `string`
            Base name of the EPICS process variable
        """
        super().__init__(mnemonic)
        self.pvAcquire = PV(pv + ':EraseStart')
        self.pvStatus = PV(pv + ':Acquiring', callback=self.onAcquireChange)
        self.pvAcquireTime = PV(pv + ':PresetLive')

        self.pvMcaCounters = []

        # Channels 1-4
        for i in range(1, 5):
            # Only ROI 0 (1st region)
            self.pvMcaCounters.append(PV(pv + ':mca' + str(i) + '.R0'))

        # Channel 5 represents SUM
        self.pvMcaCounters.append(PV(pv + ':mcaAll:sum'))

        # Channel 6 represents DIV
        self.pvMcaCounters.append(PV(pv + ':mcaAll:div'))


    def close(self):
        """
        Stops an ongoing acquisition, if any, and puts the EPICS IOC in idle state.
        """
        self.pvAcquire.put(0, wait=True)


    def getIntensity(self, channel=1):
        return self.pvMcaCounters[channel-1].get()


    def getValue(self, **kwargs):
        if(kwargs):
            return self.getIntensity(kwargs['channel'])
        return self.getIntensity()


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
        Starts acquiring an image. It will acquire for the duration set with
        :meth:`setCountTime`. The resulting file will be stored in the file set with
        :meth:`setImageName`.

        See: :meth:`setCountTime`, :meth:`setImageName`

            Examples
            --------
            >>> def acquire(pilatus, time, filename):
            ...     pilatus.setCountTime(time)
            ...     pilatus.setImageName(filename)
            ...     pilatus.startCount()
            ...     pilatus.wait()
            ...     pilatus.stopCount()
            ...
        """
        if not self._done:
            raise RuntimeError('Already counting')

        self.pvAcquire.put(1)


    def stopCount(self):
        """
        Stops acquiring the image. This method simply calls :meth:`close`.
        
        See: :meth:`close`
        """
        self.close()


    def canMonitor(self):
        """
        Returns false indicating that Pilatus cannot be used as a counter monitor.
        """
        return False


    def canStopCount(self):
        """
        Returns true indicating that Pilatus has a stop command.
        """
        return True


    def isCounting(self):
        """
        Returns true if the camera is acquiring an image, or false otherwise.

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
