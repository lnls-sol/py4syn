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
from epics import PV, ca, caput
from py4syn.epics.AreaDetector import AreaDetectorClass
from epics.devices.ad_base import AD_Camera
from epics.devices.ad_fileplugin import AD_FilePlugin
from time import sleep, time


# Pilatus ReadOut time
READOUTTIME = 1


class Pilatus(AreaDetectorClass):
    def __init__(self, mnemonic, pv, device, fileplugin, write, autowrite, path, trigger):
        super().__init__(mnemonic, pv,device, fileplugin,
                 write, autowrite, path, trigger)

        self._done = 1
        self.timi = time()
        self.counter= None,
        self.detector_name = pv+':'+device+':'
        self.write_name = pv+':'+fileplugin+':'
        self.path = path
        self.detector = AD_Camera(self.detector_name)
        self.detector.add_pv(self.detector_name+"Acquire_RBV",
                             attr='Scan')

        self.detector.add_pv(self.detector_name + "Armed", attr='Armed')

        self.detector.add_pv(self.detector_name + "FilePath", attr='FilePath')
        self.detector.add_pv(self.detector_name + "FileName", attr='FileName')
        self.detector.add_pv(self.detector_name + "FileTemplate", attr='FileTemplate')

        self.detector.FilePath = self.path
        self.detector.FileTemplate = '%s%s_%03d.tif'
        self.detector.FileName = 'temp'


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
            self.file.add_pv(self.write_name+"NumExtraDims",
                             attr="NumExtraDims")
            self.file.add_pv(self.write_name+"ExtraDimSizeX",
                             attr="ExtraDimSizeX")
            self.file.add_pv(self.write_name+"ExtraDimSizeY",
                             attr="ExtraDimSizeY")
            self.file.EnableCallbacks = 1

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

        print("Finish init Pilatus")

    def setParams(self,dictionary):
        if self.write and self.autowrite:
            self.dimensions = []
            nframes = 1
            for ipoints_motor in dictionary['points']:
                # Gambiarra pq ele conta o ultimo ponto
                self.dimensions.append(len(set(ipoints_motor)))
            self.setNextraDim(len(self.dimensions))

            for i in range(len(self.dimensions),10):
                self.dimensions.append(1)

            self.setDimX(self.dimensions[0])
            self.setDimY(self.dimensions[1])

            for i in self.dimensions:
                nframes = nframes * i

            self.setNframes(nframes)
            self.detector.NumImages = nframes

            if (self.trigger == 'Internal'):
                self.detector.NumImages = 1

            try:
                self.detector.AcquirePeriod = dictionary['aquire_time'][0][0]
            except Exception:
                print(dictionary['time'])
                self.detector.AcquirePeriod = dictionary['sleep'] + dictionary['time'][0][0]

            self.setRepeatNumber(dictionary['repetition'])

    def armedStatus(self):
        return self.detector.Armed

    def startCount(self):
        """
        Starts acquiring 
        """
        if not self._done:
            raise RuntimeError('Already counting')

        
        self.detector.Acquire = 1

        while not self.armedStatus():
            sleep(.1)
        self._done = 0 # force the confirmation that the detector has already received acquire function