from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
from epics import PV
import epics
from epics.devices.ad_fileplugin import AD_FilePlugin
from datetime import datetime

import numpy as np
from time import sleep, time

from py4syn.epics.AreaDetector import AreaDetectorClass
from epics.devices.ad_base import AD_Camera


READOUT_PIMEGA = 750e-6


class CountablePimega(StandardDevice, ICountable):
    """
    Class to control pimega via EPICS.
    Examples
    --------
    """

    def onImageChange(self, value, **kw):
        # print("onImageChange: ", value)
        if value:
            self._done = True

    def __init__(self, mnemonic, pv, device, fileplugin,
                 write, autowrite, path, trigger):
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
        self.autowrite = autowrite
        self.write = write
        self.path = path
        self.trigger = trigger
        self.write_name = pv+':'+fileplugin+':'
        self._done = 1
        self.pv = pv
        self.fileplugin = fileplugin
        self.file = ''
        pv = pv+':'+device
        self.pvAcquire = epics.PV(pv + ':Acquire')
        self.pvImageMode = epics.PV(pv + ':ImageMode')
        self.pvTriggerMode = epics.PV(pv + ':TriggerMode')
        self.pvSensorBias = epics.PV(pv + ':SensorBias_RBV')
        self.pvNumCaptured = epics.PV(
            pv + ':NumCaptured_RBV', callback=self.onImageChange)
        self.pvAcquireTime = epics.PV(pv + ':AcquireTime')
        self.pvAcquirePeriod = epics.PV(pv + ':AcquirePeriod')
        self.pvNumImages = PV(pv + ':NumExposures')

        # self.pvAcquirePeriod.put(0, wait=True)

        if self.write and self.autowrite:
            if self.fileplugin == 'HDF1':
                self.config_H5_plugin()

            elif self.fileplugin == 'cam1':
                self.file = AD_FilePlugin(self.write_name)

            self.setFilePath(self.path)
            self.setAutoSave(1)
            self.setOutputFormat("%s%s_%3.3d.hdf5")

        # force stop ioc and backend to guarantee correct initial state
        self.stopAcquire()
        self.stopCapture()

        if self.trigger == 'External' or self.trigger == 'ExternalFly':
            self.setTriggerMode(1)
        else:
            self.setTriggerMode(0)

    def config_H5_plugin(self):
        prefix = self.pv + ':HDF1:'
        self.file = AD_FilePlugin(prefix)
        self.file.add_pv(prefix+'Compression', attr='compression')
        self.file.add_pv(prefix+'SWMRMode', attr='swmrmode')

        self.file.compression = 3
        self.file.swmrmode = 1
        self.file.EnableCallbacks = 1
        self.file.FileWriteMode = 2

        self.configure_adplugins()

    def configure_adplugins(self):
        prefix_roi = ':ROI1:'
        self.pv_roi_enable = epics.PV(self.pv + prefix_roi + 'EnableCallbacks')
        self.pv_roi_size_x = epics.PV(self.pv + prefix_roi + 'SizeX')
        self.pv_roi_size_y = epics.PV(self.pv + prefix_roi + 'SizeY')

        self.pv_roi_enable.put(1)
        # set image size 1x1
        self.pv_roi_size_x.put(1)
        self.pv_roi_size_y.put(1)

        # configure HDF5 NDArrayPort to get image from ROI1 Plugin
        self.file.NDArrayPort = 'ROI1'

    def setAutoSave(self, val):
        self._autosave = val

    def getAutoSave(self):
        return self._autosave

    def getOutputFormat(self):
        return self._outputformat

    def setOutputFormat(self, val):
        self._outputformat = val

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
        return self._triggermode

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
        self._triggermode = val

    def close(self):
        """
        Stops an ongoing acquisition, if any, and puts the EPICS IOC in idle state.
        """
        self._done = 1

    def getIntensity(self):
        return self.pvSensorBias.get()

    def getValue(self, **kwargs):
        value = self.getIntensity()
        return value

    def setCountTime(self, t):
        """
        Sets the image acquisition time.
        Parameters
        ----------
        t : `float`
            Acquisition time
        """
        print("setCountTime")
        self.pvAcquireTime.put(t, wait=True)

    def setPresetValue(self, channel, val):
        """
        Dummy method to set initial counter value.
        """
        pass

    def getFileName(self):
        """
        Returns the output image file name.

        Returns
        ----------
        name : `string`
            The name of the image.
        """
        return self._filename

    def getFilePath(self):
        """
        Gets the output image file path. The image will be saved in this location
        after the acquisition.

        Parameters
        ----------
        name : `string`
            The path of location to save the image.
        """
        return self._filepath

    def setFilePath(self, val):
        """
        Sets the output image file path. The image will be saved in this location
        after the acquisition.

        Parameters
        ----------
        name : `string`
            The path of location to save the image.
        """
        self._filepath = val

    def setFileName(self, val):
        """
        Sets the output image file name. The image will be saved with this name
        after the acquisition.

        Parameters
        ----------
        name : `string`
            The name of the image.
        """
        self._filename = val

    def getNframes(self):
        """
        Gets the number of frames to acquire.

        Returns
        ----------
        nframes : `int`
            The name of the image.
        """
        return self._nframes

    def setNframes(self, val):
        """
        Sets the number of frames to acquire.

        Parameters
        ----------
        nframes : `int`
            The name of the image.
        """
        self._nframes = val

    def setRepeatNumber(self, val):
        self._repeat_number = val

    def getRepeatNumber(self):
        return self._repeat_number

    def setParams(self, dictionary):
        if self.write and self.autowrite:
            self.dimensions = []

            nframes = 1
            for ipoints_motor in dictionary['points']:
                self.dimensions.append(len(set(ipoints_motor)))

            for i in range(len(self.dimensions), 10):
                self.dimensions.append(1)
            nframes = len(dictionary['points'][0])

            # if saxs scan, remove extra points
            if dictionary['start'][0][0] == 0 and dictionary['end'][0][0] == 0:
                nframes -= 1

            self.setNframes(nframes)

    def setWriteParams(self):
        self.pvTriggerMode.put(self.getTriggerMode())
        if self.write and self.autowrite:
            # Set output path
            self.file.AutoSave = self.getAutoSave()
            self.file.setPath(self.getFilePath())
            self.file.setTemplate(self.getOutputFormat())
            self.file.setFileName(self.getFileName())
            self.file.setNumCapture(self.getNframes())
            self.file.FileNumber = self.getRepeatNumber()
        else:
            self.dumbnumb += 1
            self.setRepeatNumber(self.dumbnumb)

        if self.trigger == "ExternalFly":
            self.pvNumImages.put(self.getNframes())
            self.setImageMode(1)
            self.pvImageMode.put(self.getImageMode(), wait=True)

        else:
            self.pvNumImages.put(1, wait=True)
            # set imagemode to single
            self.setImageMode(0)
            self.pvImageMode.put(self.getImageMode(), wait=True)

        print("SetWriteParams")

    def startCapture(self):
        print("startCapture")
        if self.write and self.autowrite:
            # print("Time Start Capture Pimega: ", datetime.now())
            self.file.put('Capture', 1)
            if self.fileplugin == 'cam1':
                sleep(3)  # wait pimega configure the RDMA

    def stopCapture(self):
        if self.write and self.autowrite:
            self.file.Capture = 0

    def stopAcquire(self):
        if self.write and self.autowrite:
            self.pvAcquire.put(0)

    def startCount(self):
        """
        Starts acquiring
        """
        if not self._done:
            raise RuntimeError('Already counting')
        self.pvAcquire.put(1)
        if not self.trigger == "Internal":
            sleep(1)  # wait acquire cmd finished before configure trigger
        # print("Time Start Pimega: ", datetime.now())
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
        return self._imagemode

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
        self._imagemode = val

    def wait(self):
        """
        Blocks until the acquisition completes.
        """
        while not self._done:
            epics.poll(evt=1.e-5, iot=0.1)


class CountablePimegaParams(StandardDevice, ICountable):
    """
    Class to control pimega via EPICS.
    Examples
    --------
    """

    def onImageChange(self, value, **kw):
        if value:
            self._done = True

    def __init__(self, mnemonic, pv, device, fileplugin,
                 write, autowrite, path, trigger):
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
        self.autowrite = autowrite
        self.write = write
        self.path = path
        self.trigger = trigger
        self.write_name = pv+':'+fileplugin+':'
        self._done = 1
        self.pv = pv
        self.fileplugin = fileplugin
        self.file = ''
        pv = pv+':'+device
        self.pvAcquire = epics.PV(pv + ':Acquire')
        self.pvImageMode = epics.PV(pv + ':ImageMode')
        self.pvTriggerMode = epics.PV(pv + ':TriggerMode')
        self.pvSensorBias = epics.PV(pv + ':SensorBias_RBV')
        self.pvNumCaptured = epics.PV(
            pv + ':NumCaptured_RBV', callback=self.onImageChange)
        self.pvAcquireTime = epics.PV(pv + ':AcquireTime')
        self.pvAcquirePeriod = epics.PV(pv + ':AcquirePeriod')
        self.pvNumImages = PV(pv + ':NumExposures')

        if self.write and self.autowrite:
            self.config_H5_plugin()
            self.setFilePath(self.path)
            self.setAutoSave(1)
            self.setOutputFormat("%s%s_%3.3d.hdf5")

        if self.trigger == 'External' or self.trigger == 'ExternalFly':
            self.setTriggerMode(1)
        else:
            self.setTriggerMode(0)

    def config_H5_plugin(self):
        prefix = self.pv + ':HDF1:'
        self.file = AD_FilePlugin(prefix)
        self.file.add_pv(prefix+'Compression', attr='compression')
        self.file.add_pv(prefix+'SWMRMode', attr='swmrmode')

        self.file.compression = 3
        self.file.swmrmode = 1
        self.file.EnableCallbacks = 1
        self.file.FileWriteMode = 2

        self.configure_adplugins()

    def configure_adplugins(self):
        prefix_roi = ':ROI1:'
        self.pv_roi_enable = epics.PV(self.pv + prefix_roi + 'EnableCallbacks')
        self.pv_roi_size_x = epics.PV(self.pv + prefix_roi + 'SizeX')
        self.pv_roi_size_y = epics.PV(self.pv + prefix_roi + 'SizeY')

        self.pv_roi_enable.put(1)
        # set image size 1x1
        self.pv_roi_size_x.put(1)
        self.pv_roi_size_y.put(1)

        # configure HDF5 NDArrayPort to get image from ROI1 Plugin
        self.file.NDArrayPort = 'ROI1'

    def setAutoSave(self, val):
        self._autosave = val

    def getAutoSave(self):
        return self._autosave

    def getOutputFormat(self):
        return self._outputformat

    def setOutputFormat(self, val):
        self._outputformat = val

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
        return self._triggermode

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
        self._triggermode = val

    def close(self):
        """
        Stops an ongoing acquisition, if any, and puts the EPICS IOC in idle state.
        """
        self._done = 1

    def getIntensity(self):
        return self.pvSensorBias.get()

    def getValue(self, **kwargs):
        value = self.getIntensity()
        return value

    def setCountTime(self, t):
        """
        Sets the image acquisition time.
        Parameters
        ----------
        t : `float`
            Acquisition time
        """
        pass

    def setPresetValue(self, channel, val):
        """
        Dummy method to set initial counter value.
        """
        pass

    def getFileName(self):
        """
        Returns the output image file name.

        Returns
        ----------
        name : `string`
            The name of the image.
        """
        return self._filename

    def getFilePath(self):
        """
        Gets the output image file path. The image will be saved in this location
        after the acquisition.

        Parameters
        ----------
        name : `string`
            The path of location to save the image.
        """
        return self._filepath

    def setFilePath(self, val):
        """
        Sets the output image file path. The image will be saved in this location
        after the acquisition.

        Parameters
        ----------
        name : `string`
            The path of location to save the image.
        """
        self._filepath = val

    def setFileName(self, val):
        """
        Sets the output image file name. The image will be saved with this name
        after the acquisition.

        Parameters
        ----------
        name : `string`
            The name of the image.
        """
        self._filename = val

    def getNframes(self):
        """
        Gets the number of frames to acquire.

        Returns
        ----------
        nframes : `int`
            The name of the image.
        """
        return self._nframes

    def setNframes(self, val):
        """
        Sets the number of frames to acquire.

        Parameters
        ----------
        nframes : `int`
            The name of the image.
        """
        self._nframes = val

    def setRepeatNumber(self, val):
        self._repeat_number = val

    def getRepeatNumber(self):
        return self._repeat_number

    def setParams(self, dictionary):
        self.setRepeatNumber(dictionary['repetition'])
        if self.write and self.autowrite:
            self.dimensions = []

            nframes = 1
            for ipoints_motor in dictionary['points']:
                self.dimensions.append(len(set(ipoints_motor)))

            for i in range(len(self.dimensions), 10):
                self.dimensions.append(1)
            nframes = len(dictionary['points'][0])

            # if saxs scan, remove extra points
            if dictionary['start'][0][0] == 0 and dictionary['end'][0][0] == 0:
                nframes -= 1

            self.setNframes(nframes)

    def setWriteParams(self):
        if self.write and self.autowrite:
            # Set output path
            self.file.AutoSave = self.getAutoSave()
            self.file.setPath(self.getFilePath())
            self.file.setTemplate(self.getOutputFormat())
            self.file.setFileName(self.getFileName())
            self.file.setNumCapture(self.getNframes())
            self.file.FileNumber = self.getRepeatNumber()
        else:
            self.dumbnumb += 1
            self.setRepeatNumber(self.dumbnumb)

        print("SetWriteParams")

    def startCapture(self):
        print("startCapture")
        if self.write and self.autowrite:
            # print("Time Start Capture Pimega: ", datetime.now())
            self.file.put('Capture', 1)
            if self.fileplugin == 'cam1':
                sleep(3)  # wait pimega configure the RDMA

    def stopCapture(self):
        if self.write and self.autowrite:
            self.file.Capture = 0

    def stopAcquire(self):
        if self.write and self.autowrite:
            self.pvAcquire.put(0)

    def startCount(self):
        """
        Starts acquiring
        """
        pass

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
        return self._imagemode

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
        self._imagemode = val

    def wait(self):
        """
        Blocks until the acquisition completes.
        """
        while not self._done:
            epics.poll(evt=1.e-5, iot=0.1)
