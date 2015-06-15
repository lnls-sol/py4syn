"""PyLoN Charge-Coupled Devices (CCD) Class

Python Class for EPICS LabView RT Detector control of Princeton Instruments
PyLoN camera.

:platform: Unix
:synopsis: Python Class for EPICS LabView RT Detector control of Princeton
Instruments PyLoN camera.

.. moduleauthor:: Douglas Bezerra Beniz <douglas.beniz@lnls.br>
    .. note:: 16/04/2015 [douglas.beniz]  first version released
"""

from time import sleep
from enum import Enum
from epics import PV
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable

class PylonCCDTriggered(StandardDevice, ICountable):
    """
    Python class to help configuration and control of Charge-Coupled Devices
    (CCD) via Hyppie over EPICS.
    
    CCD is the most common mechanism for converting optical images to electrical
    signals. In fact, the term CCD is know by many people because of their use
    of video cameras and digital still cameras.
    """
    
    # PyLoN CCD callback function for acquire status
    def onAcquireChange(self, value, **kw):
        # print datetime.datetime.now(), " - Acquisition Done = ", (value == 0)
        self._done = (value == 0)
    
    # PyLoN CCD constructor
    def __init__(self, pvNameIN, pvNameOUT, mnemonic, scalerObject=""):
        StandardDevice.__init__(self, mnemonic)
        # IN   DXAS:DIO:bi8         # 1.0   (read TTL OUT from CCD)
        # OUT  DXAS:DIO:bo17        # 6.1   (write Trigger IN to CCD start acquisition)
        self.pvAcquire = PV(pvNameOUT)
        self.pvMonitor = PV(pvNameIN, callback=self.onAcquireChange)
        self._done = self.isDone()
        self.countTime = 1

    def isDone(self):
        return (self.pvMonitor.get() == 0)

    def acquire(self, waitComplete=False):
        self.pvAcquire.put(1)
        sleep(0.01)
        self.pvAcquire.put(0)
        self._done = False
        if(waitComplete):
            self.wait()

    def waitFinishAcquiring(self):
        while(not self._done):
            sleep(0.001)

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
        sleep(t)

    def wait(self):
        """
        Wait for a complete PyLoN CCD acquiring process to finish.

        Returns
        -------
        out : `bool`
        """
        self.waitFinishAcquiring()

    def startCount(self):
        """
        Trigger the acquisition process of PyLoN CCD.

        """
        self.acquire(True)
        
    def stopCount(self):
        """
        Stop acquisition process.  It does not make sense to PyLoN CCD, just passing it...

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
        return (not self.isDone())

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
        return 0
