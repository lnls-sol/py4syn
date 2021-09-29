"""Dectris Pilatus X-ray camera class

Python class for Pilatus X-ray cameras using EPICS area detector
IOC.

:platform: Unix
:synopsis: Python class for Pilatus X-ray cameras

"""
from threading import Event

from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
from epics import PV, ca, caput
from py4syn.epics.AreaDetector import AreaDetectorClass
from epics.devices.ad_base import AD_Camera
from epics.devices.ad_fileplugin import AD_FilePlugin
from time import sleep, time


class Pilatus(AreaDetectorClass):
    def __init__(self, mnemonic, pv, device, fileplugin, write, autowrite, path, trigger):
        super().__init__(mnemonic, pv, device, fileplugin,
                         write, autowrite, path, trigger)

        self._done = 1
        self.timi = time()
        self.counter = None,
        self.detector_name = pv+':'+device+':'
        self.write_name = pv+':'+fileplugin+':'
        self.path = path
        self.detector = AD_Camera(self.detector_name)
        self.detector.add_pv(self.detector_name+"Acquire_RBV",
                             attr='Scan')

        self.detector.add_pv(self.detector_name + "Armed", attr='Armed')

        self.armed_status = self.armedStatus()

        self.trigger = trigger
        self.dumbnumb = 0
        self.detector.Acquire = 0
        self.setFilePath('')

        if self.trigger == 'External':
            self.setImageMode(2)
            self.detector.add_callback("ArrayCounter_RBV",
                                       callback=self.onArrayCounterChange)
        else:
            self.detector.add_callback("Acquire_RBV",
                                       callback=self.onAcquireChange)
            self.setImageMode(0)

        self.detector.Scan = 9
        self.detector.ImageMode = self.getImageMode()
        self.autowrite = autowrite
        self.write = write

        if self.write and self.autowrite:
            self.file = AD_FilePlugin(self.write_name)
            self.file.EnableCallbacks = 1

            self.setFilePath(self.path)
            self.setEnableCallback(1)
            self.setAutoSave(1)
            self.setOutputFormat("%s%s_%3.3d.hdf5")
            self.stopCapture()

        if self.trigger == 'External':
            self.setTriggerMode(1)
        else:
            self.setTriggerMode(0)
        self.detector.ImageMode = self.getImageMode()

        self.detector.ArrayCallbacks = 1

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

            # for i in self.dimensions:
            #    nframes = nframes * i

            nframes = len(dictionary['points'][0])

            if dictionary['start'][0][0] == 0 and dictionary['end'][0][0] == 0:
                nframes -= 1

            self.setNframes(nframes)
            self.detector.NumImages = nframes

            if (self.trigger == 'Internal'):
                self.detector.NumImages = 1
            else:
                self.aq_time = dictionary['acquire_period'][0][0]

            try:
                self.detector.AcquirePeriod = dictionary['acquire_period'][0][0]
            except Exception:
                print(dictionary['time'])
                self.detector.AcquirePeriod = dictionary['sleep'] + \
                    dictionary['time'][0][0]

            self.setRepeatNumber(dictionary['repetition'])

    def armedStatus(self):
        return self.detector.Armed

    def setCountTime(self, t):
        """
        Sets the image acquisition time.
        Parameters
        ----------
        t : `float`
            Acquisition time
        """
        self.detector.AcquireTime = t
        if (self.trigger == 'Internal'):
            self.detector.AcquirePeriod = t+0.2
        else:
            self.detector.AcquirePeriod = self.aq_time

    def startCount(self):
        """
        Starts acquiring 
        """
        if not self._done:
            raise RuntimeError('Already counting')

        self.detector.Acquire = 1

        while not self.armedStatus():
            sleep(.1)
        self._done = 0  # force the confirmation that the detector has already received acquire function

    def setWriteParams(self):
        self.detector.Acquire = 0
        self.detector.ImageMode = self.getImageMode()
        self.detector.TriggerMode = self.getTriggerMode()
        if self.write and self.autowrite:
            self.file.EnableCallbacks = self.getEnableCallback()

            # points
            self.file.NumExtraDims = self.getNextraDim()
            #self.detector.NumImages     =   self.getDimX()
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
