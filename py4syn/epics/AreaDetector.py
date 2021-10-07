"""AreaDetector class

Python class for AreaDetector devices using EPICS area detector IOC.

:platform: Unix
:synopsis: Python class for AreaDetector devices

.. moduleauthor:: Luciano Carneiro Guedes <luciano.guedes@lnls.br>
                  Carlos Doro Neto <carlos.doro@lnls.br>
"""

from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
from epics.devices.ad_base import AD_Camera
from epics.devices.ad_fileplugin import AD_FilePlugin


class AreaDetectorClass(StandardDevice, ICountable):

    def __init__(self, mnemonic, pv, device, fileplugin,
                 write, autowrite, path, trigger):
        """Class to control Area Detector (AD) via EPICS

        Parameters
        ----------
        mnemonic : `string`
            A mnemonic for the detector
        pv : `string`
            Base name (prefix) of the EPICS process variables
        device : `string`
            AD camera suffix
        fileplugin : `string`
            NDPluginFile suffix
        write : `string`
            If false does not write any data to disk
        autowrite : `string`
            Indicates whether or not the IOC itself will write the data file(s)
            Must be true for this class
        path : `string`
            Ignored, kept for compatibility reasons
        trigger : `string`
            Ignored, kept for compatibility reasons
        """

        assert autowrite, "autowrite must be True for AD class"

        super().__init__(mnemonic)

        self.write = write

        detector_name = pv + ":" + device + ":"
        write_name = pv + ":" + fileplugin + ":"

        self._detector = AD_Camera(detector_name)
        self._detector.add_pv(detector_name+"Acquire_RBV", attr="Acquire_RBV")
        self._detector.add_pv(detector_name+"NumExposures", attr="NumExposures")
        self._detector.add_pv(detector_name+"NumExposures_RBV", attr="NumExposures_RBV")

        self._file = AD_FilePlugin(write_name)

        # Extra dimensions are available only in NDFileHDF5 plugin.
        # For other file plugins (tiff, jpeg, etc) these attributes will
        # return None without raising errors.
        self._file.add_pv(write_name+"NumExtraDims", attr="NumExtraDims")
        self._file.add_pv(write_name+"NumExtraDims_RBV",
                          attr="NumExtraDims_RBV")

        for i in ["X", "Y", "3",  "4", "5", "6", "7", "8", "9"]:
            suffix = "ExtraDimSize" + i
            self._file.add_pv(write_name+suffix, attr=suffix)
            self._file.add_pv(write_name+suffix+"_RBV", attr=suffix+"_RBV")

        self._detector.ensure_value("ArrayCallbacks", 1)

    def getNframes(self):
        """Returns the number of frames to acquire.

        Returns
        -------
        `int`
        """
        return int(self._file.NumCapture_RBV)

    def setNframes(self, val):
        """Sets the number of frames to acquire.

        Parameters
        ----------
        val : `int`
        """
        self._file.ensure_value("NumCapture", val)

    def getFileName(self):
        """Returns the output image file name.

        Returns
        -------
        `string`
        """
        return self._file.getName()

    def setFileName(self, val):
        """Sets the output image file name.

        Parameters
        ----------
        val : `string`
        """
        self._file.ensure_value("FileName", val)

    def getFilePath(self):
        """Returns the output image file path.

        Returns
        -------
        `string`
        """
        return self._file.getPath()

    def setFilePath(self, val):
        """Sets the output image file path.

        Parameters
        ----------
        val : `string`
        """
        self._file.ensure_value("FilePath", val)

    def getImageMode(self):
        """Gets the image mode.

        Returns
        -------
        `int`
            0 - Single
            1 - Multiple
            2 - Continuous
        """
        return int(self._detector.ImageMode_RBV)

    def setImageMode(self, val):
        """
        Sets the image mode.

        Parameters
        ----------
        val : `int`
            0 - Single
            1 - Multiple
            2 - Continuous
        """
        self._detector.ensure_value("ImageMode", val)

    def getTriggerMode(self):
        """Returns the trigger mode.

        Returns
        -------
        val : `int`
            0 - Internal
            1 - External
        """
        return int(self._detector.TriggerMode_RBV)

    def setTriggerMode(self, val):
        """
        Sets the trigger mode.

        Parameters
        ----------
        val : `int`
            0 - Internal
            1 - External
        """
        self._detector.ensure_value("TriggerMode", val)

    def getEnableCallback(self):
        """Returns true if the NDPluginFile is enabled."""
        return bool(self._file.EnableCallbacks_RBV)

    def setEnableCallback(self, val):
        """Enables/disables the NDPluginFile.

        Parameters
        ----------
        val : `bool`
            0 - OFF
            1 - ON
        """
        self._file.EnableCallbacks = val

    def getAutoSave(self):
        return bool(self._file.AutoSave_RBV)

    def setAutoSave(self, val):
        self._file.ensure_value("AutoSave", val)

    def getNextraDim(self):
        return int(self._file.NumExtraDims)

    def setNextraDim(self, val):
        self._file.ensure_value("NumExtraDims", val)

    def getDimX(self):
        return int(self._file.ExtraDimSizeX)

    def setDimX(self, val):
        self._file.ensure_value("ExtraDimSizeX", val)

    def getDimY(self):
        return int(self._file.ExtraDimSizeY)

    def setDimY(self, val):
        self._file.ensure_value("ExtraDimSizeY", val)

    def getWriteMode(self):
        return int(self._file.FileWriteMode_RBV)

    def setWriteMode(self, val):
        self._file.ensure_value("FileWriteMode", val)

    def getOutputFormat(self):
        return self._file.getTemplate()

    def setOutputFormat(self, val):
        self._file.ensure_value("FileTemplate", val)

    def getRepeatNumber(self):
        return int(self._file.FileNumber_RBV)

    def setRepeatNumber(self, val):
        self._file.ensure_value("FileNumber", val)

    def startCapture(self):
        self._file.ensure_value("Capture", 1)

    def stopCapture(self):
        self._file.ensure_value("Capture", 0)

    def setParams(self, dictionary):
        """Sets up the AD device to a state usable by scan-utils."""
        assert not self.isCounting(), "Already counting"
        assert not self._file.Capture_RBV, "Already counting"

        if self.write:

            self.setCountTime(dictionary["time"][0][0])
            self._detector.ensure_value("NumImages", 1)
            self._detector.ensure_value("NumExposures", 1)
            self.setImageMode(1)

            self.setEnableCallback(1)
            self.setWriteMode(2)
            self._file.ensure_value("AutoIncrement", 0)
            self.setRepeatNumber(dictionary["repetition"])

            # Calculate the size of each dimension.
            dim_sizes = []
            for points in dictionary["points"]:
                # Use set to remove duplicates.
                dim_sizes.append(len(set(points)))

            self.setNextraDim(len(dim_sizes))
            dim_names = ["X", "Y", "3",  "4", "5", "6", "7", "8", "9"]
            for name, size in zip(dim_names, dim_sizes):
                attr = "ExtraDimSize" + name
                self._file.ensure_value(attr, size)

            # Use dim_sizes to calculate the number of frames to acquire.
            nframes = 1
            for i in dim_sizes:
                nframes = i * nframes
            self.setNframes(nframes)

        else:
            self.setEnableCallback(0)

    def getAcquireTime(self):
        return float(self._detector.AcquireTime_RBV), float(self._detector.AcquirePeriod_RBV)

    def setWriteParams(self, *args, **kwargs):
        """This method is deprecated and is kept for compatibility reasons."""
        pass

    def close(self):
        """Stops ongoing acquisition and puts the IOC in an idle state."""
        self.stopCount()
        self._file.ensure_value("WriteFile", 1)
        self.stopCapture()

    def getIntensity(self, *args, **kwargs):
        """This method is deprecated and is kept for compatibility reasons."""
        pass

    # ICountable methods overriding

    def getValue(self, **kwargs):
        """Returns number of acquired frames. Works as a heartbeat."""
        return int(self._file.NumCaptured_RBV)

    def setCountTime(self, t):
        """Sets the image acquisition time.

        Parameters
        ----------
        t : `float`
        """
        self._detector.ensure_value("AcquireTime", t)
        self._detector.ensure_value("AcquirePeriod", t)

    def setPresetValue(self, channel, val):
        """Not available on AD, does nothing."""
        pass

    def startCount(self):
        """Starts acquiring"""
        self._detector.ensure_value("Acquire", 1)

    def stopCount(self):
        """Stops ongoing acquisition and puts the IOC in an idle state."""
        self._detector.ensure_value("Acquire", 0)

    def canMonitor(self):
        """Returns false indicating that AD cannot be used as a monitor."""
        return False

    def canStopCount(self):
        """Returns true indicating that AD has a stop command."""
        return True

    def isCounting(self):
        """Returns true if the detector is acquiring."""
        return bool(self._detector.Acquire_RBV)

    def wait(self):
        """Blocks until the acquisition completes."""
        while self.isCounting():
            pass
