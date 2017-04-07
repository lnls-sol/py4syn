"""Dxp Class

Python Class for EPICS Ocean Control.

:platform: Unix
:synopsis: Python Class for EPICS Spectro control.

.. moduleauthor:: Gabriel Fedel <gabriel.fedel@lnls.br>
.. based on dxpclass from Juliano Murari and Pilatus Class from
.. Henrique Almeida
    .. note:: 10/18/2016 [gabrielfedel]  first version released
"""
import os
from bisect import bisect

from epics import PV, caget
import numpy as np
from threading import Event
import h5py
from py4syn.utils.timer import Timer
from py4syn.epics.ImageHDFClass import ImageHDF

class Ocean(ImageHDF):
    # CONSTRUCTOR OF Ocean CLASS
    def __init__(self, mnemonic, pv=None, responseTimeout=15, output="./out",
                 numPoints=1044):
        """Constructor
        responseTimeout : how much time to wait qe65000 answer
        numPoints : how many points are collected each time
        """
        super().__init__(mnemonic, numPoints, output, 'ocean')
        self.acquireChanged = Event()
        self.acquiring = False

        # determines the start of counting
        self.pvStart = PV(pv+":Acquire")
        # determines mode of Acquisition (Single,Continous, Dark Spectrum)
        self.pvAcquireMode = PV(pv+":AcquisitionMode")

        # use darkcorrection
        self.pvDarkCorrection = PV(pv+":ElectricalDark")

        # set Acquire Time
        self.pvAcquireTime = PV(pv+":SetIntegration")

        # integration Time
        self.pvTime = PV(pv+":IntegrationTime:Value")

        # control the end of acquire process
        self.pvAcquire = PV(pv+":Acquiring")
        self.pvAcquire.add_callback(self.statusChange)

        # acquisition mode
        self.pvAcMode = PV(pv+":AcquisitionMode")
        # set to single mode
        self.pvAcMode.put("Single")
        #axis Spectra
        self.axis = caget(pv + ":SpectraAxis", as_numpy=True)[:self.numPoints]

        self.pv = pv

        # regions of interest
        self.ROIS = []

        self.responseTimeout = responseTimeout
        self.timer = Timer(self.responseTimeout)

    def statusChange(self, value, **kw):
        """
        Helper callback used to wait for the end of the acquisition.
        """
        if value == 0:
            self.acquiring = False
        else:
            self.acquiring = True
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
        self.pvTime.put(time, wait=True)
        self.timer = Timer(time + self.responseTimeout)

    def getCountTime(self):
        return self.pvTime.get()

    def setCountStop(self):
        # TODO: test
        # Work only when in continuos mode
        pass

    def saveSpectrum(self, **kwargs):
        ''' save the spectrum intensity in a mca file or an hdf file '''
        dark = self.pvDarkCorrection.get()

        # the spectra come from different pv if use darkcorrection
        if dark == 1:
            self.pvSpectrum = PV(self.pv+":DarkCorrectedSpectra")
        else:
            self.pvSpectrum = PV(self.pv+":Spectra")

        allSpectrum = self.pvSpectrum.get(as_numpy=True)[:self.numPoints]
        self.spectrum = allSpectrum
        super().saveSpectrum()

        # there are ROIS to save
        if len(self.ROIS) > 0:
            i = 1
            for mini, maxi in self.ROIS:
                # get the spectrum positions
                start = bisect(self.axis, mini)
                end = bisect(self.axis, maxi)
                roi = allSpectrum[start:end]
                self.spectrum = roi
                super().saveSpectrum(sufixName = "_ROI" + str(i))
                i += 1

    def isCountRunning(self):
        return (self.acquiring)

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
            raise RuntimeError('Ocean is not answering')

    def canMonitor(self):
        """ Returns false indicating cannot be use as a counter monitor"""
        return False

    def canStopCount(self):
        """
        Returns true indicating that Dxp has a stop command.
        """
        return False

    def getValue(self, **kwargs):
        """Return intensity
        It's a dummy method, always return 1.0. """
        self.saveSpectrum()
        return 1.0

    def isCounting(self):
        return self.acquiring

    def startCount(self):
        """ Starts acquiring an spectrum
        It's necessary to call setCounTime before"""

        if self.acquiring:
            raise RuntimeError('Already counting')

        self.acquiring = True
        self.pvStart.put("Stop")
        # resets initial time value
        self.timer.mark()

    def stopCount(self):
        self.setCountStop()

    def setPresetValue(self, channel, val):
        """Dummy method"""
        pass

    def startCollectImage(self, rows=0, cols=0):
        super().startCollectImage('float32', rows, cols)

    def addRoi(self, roi):
        """ Insert a new roi
        roi: a tuple with begin and end: (begin,end)"""
        self.ROIS.append(roi)
