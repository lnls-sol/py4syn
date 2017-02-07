"""Image HDF Class

Python Class for Save HDF images .

:platform: Unix
:synopsis: Python Class for HDF images.

.. moduleauthor:: Gabriel Fedel <gabriel.fedel@lnls.br>
.. note:: 06/02/2017 [gabrielfedel]  first version released
"""
import numpy as np
import os
import h5py


class ImageHDF():
    # CONSTRUCTOR OF ImageHDF CLASS
    def __init__(self,  numPoints, output, prefix):
        """ Constructor
        prefix: prefix for filenames
        """
        self.numPoints = numPoints
        self.image = None
        self.lastPos = -1
        self.output = output
        self.prefix = prefix
        self.sufix = sufix


    def nameFile(self, output, prefix, sufix):
        '''Generate correct name to file
        output: original fileName
        prefix: added after id
        sufix: extension'''

        start = fileName.split('.')[0]

        idx = 0
        while os.path.exists('%s%s_%04d.%s' % (start, prefix, idx, sufix)):
            idx += 1

        resultName= '%s%s_%04d.%s' % (start, prefix, idx, sufix)

        return resultName

    def saveSpectrum(self, spectrum, snake = True):
        ''' save the spectrum intensity in a mca file if is a point
            or an hdf file if is an image
            snake: if data is collected on snake mode'''
        self.spectrum = spectrum
        # save a unique point
        if self.image is None:
            fileName = self.nameFile(self.output, self.prefix, "mca")
            np.savetxt(fileActual, self.spectrum, fmt='%f')
        else:
            # add a point on hdf file
            self.col = int(self.lastPos/self.rows)
            self.row = self.lastPos - self.rows*self.col
            if snake:
                # if is an odd line
                if (self.col % 2 != 0):
                    self.row = -1*(self.row+1)
            self.image[self.col, self.row, :] = self.spectrum

            self.lastPos += 1

    def startCollectImage(self, dtype, rows=0, cols=0):
        """Start to collect an image
        When collect an image, the points will be  saved on a hdf file"""
        self.rows = rows
        self.cols = cols
        # create HDF file
        fileName = self.nameFile(self.output, self.prefix, "hdf")

        self.fileResult = h5py.File(fileName)

        # TODO: review this
        lineShape = (1, self.rows, self.numPoints)
        self.image = self.fileResult.create_dataset(
                     'data',
                     shape=(self.cols, self.rows, self.numPoints),
                     dtype=dtype,
                     chunks=lineShape)

        # create "image" normalized
        self.imageNorm = self.fileResult.create_dataset(
                     'data_norm',
                     shape=(self.cols, self.rows, self.numPoints),
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
            fileName = self.nameFile(self.output, self.prefix + '_norm', "mca")
            np.savetxt(fileName, result, fmt='%f')

        else:
            self.imageNorm[self.col, self.row, :] = result
