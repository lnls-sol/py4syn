"""Image HDF Class

Python Class for Save HDF images .

:platform: Unix
:synopsis: Python Class for HDF images.

.. moduleauthor:: Gabriel Fedel <gabriel.fedel@lnls.br>
.. note:: 06/02/2017 [gabrielfedel]  first version released
"""
from epics import PV
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
import numpy as np
from threading import Event
from py4syn.utils.timer import Timer
import os
import h5py


class ImageHDF():
    # CONSTRUCTOR OF ImageHDF CLASS
    def __init__(self,  numPoints):
        """ Constructor
        """
        self.numPoints = numPoints
        self.image = None


    def nameFile(self):
        '''Generate correct name to file'''
        pass
    # save the spectrum intensity in a mca file if is a point
    # or an hdf file if is an image
    def saveSpectrum(self, spectrum):
        # save a unique point
        if self.image is None:
            fileName = self.fileName
            idx = 1
            if(fileName):
                prefix = fileName.split('.')[0]
                while os.path.exists('%s_%s%d_%04d.mca' % (prefix,
                                                           self.dxpType,
                                                           self.ch, idx)):
                    idx += 1
                fileName = '%s_%s%d_%04d.mca' % \
                           (prefix, self.dxpType, self.ch, idx)
                np.savetxt(fileName, self.spectrum, fmt='%f')
        else:
            # add a point on hdf file
            self.spectrum[0] = self.lastPos
            self.col = int(self.lastPos/self.rows)
            self.row = self.lastPos - self.rows*self.col
            # if is an odd line
            if (self.col % 2 != 0):
                self.row = -1*(self.row+1)
            self.image[self.col, self.row, :] = self.spectrum

            self.lastPos += 1

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

        while os.path.exists('%s_%s_%04d.hdf' % (prefix, self.dxpType, idx)):
            idx += 1
        fileName = '%s_%s_%04d.hdf' % (prefix, self.dxpType, idx)

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
                     dtype='int32',
                     chunks=lineShape)

        # create "image" normalized
        self.imageNorm = self.fileResult.create_dataset(
                     'data_norm',
                     shape=(self.cols, self.rows, self.imageDeep),
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
            idx = 1
            if(fileName):
                prefix = fileName.split('.')[0]
                while os.path.exists('%s_%s%d_%04d_norm.mca' % (prefix,
                                                                self.dxpType,
                                                                self.ch, idx)):
                    idx += 1
                fileName = '%s_%s%d_%04d_norm.mca' % \
                           (prefix, self.dxpType, self.ch, idx)
                np.savetxt(fileName, result, fmt='%f')

        else:
            self.imageNorm[self.col, self.row, :] = result
