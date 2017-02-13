"""Dxp Class

Python Class for EPICS Dxp Control.

:platform: Unix
:synopsis: Python Class for EPICS Spectro control.

.. moduleauthor:: Gabriel Fedel <gabriel.fedel@lnls.br>
.. based on dxpclass from Juliano Murari and Pilatus Class from i
.. Henrique Almeida
    .. note:: 10/18/2016 [gabrielfedel]  first version released
"""
import os

from epics import PV
import numpy as np
from threading import Event
import h5py
from py4syn.utils.timer import Timer
from py4syn.epics.ImageHDFClass import ImageHDF

# constants used to parse PV name
CHANNELPOSITION=3
ROIPOSITION=6

class Dxp(ImageHDF):

    # CONSTRUCTOR OF DXP CLASS
    def __init__(self, mnemonic, numberOfChannels=4, numberOfRois=32,
                 pv=None, dxpType="mca", responseTimeout=15, output="./out",
                 numPoints=2048):
        """ Constructor
        responseTimeout : how much time to wait dxp answer
        imageDeep : how many points are collected each time
        """
        super().__init__(mnemonic, numPoints, output, dxpType)

        self.acquireChanged = Event()
        self.acquiring = False

        # determines the start of counting
        self.pvDxpEraseStart = PV(pv+":EraseStart.VAL")
        # determines mode of counting (Live Time, Real Time, ...)
        self.pvDxpPresetMode = PV(pv+":PresetMode.VAL")

        self.pvDxpStop = PV(pv+":StopAll.VAL")
        # store all channels
        self.pvDxpChannels = []
        # store ROIs
        self.pvDxpRois = []

        # store Acquire Time for each channel
        self.pvDxpAcquireTime = []

        for c in range(0, numberOfChannels):
            # store each channel
            self.pvDxpChannels.append(PV(pv+":"+dxpType+str(c+1)))
            # for each channel store the PV for AcquireTime
            self.pvDxpAcquireTime.append(PV(pv+":" + dxpType + "%d.PLTM"
                                         % (c+1)))
            self.pvDxpRois.append([])
            # storeing each ROI in your channel
            for r in range(0, numberOfRois):
                self.pvDxpRois[c].append(PV(pv+":"+dxpType+str(c+1)+'.R'
                                         + str(r)))

        self.pvDxpAcquire = PV(pv+":Acquiring")
        self.pvDxpAcquire.add_callback(self.statusChange)
        self.channels = numberOfChannels
        self.rois = numberOfRois

        self.responseTimeout = responseTimeout
        self.timer = Timer(self.responseTimeout)

    def statusChange(self, value, **kw):
        """
        Helper callback used to wait for the end of the acquisition.
        """
        self.acquiring = value
        # threads waiting are awakened
        self.acquireChanged.set()

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
        for i in range(0, self.channels):
            self.pvDxpAcquireTime[i].put(time, wait=True)

        # This make long exposure time works
        if (self.responseTimeout < time*0.4):
            self.responseTimeout = time*0.4

        self.timer = Timer(time + self.responseTimeout)

    def getCountTime(self):
        return self.pvDxpTime.get()

    def setCountStop(self):
        self.pvDxpStop.put(1, wait=True)

    def getValueChannel(self, **kwargs):
        """Return intensity
        channel is on format mcaC.Rr, where C is  the channel and
        r is the ROI"""
        channel = kwargs['channel']
        c = int(channel[CHANNELPOSITION]) - 1
        if(len(channel) > ROIPOSITION + 1):
            r = int(channel[ROIPOSITION])
            return self.pvDxpRois[c][r].get()
        else:
            self.saveSpectrum(c, **kwargs)
            return 1.0

    def saveSpectrum(self, ch, **kwargs):
        '''save the spectrum intensity in a mca file or an hdf file
        This method load spectrum from a PV and then save it to HDF file'''
        self.ch = ch
        self.spectrum = self.pvDxpChannels[self.ch].get(as_numpy=True)

        if self.image is None:
            # if is a point, prefix is different
            self.prefix = self.dxpType + str(self.ch)

        super().saveSpectrum()

    def isCountRunning(self):
        return (self.pvDxpAcquire.get())

    def wait(self):
        """
        Blocks until the acquisition completes.
        """
        if self.acquiring is False:
            return

        self.acquireChanged.clear()
        # while acquiring and not time out waits
        # TODO: find a better way to do this
        while self.acquiring and self.timer.check():
            self.acquireChanged.wait(0.001)
            self.acquireChanged.clear()

        if self.timer.expired():
            raise RuntimeError('DXP is not answering')

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
        return self.acquiring

    def startCount(self):
        """ Starts acquiring an spectrum
        It's necessary to call setCounTime before"""
        if self.acquiring:
            raise RuntimeError('Already counting')

        self.acquiring = True
        self.pvDxpEraseStart.put(1)
        # resets initial time value
        self.timer.mark()

    def stopCount(self):
        self.setCountStop()

    def setPresetValue(self, channel, val):
        """Dummy method"""
        pass

    def close(self):
        """Stops an ongoing acquisition, if any, and puts the EPICS IOC in
        idle state."""
        self.pvDxpStop.put(1, wait=True)

    def startCollectImage(self, rows=0, cols=0):
        """Start to collect an image
        When collect an image, the points will be  saved on a hdf file"""
        super().startCollectImage("int32", rows, cols)

    def setNormValue(self, value):
        """Applies normalization"""
        if self.image is None:
            self.prefix = self.dxpType + str(self.ch)

        super.setNormValue(value)

