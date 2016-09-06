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
        self.pvFilePath = PV(pv + ':FileName')
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
        self.pvFilePath.put(name + "\0", wait=True)

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
        self.timer = Timer(t + self.RESPONSE_TIMEOUT)

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
