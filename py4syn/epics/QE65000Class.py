"""Dxp Class

Python Class for EPICS QE65000 Control.

:platform: Unix
:synopsis: Python Class for EPICS Spectro control.

.. moduleauthor:: Gabriel Fedel <gabriel.fedel@lnls.br>
.. based on dxpclass from Juliano Murari and Pilatus Class from
.. Henrique Almeida
    .. note:: 10/18/2016 [gabrielfedel]  first version released
"""
from epics import PV
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
import numpy as np
from threading import Event
from py4syn.utils.timer import Timer
import os
import h5py


class QE65000(StandardDevice, ICountable):
    # CONSTRUCTOR OF QE65000 CLASS
    def __init__(self, mnemonic, pv=None, responseTimeout=15, output="./out",
                 imageDeep=1044):
        """Constructor
        responseTimeout : how much time to wait qe65000 answer
        imageDeep : how many points are collected each time
        """
        super().__init__(mnemonic)
        self.acquireChanged = Event()
        self.acquiring = False
        self.fileName = output

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

        # spectra axis
        self.pvAxis = PV(pv+":SpectraAxis")

        self.imageDeep = imageDeep

        # data to save hdf
        self.image = None
        self.lastPos = -1

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

        # save a unique point
        if self.image is None:
            fileName = self.fileName
            idx = 1
            if(fileName):
                prefix = fileName.split('.')[0]
                while os.path.exists('%s_ocean_%04d.mca' % (prefix, idx)):
                    idx += 1
                fileName = '%s_ocean_%04d.mca' % (prefix, idx)
                np.savetxt(fileName, self.spectrum, fmt='%f')
        else:
            # add a point on hdf file
            self.col = int(self.lastPos/self.rows)
            self.row = self.lastPos - self.rows*self.col
            # if is an odd line
            if (self.col % 2 != 0):
                self.row = -1*(self.row+1)

            self.image[self.col, self.row, :] = self.spectrum[:self.imageDeep]

            self.lastPos += 1

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

    # TODO: verificar
    def close(self):
        """Stops an ongoing acquisition, if any, and puts the EPICS IOC in
        idle state."""
        pass

    def startCollectImage(self, rows=0, cols=0):
        """Start to collect an image
        When collect an image, the points will be  saved on a hdf file"""
        self.rows = rows
        self.cols = cols
        # create HDF file
        fileName = self.fileName
        prefix = fileName.split('.')[0]

        # TODO: include channel on fileName

        fileName = self.fileName
        idx = 1

        while os.path.exists('%s_ocean_%04d.hdf' % (prefix, idx)):
            idx += 1
        fileName = '%s_ocean_%04d.hdf' % (prefix, idx)

        self.fileResult = h5py.File(fileName)

        # TODO: review this
        lineShape = (1, self.rows, self.imageDeep)
        # TODO: verify if it's better create it with complete or
        # resize on each point
        # TODO: verify if dtype is always int32
        # create "image"
        self.image = self.fileResult.create_dataset(
                     'data',
                     shape=(self.cols, self.rows, self.imageDeep),
                     dtype='float32',
                     chunks=lineShape)

        # create "image" normalized
        self.imageNorm = self.fileResult.create_dataset(
                     'data_norm',
                     shape=(self.cols, self.rows, self.imageDeep),
                     dtype='float32',
                     chunks=lineShape)

        # create and save X axis
        self.axis = self.fileResult.create_dataset(
                     'axis',
                     shape=(self.imageDeep),
                     dtype='float32')
        self.axis = self.pvAxis.get(asNumpy=True)

        # last collected point
        self.lastPos = 0

    def stopCollectImage(self):
        """Stop collect image"""
        self.fileResult.close()
        self.lastPos = -1

    def setNormValue(self, value):
        """Applies normalization"""
        result = np.divide(self.spectrum[:self.imageDeep], float(value))
        if self.image is None:
            # normalization for a point
            fileName = self.fileName
            idx = 1
            if(fileName):
                prefix = fileName.split('.')[0]
                while os.path.exists('%s_ocean_%04d_norm.mca' % (prefix, idx)):
                    idx += 1
                fileName = '%s_ocean_%04d_norm.mca' % (prefix, idx)
                np.savetxt(fileName, result, fmt='%f')

        else:
            self.imageNorm[self.col, self.row, :] = result
