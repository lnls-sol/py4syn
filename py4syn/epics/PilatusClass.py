"""Dectris Pilatus X-ray camera class

Python class for Pilatus X-ray cameras using EPICS area detector
IOC.

:platform: Unix
:synopsis: Python class for Pilatus X-ray cameras

.. moduleauthor:: Henrique Dante de Almeida <henrique.almeida@lnls.br>
                  Carlos Doro Neto <carlos.doro@lnls.br>
"""

from time import sleep
from py4syn.epics.AreaDetector import AreaDetectorClass


class Pilatus(AreaDetectorClass):

    def __init__(self, mnemonic, pv, device, fileplugin,
                 write, autowrite, path, trigger):

        super().__init__(mnemonic, pv, device, fileplugin,
                         write, autowrite, path, trigger)

        detector_name = pv + ":" + device + ":"
        self._detector.add_pv(detector_name + "Armed", attr='Armed')

    def armedStatus(self):
        return bool(self._detector.Armed)

    def setParams(self, dictionary):
        super().setParams(dictionary)
        self.setNextraDim(0)
        sleep(1)

    # ICountable methods overriding

    def setCountTime(self, t):
        """Sets the image acquisition time.

        Parameters
        ----------
        t : `float`
        """
        self._detector.ensure_value("AcquireTime", t)
        self._detector.ensure_value("AcquirePeriod", t + .01)

    def startCount(self):
        """Starts acquiring"""
        self._detector.ensure_value("Acquire", 1)
        while not self.armedStatus():
            pass
