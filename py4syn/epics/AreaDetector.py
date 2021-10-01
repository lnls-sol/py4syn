"""AreaDetector class

Python class for AreaDetector devices using EPICS area detector IOC.

:platform: Unix
:synopsis: Python class for AreaDetector devices

.. moduleauthor::   Luciano Carneiro Guedes <luciano.guedes@lnls.br>
                    Carlos Doro Neto <carlos.doro@lnls.br>
"""

from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
from epics.devices.ad_base import AD_Camera
from epics.devices.ad_fileplugin import AD_FilePlugin


class AreaDetectorClass(StandardDevice, ICountable):
    """
    Class to control AreaDetector via EPICS.
    Examples
    --------
    """

    def __init__(self, mnemonic, pv, device, fileplugin,
                 write=None, autowrite=None, path=None, trigger=None):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`
        Parameters
        ----------
        mnemonic : `string`
            A mnemonic for the detector
        pv : `string`
            Base name of the EPICS process variable
        device : `string`
            Area Detector camera suffix
        fileplugin : `string`
            NDPluginFile suffix
        write : `string`
            Ignored, kept for compatibility purposes
        autowrite : `string`
            Ignored, kept for compatibility purposes
        path : `string`
            Ignored, kept for compatibility purposes
        trigger : `string`
            Ignored, kept for compatibility purposes
        """

        super().__init__(mnemonic)

        self.detector_name = pv + ":" + device + ":"
        self.write_name = pv + ":" + fileplugin + ":"

        self._detector = AD_Camera(self.detector_name)
        self._file = AD_FilePlugin(self.write_name)

        self._detector.add_pv(self.detector_name + "Acquire_RBV",
                              attr="Acquire_RBV")
        self._file.add_pv(self.write_name+"NumExtraDims", attr="NumExtraDims")
        self._file.add_pv(self.write_name+"ExtraDimSizeX", attr="ExtraDimSizeX")
        self._file.add_pv(self.write_name+"ExtraDimSizeY", attr="ExtraDimSizeY")

        for i in range(3, 10):
            self._file.add_pv(self.write_name+"ExtraDimSize"+str(i),
                              attr="ExtraDimSize"+str(i))

        self._detector.ArrayCallbacks = 1
        self.setEnableCallback(1)

        if self._detector.TriggerMode_RBV != "Internal":
            self.setImageMode(2)

    def getNframes(self):
        """
        Gets the number of frames to acquire.

        Returns
        ----------
        nframes : `int`
            The name of the image.
        """
        return self._file.NumCapture_RBV

    def setNframes(self, val):
        """
        Sets the number of frames to acquire.

        Parameters
        ----------
        nframes : `int`
            The name of the image.
        """
        self._detector.NumImages = val
        self._file.NumCapture = val

    def getFileName(self):
        """
        Returns the output image file name.

        Returns
        ----------
        name : `string`
            The name of the image.
        """
        return self._file.FileName_RBV

    def setFileName(self, val):
        """
        Sets the output image file name. The image will be saved with this name
        after the acquisition.

        Parameters
        ----------
        name : `string`
            The name of the image.
        """
        self._file.FileName = val

    def getFilePath(self):
        """
        Gets the output image file path. The image will be saved in this location
        after the acquisition.

        Parameters
        ----------
        name : `string`
            The path of location to save the image.
        """
        return self._file.FilePath_RBV

    def setFilePath(self, val):
        """
        Sets the output image file path. The image will be saved in this location
        after the acquisition.

        Parameters
        ----------
        name : `string`
            The path of location to save the image.
        """
        self._file.FilePath = val

    def getImageMode(self):
        """
        Gets the image mode.

        Returns
        ----------
        _imagemode : `int`
            The value of one of these options.
            0 - Single
            1 - Multiple
            2 - Continuous
        """
        return self._detector.ImageMode_RBV

    def setImageMode(self, val):
        """
        Sets the image mode.

        Paramters
        ----------
        _imagemode : `int`
            The value of one of these options.
                0 - Single
                1 - Multiple
                2 - Continuous
        """
        self._detector.ImageMode = val

    def getTriggerMode(self):
        """
        Gets the trigger mode.

        Returns
        ----------
        _triggermode : `int`
            The value of one of these options:
                0 - Internal
                1 - External
        """
        return self._detector.TriggerMode_RBV

    def setTriggerMode(self, val):
        """
        Sets the trigger mode.

        Returns
        ----------
        _triggermode : `int`
            The value of one of these options:
                0 - Internal
                1 - External
        """
        self._detector.TriggerMode = val

    def getEnableCallback(self):
        """
        Gets if the Pluging to Write Files is enabled.

        Returns
        ----------
        _enablecallbak : `int`
            The value of one of these options:
                0 - ON
                1 - OFF
        """
        return self._file.EnableCallbacks_RBV

    def setEnableCallback(self, val):
        """
        Enables the Pluging to Write Files.

        Parameters
        ----------
        _enablecallbak : `int`
            The value of one of these options:
                0 - ON
                1 - OFF
        """
        self._file.EnableCallbacks = val

    def getAutoSave(self):
        return self._file.AutoSave_RBV

    def setAutoSave(self, val):
        self._file.AutoSave = val

    def getNextraDim(self):  # TODO
        return self._file.NumExtraDims

    def setNextraDim(self, val):  # TODO
        self._file.NumExtraDims = val

    def getDimX(self):  # TODO
        return self._file.ExtraDimSizeX

    def setDimX(self, val):  # TODO
        self._file.ExtraDimSizeX = val

    def getDimY(self):  # TODO
        return self._file.ExtraDimSizeY

    def setDimY(self, val):  # TODO
        self._file.ExtraDimSizeY = val

    def getWriteMode(self):
        return self._file.FileWriteMode_RBV

    def setWriteMode(self, val):
        self._file.FileWriteMode = val

    def getOutputFormat(self):
        return self._file.FileTemplate_RBV

    def setOutputFormat(self, val):
        self._file.FileTemplate = val

    def setRepeatNumber(self, val):
        self._file.FileNumber = val

    def getRepeatNumber(self):
        return self._file.FileNumber_RBV

    def startCapture(self):
        self._file.Capture = 1

    def stopCapture(self):
        self._file.Capture = 0

    def setParams(self, dictionary):  # TODO
        if self.write and self.autowrite:
            self.dimensions = []

            nframes = 1
            for ipoints_motor in dictionary["points"]:
                # Gambiarra pq ele conta o ultimo ponto
                self.dimensions.append(len(set(ipoints_motor)) - 1)
            self.setNextraDim(len(self.dimensions))

            for i in range(len(self.dimensions), 10):
                self.dimensions.append(1)

            self.setDimX(self.dimensions[0])
            self.setDimY(self.dimensions[1])

            for i in range(3, 10):
                self._file.put("ExtraDimSize"+str(i), self.dimensions[i-1])

            for i in self.dimensions:
                nframes = nframes * i
            self.setNframes(nframes)

            self.setRepeatNumber(dictionary["repetition"])

    def setWriteParams(self):
        pass

    def close(self, *args, **kwargs):  # TODO
        """
        Stops acquiring. This method simply calls :meth:`stopCount`.

        See: :meth:`stopCount`
        """
        return self.stopCount(*args, **kwargs)

    def getIntensity(self, *args, **kwargs):  # TODO
        return self.getValue(*args, **kwargs)

    def getAcquireTime(self):
        return self._detector.AcquireTime_RBV, self._detector.AcquirePeriod_RBV

    # ICountable methods overriding

    def getValue(self, **kwargs):
        if self.getWriteMode() == "Single":
            self._file.WriteFile = 1
        elif self.getWriteMode() == "Capture":
            self._file.WriteFile = 1
            self.stopCapture()
        elif self.getWriteMode() == "Stream":
            self.stopCapture()
        else:
            raise RuntimeError("Unrecognized write mode")

    def setCountTime(self, t):
        """
        Sets the image acquisition time.
        Parameters
        ----------
        t : `float`
            Acquisition time
        """
        self._detector.AcquireTime = t
        self._detector.AcquirePeriod = t

    def setPresetValue(self, channel, val):
        """
        Dummy method to set initial counter value.
        """
        pass

    def startCount(self):
        """
        Starts acquiring
        """
        if self.isCounting() or self._file.Capture_RBV:
            raise RuntimeError("Already counting")
        self.startCapture()
        self._detector.Acquire = 1

    def stopCount(self):
        """
        Stops an ongoing acquisition, if any, and puts the EPICS IOC in idle state.
        """
        self._detector.Acquire = 0
        self.getValue()

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
        return self._detector.Acquire_RBV

    def wait(self):
        """
        Blocks until the acquisition completes.
        """
        while self.isCounting():
            pass
