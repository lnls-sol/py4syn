"""Pimega detector class

Python class for Pimega using EPICS area detector
IOC.

:platform: Unix
:synopsis: Python class for Pimega detector

"""

from epics import PV, ca, caput
from py4syn.epics.AreaDetector import AreaDetectorClass
from epics.devices.ad_base import AD_Camera
from epics.devices.ad_fileplugin import AD_FilePlugin
from time import sleep, time

READOUT_PIMEGA = 700e-6


class Pimega(AreaDetectorClass):

    def onImageChange(self, value, **kw):
        # print("onImageChange: ", value)
        if value:
            self._done = True

    def __init__(self, mnemonic, pv, device, fileplugin, write, autowrite, path, trigger):
        super().__init__(mnemonic, pv, device, fileplugin,
                         write, autowrite, path, trigger)

        self._done = 1
        self.detector_name = pv+':'+device+':'
        self.write_name = pv+':'+fileplugin+':'
        self.path = path
        self.trigger = trigger

        self.pvNumCaptured = PV(
            pv + ':' + device + ':NumCaptured_RBV', callback=self.onImageChange)

        if self.trigger == 'External':
            self.detector.add_callback("ArrayCounter_RBV",
                                       callback=self.onArrayCounterChange)
        else:
            self.detector.add_callback("Acquire_RBV",
                                       callback=self.onAcquireChange)

        self.autowrite = autowrite
        self.write = write

        if self.write and self.autowrite:
            self.file = AD_FilePlugin(self.write_name)
            self.setFilePath(self.path)
            self.setEnableCallback(1)
            self.setAutoSave(1)
            self.setOutputFormat("%s%s_%3.3d.hdf5")

        if self.trigger == 'External':
            self.setTriggerMode(1)  # (1) - External
        else:
            self.setTriggerMode(0)  # (0) - Internal

    def setParams(self, dictionary):
        self.detector.put('Acquire', 0, wait=True)
        self.stopCapture()

        if self.write and self.autowrite:
            self.dimensions = []
            nframes_to_capture = 1
            nframes_to_acquire = 1

            for ipoints_motor in dictionary['points']:
                self.dimensions.append(len(set(ipoints_motor)))
            self.setNextraDim(len(self.dimensions))

            for i in range(len(self.dimensions), 10):
                self.dimensions.append(1)

            self.setDimX(self.dimensions[0])
            self.setDimY(self.dimensions[1])

            nframes_to_capture = len(dictionary['points'][0])
            nframes_to_acquire = nframes_to_capture

            if dictionary['start'][0][0] == 0 and dictionary['end'][0][0] == 0:
                nframes_to_capture -= 1
                nframes_to_acquire = 1

            if 'file_points' in dictionary:
                nframes_to_capture = len(dictionary['points'][0])

            self.setNframes(nframes_to_capture)
            # To pimega ioc, the num images is setting on NumExposures PV
            self.detector.NumExposures = nframes_to_acquire
            self.setRepeatNumber(dictionary['repetition'])
            # Set acquire period with the value passed by scan cmd.
            # To guarantee that acquire period is bigger than acquire time,
            # set acquire time to zero, before set acquire period
            self.detector.AcquireTime = 0
            if 'acquire_period' in dictionary:
                self.detector.AcquirePeriod = dictionary['acquire_period'][0][0]
            else:
                self.detector.AcquirePeriod = 0
                self.detector.NumExposures = 1

    def setCountTime(self, t):
        """
        Sets the image acquisition time.
        Parameters
        ----------
        t : `float`
            Acquisition time
        """

        # Overloading the function, because the pimega should be set the acquire period
        # before than acquire time, and the acquire time should be > acquire_period + readout (700us)
        if t < self.detector.AcquirePeriod or self.detector.AcquirePeriod == 0:
            self.detector.AcquireTime = t
        else:
            self.detector.AcquireTime = self.detector.AcquirePeriod - READOUT_PIMEGA

    def startCount(self):
        """
        Starts acquiring
        """
        if not self._done:
            raise RuntimeError('Already counting')

        self.detector.Acquire = 1
        if not self.trigger == "Internal":
            sleep(2)  # wait acquire cmd finished before configure trigger
        self._done = 0  # force the confirmation that the detector has already received acquire function

    def setWriteParams(self):
        self.detector.TriggerMode = self.getTriggerMode()
        if self.write and self.autowrite:
            # points
            self.file.NumExtraDims = self.getNextraDim()
            self.file.ExtraDimSizeY = self.getDimY()
            self.file.setWriteMode(mode=self.getWriteMode())
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


class PimegaParams(AreaDetectorClass):
    def __init__(self, mnemonic, pv, device, fileplugin, write, autowrite, path, trigger):
        super().__init__(mnemonic, pv, device, fileplugin,
                         write, autowrite, path, trigger)

        print("Init Pimega Params")
        self._done = 1
        self.detector_name = pv+':'+device+':'
        self.write_name = pv+':'+fileplugin+':'
        self.path = path
        self.pv = pv
        self.detector = AD_Camera(self.detector_name)

        self.autowrite = autowrite
        self.write = write

        if self.write and self.autowrite:
            self.config_H5_plugin()

    def config_H5_plugin(self):
        self.file = AD_FilePlugin(self.write_name)
        self.file.add_pv(self.write_name + 'Compression', attr='compression')
        self.file.add_pv(self.write_name + 'SWMRMode', attr='swmrmode')

        self.file.compression = 3
        self.file.swmrmode = 1
        self.file.EnableCallbacks = 1
        self.file.FileWriteMode = 2

        self.configure_adplugins()

    def configure_adplugins(self):
        prefix_roi = ':ROI1:'
        self.pv_roi_enable = PV(self.pv + prefix_roi + 'EnableCallbacks')
        self.pv_roi_size_x = PV(self.pv + prefix_roi + 'SizeX')
        self.pv_roi_size_y = PV(self.pv + prefix_roi + 'SizeY')

        self.pv_roi_enable.put(1)
        # set image size 1x1
        self.pv_roi_size_x.put(1)
        self.pv_roi_size_y.put(1)

        # configure HDF5 NDArrayPort to get image from ROI1 Plugin
        self.file.NDArrayPort = 'ROI1'

    def setParams(self, dictionary):
        if self.write and self.autowrite:
            self.dimensions = []
            nframes = 1

            for ipoints_motor in dictionary['points']:
                self.dimensions.append(len(set(ipoints_motor)))
            self.setNextraDim(len(self.dimensions))

            for i in range(len(self.dimensions), 10):
                self.dimensions.append(1)

            self.setDimX(self.dimensions[0])
            self.setDimY(self.dimensions[1])

            nframes = len(dictionary['points'][0])

            if dictionary['start'][0][0] == 0 and dictionary['end'][0][0] == 0:
                nframes -= 1

            self.setNframes(nframes)
            self.setRepeatNumber(dictionary['repetition'])

    def startCount(self):
        """
        Starts acquiring
        """
        pass

    def setWriteParams(self):
        if self.write and self.autowrite:
            self.file.EnableCallbacks = self.getEnableCallback()

            # points
            self.file.NumExtraDims = self.getNextraDim()
            self.file.ExtraDimSizeY = self.getDimY()
            self.file.setWriteMode(mode=self.getWriteMode())
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

    def setCountTime(self, t):
        """
        Sets the image acquisition time.
        Parameters
        ----------
        t : `float`
            Acquisition time
        """
        pass
