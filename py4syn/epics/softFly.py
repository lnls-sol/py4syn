from threading import Event

from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
from epics import PV, ca, caput
from py4syn.epics.AreaDetector import AreaDetectorClass
from epics.devices.ad_base import AD_Camera
from epics.devices.ad_fileplugin import AD_FilePlugin
from time import sleep, time


READOUTTIME = 1


class softFly(AreaDetectorClass):
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
            self.setImageMode(1)  # set multiple frames

        self.detector.Scan = 9
        self.detector.ImageMode = self.getImageMode()
        self.autowrite = autowrite
        self.write = write

        if self.write and self.autowrite:
            self.file = AD_FilePlugin(self.write_name)
            self.file.add_pv(self.write_name+"NDAttributeChunk",
                             attr="NDAttributeChunk")
            self.file.add_pv(self.write_name+"SWMRMode",
                             attr="SWMRMode")
            self.file.add_pv(self.write_name+"NumExtraDims",
                             attr="NumExtraDims")
            self.file.add_pv(self.write_name+"ExtraDimSizeX",
                             attr="ExtraDimSizeX")
            self.file.add_pv(self.write_name+"ExtraDimSizeY",
                             attr="ExtraDimSizeY")
            self.file.EnableCallbacks = 1

            # Turn on the SWMR mode for the next acquisition
            self.file.SWMRMode = 1

            # Determine to flush the NDAttribute datasets to disk each 1 frame
            self.file.NDAttributeChunk = 1

            self.setFilePath(self.path)
            self.setEnableCallback(1)
            self.setAutoSave(1)
            self.setWriteMode(2)
            self.setOutputFormat("%s%s_%03d.hdf5")
            self.stopCapture()

        if self.trigger == 'External':
            self.setTriggerMode(3)
        else:
            self.setTriggerMode(0)
        self.detector.ImageMode = self.getImageMode()
        self.detector.ArrayCallbacks = 1

    def setParams(self, dictionary):
        if self.write and self.autowrite:
            self.dimensions = []
            nframes = 1
            for ipoints_motor in dictionary['points']:
                # Gambiarra pq ele conta o ultimo ponto
                self.dimensions.append(len(set(ipoints_motor)))
            self.setNextraDim(len(self.dimensions))

            for i in range(len(self.dimensions), 10):
                self.dimensions.append(1)

            self.setDimX(self.dimensions[0])
            self.setDimY(self.dimensions[1])

            for i in self.dimensions:
                nframes = nframes * i

            self.setNframes(nframes)
            self.detector.NumImages = nframes

            if (self.trigger == 'Internal'):
                self.detector.NumImages = nframes

            try:
                self.detector.AcquirePeriod = dictionary['acquire_period'][0][0]
            except Exception:
                self.detector.AcquirePeriod = dictionary['sleep'] + \
                    dictionary['time'][0][0]

            self.setRepeatNumber(dictionary['repetition'])

    def startCount(self):
        """
        Starts acquiring 
        """
        if not self._done:
            raise RuntimeError('Already counting')

        self.detector.Acquire = 1
