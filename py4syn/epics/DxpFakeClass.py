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
        fileName = self.fileName
        idx = 0
        if(fileName):
            # TODO: change random interval to be defined
            # generate a random spectrum
            spectrum = np.random.randint(100, size=(2048))
            prefix = fileName.split('.')[0]
            while os.path.exists('%s_%s%d_%04d.mca' % (prefix, self.dxpType,
                                                       ch, idx)):
                idx += 1
            fileName = '%s_%s%d_%04d.mca' % \
                       (prefix, self.dxpType, ch, idx)
        np.savetxt(fileName, spectrum, fmt='%f')

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
