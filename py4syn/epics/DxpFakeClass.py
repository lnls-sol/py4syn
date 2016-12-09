"""Dxp Class

Python Class for EPICS Fake Dxp Control.

:platform: Unix
:synopsis: Python Class for EPICS Spectro control.

.. moduleauthor:: Gabriel Fedel <gabriel.fedel@lnls.br>
    .. note:: 11/30/2016 [gabrielfedel]  first version released
"""
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
import numpy as np
import os
import h5py

class DxpFake(StandardDevice, ICountable):
    # CONSTRUCTOR OF DXP CLASS
    def __init__(self, mnemonic, numberOfChannels=4, numberOfRois=32,
                 pv=None, dxpType="mca", responseTimeout=15, output="out"):
        """ Constructor
        responseTimeout : how much time to wait dxp answer
        """
        super().__init__(mnemonic)
        self.acquiring = False
        self.fileName = output

        self.dxpType = dxpType
        self.rois = numberOfRois

        self.imageDeep = 2048

        self.image = None

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

    def setCountStop(self):
        pass

    def getValueChannel(self, **kwargs):
        """Return intensity
        channel is on format mcaC.Rr, where C is  the channel and
        r is the ROI"""
        channel = kwargs['channel']
        c = int(channel[3]) - 1
        if(len(channel) > 4):
            return np.random.rand()
        else:
            self.saveSpectrum(c, **kwargs)
            return 1.0

    # save the spectrum intensity in a mca file
    def saveSpectrum(self, ch, **kwargs):
        self.spectrum = np.random.randint(100, size=(2048))

        # save a unique point
        if self.image is None:
            fileName = self.fileName
            idx = 0
            if(fileName):
                prefix = fileName.split('.')[0]
                while os.path.exists('%s_%s%d_%04d.mca' % (prefix, self.dxpType,
                                                           ch, idx)):
                    idx += 1
                fileName = '%s_%s%d_%04d.mca' % \
                           (prefix, self.dxpType, ch, idx)
                np.savetxt(fileName, self.spectrum, fmt='%f')
        else:
            # add a point on hdf file
            self.row = int(self.lastPos/self.cols)
            self.col = self.lastPos - self.row*self.cols
            # if is an odd line
            if (self.row % 2 != 0):
                self.col = -1*(self.col+1)
            self.image[self.row,self.col,:] = self.spectrum

            self.lastPos += 1

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
        self.rows = rows
        self.cols = cols
        # create HDF file
        fileName = self.fileName
        prefix = fileName.split('.')[0]

        # TODO: include channel on fileName

        fileName = self.fileName
        idx = 0

        while os.path.exists('%s_%s_%04d.hdf' % (prefix, self.dxpType, idx)):
            idx += 1
        fileName = '%s_%s_%04d.hdf' % (prefix, self.dxpType, idx)

        self.fileResult = h5py.File(fileName,'w')

        # TODO: review this
        lineShape = (1, self.cols, self.imageDeep)
        # TODO: verify if it's better create it with complete or
        # resize on each point
        # TODO: verify if dtype is always int32
        # create "image"
        self.image = self.fileResult.create_dataset(
                     'data',
                     shape=(self.rows, self.cols , self.imageDeep),
                     dtype='int32',
                     chunks=lineShape)

        # create "image" normalized
        self.imageNorm = self.fileResult.create_dataset(
                     'data_norm',
                     shape=(self.rows, self.cols , self.imageDeep),
                     dtype='float32',
                     chunks=lineShape)

        # last collected point
        self.lastPos = 0

    def stopCollectImage(self):
        """Stop collect image"""
        self.fileResult.close()
        self.lastPos = -1

    def setNormValue(self, value):
        """Applies normalization"""
        result = np.divide(self.spectrum, float(value))
        if self.image is None:
            # normalization for a point
            fileName = self.fileName
            idx = 0
            if(fileName):
                prefix = fileName.split('.')[0]
                while os.path.exists('%s_%s%d_%04d_norm.mca' % (prefix, self.dxpType,
                                                           ch, idx)):
                    idx += 1
                fileName = '%s_%s%d_%04d_norm.mca' % \
                           (prefix, self.dxpType, ch, idx)
                np.savetxt(fileName, result, fmt='%f')

        else:
            self.imageNorm[self.row,self.col,:] = result

