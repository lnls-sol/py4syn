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
from datetime import datetime
from enum import Enum
from epics import PV
from py4syn.epics.PylonCCDClass import PylonCCD

class PylonCCDTriggered(PylonCCD):
    """
    Python class to help configuration and control of Charge-Coupled Devices
    (CCD) via Hyppie over EPICS and external trigger mechanism.
    
    CCD is the most common mechanism for converting optical images to electrical
    signals. In fact, the term CCD is know by many people because of their use
    of video cameras and digital still cameras.
    """
    
    # PyLoN CCD callback function for acquire status
    def onAcquireChange(self, value, **kw):
        self._done = (value == 0)
    
    # PyLoN CCD constructor
    def __init__(self, pvName, pvNameIN, pvNameOUT, mnemonic, accumulations=1):
        # IN   DXAS:DIO:bi8         # 1.0   (read TTL OUT from CCD)
        # OUT  DXAS:DIO:bo17        # 6.1   (write Trigger IN to CCD start acquisition)
        self.pvTriggerAcquire = PV(pvNameOUT)
        self.pvMonitor = PV(pvNameIN, callback=self.onAcquireChange)
        # Number of accumulations per frame
        self.accumulations = accumulations
        # Then call parent initializer
        PylonCCD.__init__(self, pvName, mnemonic)

    def isDone(self):
        return (self.pvMonitor.get() == 0)

    def acquire(self, waitComplete=False):
        # Necessary wait if a pause command was sent to the system
        # This is being used by furnace experiments (temperature scan)
        while (self.isPaused):
            sleep(0.2)
        
        for currentAccumulation in range(self.accumulations):
            self.pvTriggerAcquire.put(1)
            sleep(0.01)
            self.pvTriggerAcquire.put(0)
            #######################################################################
            # During the tests we observed that some times the trigger (in the resolution
            # we are using) is faster than the 'capacity' of the CCD to read the input
            # signal...
            # 
            # So, as any received trigger input during an acquisition is ignored, and
            # e need to guarantee that all spectra is acquired, after the first trigger
            # signal we wait 10 ms and send a new trigger.
            sleep(0.01)
            self.pvTriggerAcquire.put(1)
            sleep(0.01)
            self.pvTriggerAcquire.put(0)
            # Set the attribute of done acquisition to False
            self._done = False
            if(waitComplete):
                self.wait()

    def startLightFieldAcquisition(self):
        self.pvAcquire.put(1)

    def waitFinishAcquiring(self):
        while(not self._done):
            sleep(0.005)

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
    
    def isCounting(self):
        """
        Abstract method to check if the device is counting or not.

        Returns
        -------
        out : `bool`
        """
        return (not self.isDone())
