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

TIMEOUT_SECONDS = 10
WAIT_ACQUIRING  = 0.010           

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
        # If 'Output Signal' of Trigger in LF is 'Waiting For Trigger',
        #     then value when done (waiting) is 1 (one);
        # Otherwise, if output signal is 'Reading Out', then value when
        #     done (read) is 0 (zero).
        self._done = (value == 0)
    
    # PyLoN CCD constructor
    #     readoutMode = 0 (FullFrame)
    #     readoutMode = 1 (Kinetics)
    def __init__(self, pvName, pvNameIN, pvNameOUT, mnemonic, accumulations=1, readoutMode=0):
        # IN   DXAS:DIO:bi8         # 1.0   (read TTL OUT from CCD)
        # OUT  DXAS:DIO:bo17        # 6.1   (write Trigger IN to CCD start acquisition)
        self.pvTriggerAcquire = PV(pvNameOUT)
        self.pvMonitor = PV(pvNameIN, callback=self.onAcquireChange)
        # Number of accumulations per frame
        self.accumulations = accumulations
        # Then call parent initializer
        # Operation Mode of readout control
        self.readoutMode = readoutMode
        PylonCCD.__init__(self, pvName, mnemonic)
        # Configurable timeout to control triggers
        self.triggerTimeout = None

    def isDone(self):
        # If 'Output Signal' of Trigger in LF is 'Waiting For Trigger',
        #     then value when done (waiting) is 1 (one);
        # Otherwise, if output signal is 'Reading Out', then value when
        #     done (read) is 0 (zero).
        return (self.pvMonitor.get() == 0)

    def acquire(self, waitComplete=False):
        # Necessary wait if a pause command was sent to the system
        # This is being used by furnace experiments (temperature scan)
        while (self.isPaused()):
            sleep(0.2)

        #print(self.readoutMode)
        if (self.readoutMode == 0):
            # FullFrame
            repeatTimes = self.accumulations
        elif (self.readoutMode == 1):
            # Kinetics
            repeatTimes = 1
        
        for currentAccumulation in range(repeatTimes):
            # Set the attribute of done acquisition to False
            self._done = False

            ####################################################################
            # The digital output port which trigger the CCD should be pulsed.
            # Minor pulse width in tests were 10 ms.
            ####################################################################
            self.pvTriggerAcquire.put(1)
            sleep(0.01)                         # Just to guarantee a 10ms trigger...
            self.pvTriggerAcquire.put(0)

            if ((waitComplete)):
                self.wait()

    def startLightFieldAcquisition(self):
        self.pvAcquire.put(1)

    def waitFinishAcquiring(self):
        accumulation_wait = 0
        while(not self._done and accumulation_wait < self.getTriggerTimeout()):
            accumulation_wait += WAIT_ACQUIRING
            sleep(WAIT_ACQUIRING)

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

    def setTriggerTimeout(self, timeout):
        self.triggerTimeout = timeout

    def getTriggerTimeout(self):
        if (self.triggerTimeout is None):
            return TIMEOUT_SECONDS
        else:
            return self.triggerTimeout

