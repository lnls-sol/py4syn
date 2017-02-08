"""Dxp Class

Python Class for EPICS QE65000 Control.

:platform: Unix
:synopsis: Python Class for EPICS Spectro control.

.. moduleauthor:: Gabriel Fedel <gabriel.fedel@lnls.br>
.. based on dxpclass from Juliano Murari and Pilatus Class from
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

class QE65000(ImageHDF):
    # CONSTRUCTOR OF QE65000 CLASS
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

        # the spectra come from different pv if use darkcorrection
        if self.pvDarkCorrection.get() == 1:
            self.pvSpectrum = PV(pv+":DarkCorrectedSpectra")
        else:
            self.pvSpectrum = PV(pv+":Spectra")

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

    # save the spectrum intensity in a mca file
    # or an hdf file
    def saveSpectrum(self, **kwargs):
        self.spectrum = self.pvSpectrum.get(as_numpy=True)

        super().saveSpectrum()

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
            raise RuntimeError('QE65000 is not answering')

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
