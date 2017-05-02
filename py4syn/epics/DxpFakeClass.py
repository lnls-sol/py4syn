"""Dxp Class

Python Class for EPICS Fake Dxp Control.

:platform: Unix
:synopsis: Python Class for EPICS Spectro control.

.. moduleauthor:: Gabriel Fedel <gabriel.fedel@lnls.br>
    .. note:: 11/30/2016 [gabrielfedel]  first version released
"""
import os

import numpy as np
import h5py
from py4syn.epics.ImageHDFClass import ImageHDF

NUMPOINTS = 2048
# constants used to parse PV name
CHANNELPOSITION=3
ROIPOSITION=6

class DxpFake(ImageHDF):
    # CONSTRUCTOR OF DXP CLASS
    def __init__(self, mnemonic, numberOfChannels=4, numberOfRois=32,
                 pv=None, dxpType="mca", responseTimeout=15, output="out"):
        """ Constructor
        responseTimeout : how much time to wait dxp answer
        """
        super().__init__(mnemonic, NUMPOINTS, output, dxpType)
        self.acquiring = False
        self.rois = numberOfRois

    def statusChange(self, value, **kw):
        """
        Helper callback used to wait for the end of the acquisition.
        """
        pass

    def setCountTime(self, time):
        """
        Method to set the count time of a scaler device.

        Parameters
        ----------
        time : `float`
            Count time to set to scaler device .

        Returns
        -------
        out : None
        """
        pass

    def getCountTime(self):
        pass

    def getRealTime(self):
        return np.random.rand()

    def setCountStop(self):
        pass

    def getValueChannel(self, **kwargs):
        """Return intensity
        channel is on format mcaC.Rr, where C is  the channel and
        r is the ROI"""
        channel = kwargs['channel']
        c = int(channel[CHANNELPOSITION]) - 1
        if(len(channel) > ROIPOSITION):
            return np.random.rand()
        else:
            self.saveSpectrum(c, **kwargs)
            return 1.0

    def saveSpectrum(self, ch, **kwargs):
        self.spectrum = np.random.randint(100, size=(2048))
        self.ch = ch

        super().saveSpectrum()

    def isCountRunning(self):
        pass

    def wait(self):
        """
        Blocks until the acquisition completes.
        """
        pass

    def canMonitor(self):
        """ Returns false indcating Dxp cannot be use as a counter monitor"""
        return False

    def canStopCount(self):
        """
        Returns true indicating that Dxp has a stop command.
        """
        return True

    def getValue(self, **kwargs):
        """
        This is a dummy method that always returns zero, which is part of the
        :class:`py4syn.epics.ICountable` interface. Dxp does not return
        a value while scanning. Instead, it stores a mca file with result .
        """
        if(kwargs):
            return self.getValueChannel(**kwargs)
        return self.getValueChannel()

    def isCounting(self):
        pass

    def startCount(self):
        pass

    def stopCount(self):
        pass

    def setPresetValue(self, channel, val):
        """Dummy method"""
        pass

    def close(self):
        pass

    def startCollectImage(self, rows=0, cols=0):
        """Start to collect an image
        When collect an image, the points will be  saved on a hdf file"""
        super().startCollectImage("int32", rows, cols)
