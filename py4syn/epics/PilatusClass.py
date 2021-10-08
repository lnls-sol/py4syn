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

    def __init__(self, mnemonic, pv, device, fileplugin, write, autowrite, path, trigger):
        super().__init__(mnemonic, pv, device, fileplugin, write, autowrite, path, trigger)
        detector_name = pv + ":" + device + ":"
        self._detector.add_pv(detector_name + "Armed", attr='Armed')

    def armedStatus(self):
        return bool(self._detector.Armed)

    def setParams(self, dictionary):
        """Sets up the AD device to a state usable by scan-utils."""

        assert not self.isCounting(), "Already counting"
        assert not self._file.Capture_RBV, "Already counting"

        # Suport for extra dimensions isn't very good on Pilatus IOC
        # so we leave it disabled on purpose, however we provide the
        # code here in case someone wishes to enable it.

        # Calculate the size of each dimension.
        dim_sizes = []
        for points in dictionary["points"]:
            # Use set() to remove duplicates.
            dim_sizes.append(len(set(points)))

        # self.setNextraDim(min(len(dim_sizes), 2))
        self.setNextraDim(0)

        # The Pilatus IOC we have now supports only 2 extra dimmensions.
        # Maybe a future release will fix this.
        dim_names = ["X", "Y"]
        for name, size in zip(dim_names, dim_sizes):
            attr = "ExtraDimSize" + name
            # self._file.ensure_value(attr, size)

        # Use dim_sizes to calculate the number of frames to acquire.
        nframes = 1
        for i in dim_sizes:
            nframes = i * nframes

        self.setCountTime(dictionary["time"][0][0])

        # Pilatus IOC does NOT honor any image mode.
        # We set it to "Multiple" in case a future release fix this.
        self.setImageMode(1)

        if self.trigger = "Internal"
            self._detector.ensure_value("NumImages", 1)
        else:
            self._detector.ensure_value("NumImages", nframes)
        self._detector.ensure_value("NumExposures", 1)

        if self.write:
            self.setEnableCallback(1)
            self.setWriteMode(2)
            self._file.ensure_value("AutoIncrement", 0)
            self.setRepeatNumber(dictionary["repetition"])
            self.setNframes(nframes)
        else:
            self.setEnableCallback(0)

        # Removing this sleep causes a segfault on camserver.
        # I believe camserver needs some time to register all param changes.
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
