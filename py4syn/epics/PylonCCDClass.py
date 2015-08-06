"""PyLoN Charge-Coupled Devices (CCD) Class

Python Class for EPICS LabView RT Detector control of Princeton Instruments
PyLoN camera.

:platform: Unix
:synopsis: Python Class for EPICS LabView RT Detector control of Princeton
Instruments PyLoN camera.

.. moduleauthor:: Douglas Bezerra Beniz <douglas.beniz@lnls.br>
    .. note:: 05/02/2015 [douglas.beniz]  first version released
"""

from time import sleep
from enum import Enum
from epics import PV
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable

class ADFrameType_t(Enum):
    """
    Enumeration of frame type.
    """
    ADFrameNormal = 0               # Normal frame type.
    ADFrameBackground = 1           # Background frame type.
    ADFrameFlatField = 2            # Flat field (no sample) frame type.
    ADFrameDoubleCorrelation = 3    # Double correlation frame type, used to remove zingers. 

class ADImageMode_t(Enum):
    """
    Enumeration of image collection modes.
    """
    ADImageSingle = 0       # Collect a single image per Acquire command.
    ADImageMultiple = 1     # Collect ADNumImages images per Acquire command.
    ADImageContinuous = 2   # Collect images continuously until Acquire is set to 0. 

class ADImageModeLightField_t(Enum):
    """
    Enumeration of image collection modes for LightField.
    """
    Normal = 0      # This is the same as pressing the Acquire button in LightField. 
                    # It may collect more than 1 accumulation per image if numAccumulations>1,
                    # more than 1 exposure per image if NumExposures>1, more than 1 image per 
                    # acquisition if NumImages>1, and more than 1 aquisition if NumAcquisitions>1.
    Preview = 1     # This is the same as pressing the Preview button in LightField.
                    # It causes acquisition to proceed as quickly as possible. It does not save the data.
    Background = 2  # This will cause the driver to acquire a background image to be used when
                    # background subtraction is enabled.

class ADShutterMode_t(Enum):
    """
    Enumeration of shutter modes.
    """
    ADShutterModeNone = 0       # Don't use shutter.
    ADShutterModeEPICS = 1      # Shutter controlled by EPICS PVs.
    ADShutterModeDetector = 2   # Shutter controlled directly by detector. 

class ADShutterStatus_t(Enum):
    """
    Enumeration of shutter status.
    """
    ADShutterClosed = 0     # Shutter closed.
    ADShutterOpen = 1       # Shutter open. 

class ADStatus_t(Enum):
    """
    Enumeration of detector status.
    """
    ADStatusIdle = 0            # Detector is idle.
    ADStatusAcquire = 1         # Detector is acquiring.
    ADStatusReadout = 2         # Detector is reading out.
    ADStatusCorrect = 3         # Detector is correcting data.
    ADStatusSaving = 4          # Detector is saving data.
    ADStatusAborting = 5        # Detector is aborting an operation.
    ADStatusError = 6           # Detector has encountered an error.
    ADStatusWaiting = 7         # Detector is waiting for something, typically for the acquire period to elapse.
    ADStatusInitializing = 8    # Detector is initializing, typically at startup.
    ADStatusDisconnected = 9    # Detector is not connected.
    ADStatusAborted = 10        # Detector aquisition has been aborted. 

class ADTriggerMode_t(Enum):
    """
    Enumeration of trigger mode.
    """
    ADTriggerInternal = 0   # Internal trigger from detector.
    ADTriggerExternal = 1   # External trigger input. 

class PylonCCD(StandardDevice, ICountable):
    """
    Python class to help configuration and control of Charge-Coupled Devices
    (CCD) via Hyppie over EPICS.
    
    CCD is the most common mechanism for converting optical images to electrical
    signals. In fact, the term CCD is know by many people because of their use
    of video cameras and digital still cameras.
    """
    
    # PyLoN CCD callback function for acquire status
    def onAcquireChange(self, value, **kw):
        #print datetime.datetime.now(), " - Acquisition Done = ", (value == 0)
        self._done = (value == 0)

    # PyLoN CCD constructor 
    def __init__(self, pvName, mnemonic):
        StandardDevice.__init__(self, mnemonic)
        self.pvAcquire = PV(pvName + ":Acquire", callback=self.onAcquireChange)
        self.pvAcquire_RBV = PV(pvName + ":Acquire_RBV")
        self.pvAcquireTime = PV(pvName + ":AcquireTime")
        self.pvAcquireTime_RBV = PV(pvName + ":AcquireTime_RBV")
        self.pvNumImages = PV(pvName + ":NumImages")
        self.pvNumImages_RBV = PV(pvName + ":NumImages_RBV")
        self.pvNumImagesCounter_RBV = PV(pvName + ":NumImagesCounter_RBV")
        self.pvNumExposures = PV(pvName + ":NumExposures") 
        self.pvNumExposures_RBV = PV(pvName + ":NumExposures_RBV")
        self.pvNumExposuresCounter_RBV = PV(pvName + ":NumExposuresCounter_RBV")
        self.pvImageMode = PV(pvName + ":ImageMode")
        self.pvImageMode_RBV = PV(pvName + ":ImageMode_RBV")
        self.pvTriggerMode = PV(pvName + ":TriggerMode")
        self.pvTriggerMode_RBV = PV(pvName + ":TriggerMode_RBV")
        self.pvFrameType = PV(pvName + ":FrameType")
        self.pvFrameType_RBV = PV(pvName + ":FrameType_RBV")
        self.pvGain = PV(pvName + ":LFGain")
        self.pvGain_RBV = PV(pvName + ":LFGain_RBV")
        self.pvNumAccumulations = PV(pvName + ":NumAccumulations")
        self.pvNumAccumulations_RBV = PV(pvName + ":NumAccumulations_RBV")
        self.pvNumAcquisitions = PV(pvName + ":NumAcquisitions")
        self.pvNumAcquisitions_RBV = PV(pvName + ":NumAcquisitions_RBV")
        self.pvNumAcquisitionsCounter_RBV = PV(pvName + ":NumAcquisitionsCounter_RBV")
        self.pvBackgroundEnable = PV(pvName + ":LFBackgroundEnable")
        self.pvBackgroundEnable_RBV = PV(pvName + ":LFBackgroundEnable_RBV")
        self.pvBackgroundPath = PV(pvName + ":LFBackgroundPath")
        self.pvBackgroundPath_RBV = PV(pvName + ":LFBackgroundPath_RBV")
        self.pvBackgroundFile = PV(pvName + ":LFBackgroundFile")
        self.pvBackgroundFile_RBV = PV(pvName + ":LFBackgroundFile_RBV")
        self.pvFilePath = PV(pvName + ":FilePath")
        self.pvFilePath_RBV = PV(pvName + ":LFFilePath_RBV")
        self.pvFileName = PV(pvName + ":FileName") 
        self.pvFileName_RBV = PV(pvName + ":LFFileName_RBV")
        self.pvFileNumber = PV(pvName + ":FileNumber")
        self.pvFileNumber_RBV = PV(pvName + ":FileNumber_RBV")
        self.pvArrayCounter = PV(pvName + ":ArrayCounter")
        self.pvArrayCounter_RBV = PV(pvName + ":ArrayCounter_RBV")
        self.pvAutoIncrement = PV(pvName + ":AutoIncrement")
        self.pvAutoIncrement_RBV = PV(pvName + ":AutoIncrement_RBV")
        self.pvImageArrayData = PV(pvName + ":image1:ArrayData")
        # Current state
        self._done = self.isDone()
        self.time = self.pvAcquireTime_RBV.get()
        self.countTime = 1
        self.paused = False

    def isDone(self):
        return (self.pvAcquire_RBV.get() == 0)

    def acquire(self, waitComplete=False):
        self.pvAcquire.put(1)
        self._done = False
        if(waitComplete):
            self.wait()

    def waitFinishAcquiring(self):
        while(not self._done):
            sleep(0.001)

    def setPause(self, paused):
        self.paused = paused
    
    def isPaused(self):
        return self.paused
    
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
        self.setAcquireTime(t)

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

    def readout(self):
        # Because we process the CCD images in a diferent way, simply return ZERO for while...
        return 1

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
        return self.readout()

    def getNumImages(self):
        """
        Obtain the number of images to acquire into a single 3-D data set. 
        """
        return self.pvNumImages_RBV.get()

    def getNumImagesCounter(self):
        """
        Obtain the counter for the number of images to acquire into a single 3-D data set. 
        """
        return self.pvNumImagesCounter_RBV.get()

    def setNumImages(self, numImages):
        """
        Set the number of images to acquire into a single 3-D data set. 
        """
        self.pvNumImages.put(numImages)

    def getNumExposures(self):
        """
        Obtain number of exposures that LightField will sum into a single image. 
        """
        return self.pvNumExposures_RBV.get()

    def getNumExposuresCounter(self):
        """
        Obtain the counter for the number of exposures that LightField will sum into a single image. 
        """
        return self.pvNumExposuresCounter_RBV.get()

    def setNumExposures(self, numExposures):
        """
        Set the number of exposures that LightField will sum into a single image. 
        """
        self.pvNumExposures.put(numExposures)

    def getImageMode(self):
        """
        Obtain current ADImageMode parameter choice, which is one of the ADImageModeLightField_t
        enumeration options
        """
        return self.pvImageMode_RBV

    def setImageMode(self, imageModeLightField):
        """
        Set the mode for the image to be configured at LightField, which should be one of the
        ADImageModeLightField_t enumeration options. 
        """
        self.pvImageMode.put(imageModeLightField)

    def getTriggerMode(self):
        """
        Obtain current ADTriggerMode parameter choice, which is one of the ADTriggerMode_t
        enumeration options
        """
        return self.pvTriggerMode_RBV

    def setTriggerMode(self, triggerMode):
        """
        Set the trigger for the image to be configured at LightField, which should be one of the
        ADTriggerMode_t enumeration options.  
        """
        self.pvTriggerMode.put(triggerMode)

    def getFrameType(self):
        """
        Obtain current ADFrameType parameter choice.
        """
        return self.pvFrameType_RBV

    def setFrameType(self, frameType):
        """
        Set the frame type for the image to be configured at LightField.
        """
        self.pvFrameType.put(frameType)

    def getGain(self):
        """
        Obtain the detector's gain. These parameters, ($P)($R)LFGain and ($P)($R)LFGain_RBV, 
        are used instead of the base class ADGain and ADGain_RBV parameters so that it can be 
        displayed as a menu as LightField does.  
        """
        return self.pvGain_RBV

    def setGain(self, gain):
        """
        The precision of the $(P)$(R)Gain record is changed to 0 because the gain in LightField
        is an integer. Allowed values are detector dependent, but 1 and 2 are typically supported.
        """
        self.pvGain.put(gain)

    def getNumAccumulations(self):
        """
        Obtain the number of on-chip accumulations to perform per image.
        """
        return self.pvNumAccumulations_RBV

    def setNumAccumulations(self, accumulations):
        """
        Set the number of on-chip accumulations to perform per image.
        """
        self.pvNumAccumulations.put(accumulations)

    def getNumAcquisitions(self):
        """
        Obtain the number of acquisitions to perform when acquisition is started. This controls 
        the number of iterations in the outermost acquisition loop explained above.
        NOTE: This is not yet implemented, it is planned for a future release.
        """
        return self.pvNumAcquisitions_RBV

    def getNumAcquisitionsCounter(self):
        """
        The number of acquisitions performed so far.
        """
        return self.pvNumAcquisitionsCounter_RBV

    def setNumAcquisitions(self, acquisitions):
        """
        Set the number of acquisitions to perform when acquisition is started. This controls 
        the number of iterations in the outermost acquisition loop explained above.
        NOTE: This is not yet implemented, it is planned for a future release.
        """
        self.pvNumAcquisitions.put(acquisitions)

    def getBackgroundEnable(self):
        """
        Obtain whether background correction is enabled. 
        """
        return self.pvBackgroundEnable_RBV

    def setBackgroundEnable(self, bgCorrection):
        """
        Set background correction.
        """
        self.pvBackgroundEnable.put(bgCorrection)

    def getBackgroundPath(self):
        """
        Obtain the path where background data should be.
        """
        bgPath = self.pvBackgroundPath_RBV.get(as_string=True)
        return bgPath

    def setBackgroundPath(self, bgPath):
        """
        Set the path where background data should be.
        """
        self.pvBackgroundPath.put(bgPath + "\0")

    def getBackgroundFile(self):
        """
        Obtain the name of background file to be used.
        """
        bgFile = self.pvBackgroundFile_RBV.get(as_string=True)
        return bgFile

    def setBackgroundFile(self, bgFile):
        """
        Set the name of background file to be used.
        """
        self.pvBackgroundFile.put(bgFile + "\0")

    def getAcquireTime(self):
        """
        Obtain acquisition time per image.
        """
        return self.pvAcquireTime_RBV.get()
    
    def setAcquireTime(self, acquireTime):
        """
        Set the acquisition time per image.
        """
        self.pvAcquireTime.put(acquireTime)

    def getFileName(self):
        """
        Obtain the actual file name for saving data. 
        """
        name = self.pvFileName_RBV.get(as_string=True)
        return name

    def setFileName(self, fileName):
        """
        Set the file name for saving experiment data.
        """
        self.pvFileName.put(fileName + "\0")

    def getFilePath(self):
        """
        Obtain the actual file path where to save data.
        """
        path = self.pvFilePath_RBV.get(as_string=True)
        return path

    def setFilePath(self, filePath):
        """
        Set the file path where to save experiment data.
        """
        self.pvFilePath.put(filePath + "\0")

    def getFileNumber(self):
        """
        Obtain current number to be appended at the file name.
        """
        return self.pvFileNumber_RBV.get()

    def setFileNumber(self, fileNumber):
        """
        Set a number to be appended at next scan to the file name.
        """
        self.pvFileNumber.put(fileNumber)

    def getAutoIncrement(self):
        """
        Obtain wheter auto-increment is enabled or not.
        """
        return self.pvAutoIncrement_RBV.get()

    def setAutoIncrement(self, autoIncrement):
        """
        Set if auto-increment should be enabled.
        0 - No;
        1 - Yes;
        """
        self.pvAutoIncrement.put(autoIncrement)
