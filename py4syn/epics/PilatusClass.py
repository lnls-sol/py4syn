"""Dectris Pilatus X-ray camera class

Python class for Pilatus X-ray cameras using EPICS area detector
IOC.

:platform: Unix
:synopsis: Python class for Pilatus X-ray cameras

.. moduleauthor:: Henrique Dante de Almeida <henrique.almeida@lnls.br>

"""
from threading import Event

from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
from py4syn.utils.timer import Timer
from epics import PV, ca, caput

# Pilatus ReadOut time
READOUTTIME = 1

class Pilatus(StandardDevice, ICountable):
    """
    Class to control Pilatus cameras via EPICS.

    Examples
    --------
    >>> from shutil import move
    >>> from py4syn.epics.PilatusClass import Pilatus
    >>> from py4syn.epics.ShutterClass import SimpleShutter
    >>> 
    >>> def getImage(pv, fileName='image.tif', shutter=''):
    ...     shutter = SimpleShutter(shutter, shutter)
    ...     camera = Pilatus('pilatus', pv)
    ...     camera.setImageName('/remote/' + fileName)
    ...     camera.setCountTime(10)
    ...     camera.startCount()
    ...     shutter.open()
    ...     camera.wait()
    ...     camera.stopCount()
    ...     shutter.close()
    ...     move('/remote/' + fileName, '/home/user/' + fileName)
    ...     camera.close()
    ...
    """
    RESPONSE_TIMEOUT = 15

    def __init__(self, mnemonic, pv):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`

        Parameters
        ----------
        mnemonic : `string`
            A mnemonic for the camera
        pv : `string`
            Base name of the EPICS process variable
        """
        super().__init__(mnemonic)
        self.acquireChanged = Event()
        self.acquiring = False
        self.pvAcquire = PV(pv + ':Acquire')
        self.pvAcquire.add_callback(self.statusChange)

        caput(pv + ':FileTemplate', '%s%s\0')
        caput(pv + ':FilePath', '\0')
        
        self.pvAcquireTime = PV(pv + ':AcquireTime')
        self.pvAcquirePeriod = PV(pv + ':AcquirePeriod')
        self.pvFilePath = PV(pv + ':FilePath')
        self.pvFileName = PV(pv + ':FileName')
        self.pvFileTemplate = PV(pv + ':FileTemplate')
        self.pvThreshold = PV(pv + ':ThresholdEnergy')
        self.pvBeamX = PV(pv + ':BeamX')
        self.pvBeamY = PV(pv + ':BeamY')
        self.pvWavelength = PV(pv + ':Wavelength')
        self.pvStartAngle = PV(pv + ':StartAngle')
        self.pvAngleIncr = PV(pv + ':AngleIncr')
        self.pvDetDist = PV(pv + ':DetDist')
        self.pvNumImages = PV(pv + ':NumImages')
        self.pvDelayTime = PV(pv + ':DelayTime')
        self.pvTriggerMode = PV(pv + ':TriggerMode')
        self.pvDet2Theta = PV(pv + ':Det2theta')
        self.pvCamserverConnectStatus = PV(pv +':CamserverAsyn.CNCT')
        self.pvLastFileName = PV(pv+ ":FullFileName_RBV")

        self.timer = Timer(self.RESPONSE_TIMEOUT)

    def setImageName(self, name):
        """
        Sets the output image file name. The image will be saved with this name
        after the acquisition.
        
        Parameters
        ----------
        name : `string`
            The full pathname of the image.
        """
        self.pvFileName.put(name + "\0", wait=True)

    def setFilePath(self, path):
        """
        Sets the output image file path. The image will be saved in this location
        after the acquisition.
        
        Parameters
        ----------
        name : `string`
            The path of location to save the image.
        """
        self.pvFilePath.put(path + "\0", wait=True)

    def getFilePath(self):
        """
        Returns the path where image file should be saved.
        """
        return self.pvFilePath.get(as_string=True)

    def setFileName(self, name):
        """
        Sets the output image file name. The image will be saved with this name
        after the acquisition.
        
        Parameters
        ----------
        name : `string`
            The name of image to save.
        """
        self.pvFileName.put(name + "\0", wait=True)

    def getFileName(self):
        """
        Returns the name of the image to be saved.
        """
        return self.pvFileName.get(as_string=True)

    def setFileTemplate(self, template="%s%s"):
        self.pvFileTemplate.put(template + "\0", wait=True)

    def getFileTemplate(self):
        return self.pvFileTemplate.get(as_string=True)

    def statusChange(self, value, **kw):
        """
        Helper callback used to wait for the end of the acquisition.
        """
        self.acquiring = value
        self.acquireChanged.set()

    def close(self):
        """
        Stops an ongoing acquisition, if any, and puts the EPICS IOC in idle state.
        """
        self.pvAcquire.put(0, wait=True)

    def getValue(self, **kwargs):
        """
        This is a dummy method that always returns zero, which is part of the
        :class:`py4syn.epics.ICountable` interface. Pilatus does not return
        a value while scanning. Instead, it stores a file with the resulting image.
        """
        return 0

    def setCountTime(self, t):
        """
        Sets the image acquisition time.

        Parameters
        ----------
        t : `float`
            Acquisition time
        """
        self.pvAcquireTime.put(t, wait=True)
        self.pvAcquirePeriod.put(t + READOUTTIME, wait=True)
        self.timer = Timer(t + self.RESPONSE_TIMEOUT)

    def getAcquireTime(self):
        return self.pvAcquireTime.get()

    def setAcquirePeriod(self, period):
        """
        Sets the acquire period.

        Parameters
        ----------
        t : `float`
            Acquisition period
        """
        self.pvAcquirePeriod.put(period, wait=True)

    def getAcquirePeriod(self):
        return self.pvAcquirePeriod.get()

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
        if self.acquiring:
            raise RuntimeError('Already counting')

        self.acquiring = True
        self.pvAcquire.put(1)
        self.timer.mark()

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
        return self.acquiring

    def wait(self):
        """
        Blocks until the acquisition completes.
        """
        if not self.acquiring:
            return

        self.acquireChanged.clear()
        while self.acquiring and self.timer.check():
            self.acquireChanged.wait(5)
            self.acquireChanged.clear()

        if self.timer.expired():
            raise RuntimeError('Camera is not answering')

    def setThreshold(self, threshold, wait=True):
        self.pvThreshold.put(threshold, wait=wait)

    def getThreshold(self):
        return self.pvThreshold.get()

    def setBeamPosition(self, position=[0,0]):
        self.pvBeamX.put(position[0], wait=True)
        self.pvBeamY.put(position[1], wait=True)

    def getBeamPosition(self):
        return [self.pvBeamX.get(), self.pvBeamY.get()]

    def setWavelength(self, wavelength):
        self.pvWavelength.put(wavelength, wait=True)

    def getWavelength(self):
        return self.pvWavelength.get()

    def setStartAngle(self, start):
        self.pvStartAngle.put(start, wait=True)

    def getStartAngle(self):
        return self.pvStartAngle.get()

    def setAngleIncr(self, incr):
        self.pvAngleIncr.put(incr, wait=True)

    def getAngleIncr(self):
        return self.pvAngleIncr.get()

    def setDetDist(self, distance):
        self.pvDetDist.put(distance, wait=True)

    def getDetDist(self):
        return self.pvDetDist.get()

    def setNumImages(self, num):
        self.pvNumImages.put(num, wait=True)

    def getNumImages(self):
        return self.pvNumImages.get()

    def setDelayTime(self, delay):
        self.pvDelayTime.put(delay, wait=True)

    def getDelayTime(self):
        return self.pvDelayTime.get()

    def setTriggerMode(self, mode):
        """
        Trigger mode

        Parameters
        ----------
        mode  : `int`
            0 : Internal
            1 : Ext. Enable
            2 : Ext. Trigger
            3 : Mult. Trigger
            4 : Alignment
        """
        self.pvTriggerMode.put(mode, wait=True)

    def getTriggerMode(self):
        return self.pvTriggerMode.get()

    def setDet2Theta(self, det2theta):
        self.pvDet2Theta.put(det2theta, wait=True)

    def getDet2Theta(self):
        return self.pvDet2Theta.get()

    def isCamserverConnected(self):
        return (self.pvCamserverConnectStatus.get() == 1)
