"""Dxp Class

Python Class for EPICS Dxp Control.

:platform: Unix
:synopsis: Python Class for EPICS Spectro control.

.. moduleauthor:: Gabriel Fedel <gabriel.fedel@lnls.br>
    .. note:: /06/2016 [gabrielfedel]  first version released
"""
from epics import PV, ca
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
import numpy as np


class Dxp(StandardDevice, ICountable):

    def onValChange(self, value, **kw):
        self._counting = value

    # CONSTRUCTOR OF DXP CLASS
    def __init__(self, pvDxpName="", dxpType="mca", channels=4, mnemonic="",numberOfRois=32 ):
        StandardDevice.__init__(self, mnemonic)
        self._counting = False

        # determines the exposition time (live time)
        self.pvDxpTime = PV(pvDxpName+":PresetLive.VAL")
        # determines the start of counting
        self.pvDxpEraseStart = PV(pvDxpName+":EraseStart.VAL")
        # determines mode of counting (Live Time, Real Time, ...)
        self.pvDxpPresetMode = PV(pvDxpName+":PresetMode.VAL")
        # TODO:maybe this is not necessary
        self.pvDxpStop = PV(pvDxpName+":StopAll.VAL")
        # store all channels
        self.pvDxpChannels = []
        # store ROIs
        self.pvDxpRois = []
        for c in range(1, channels+1):
            self.pvDxpChannels.append(PV(pvDxpName+":"+dxpType+c))
            self.pvDxpRois.append([])
            # storeing each ROI in your channel
            for r in range(0,numberOfRois):
                self.pvDxpRois[c-1].append(PV(pvDxpName+":"+dxpType+c+'.R'+r))

        # TODO: verify if onValchange is working correctly
        self.pvDxpAcquiring = PV(pvDxpName+":Acquiring", self.onValChange)
        self.channels = channels
        self.dxpType = dxpType


    def setCountTime(self, time):
        """
        Method to set the count time of a scaler device.

        Parameters
        ----------
        t : value
            Count time to set to scaler device .

        Returns
        -------
        out : None
        """
        self.pvDxpTime.put(time)


    def getCountTime(self):
        return self.pvDxpTime.get()

    def setCountStart(self):
        self._counting = True
        # TODO: testar para verificar qual melhor maneira, utilizando EraseStart ou caget
        self.pvDxpEraseStart.put(1)

    def setCountStop(self):
        self.pvDxpStop.put(1)

    def getIntensity(self, channel = 1, asnumpy = True):
        '''Return intensity
        channel is on format mcaC.Rr, where C is  the channel and
        r is the ROI'''
        return self.pvDxpChannels[channel].get(as_numpy = asnumpy)
#        return self.pvScalerCounters[channel-1].get()

    def getIntensityInTime(self, time, channel=2):
        self.setCountTime(time)
        self.setCountStart()
        self.wait()
        return self.getIntensity(channel)

    def isCountRunning(self):
        return (self.pvDxpAcquiring.get())

    def wait(self):
        while(self._counting):
            ca.poll()

    def canMonitor(self):
        return True

    def canStopCount(self):
        return True

    def getValue(self, **kwargs):
         """
        This is a dummy method that always returns zero, which is part of the
        :class:`py4syn.epics.ICountable` interface. Dxo does not return
        a value while scanning. Instead, it stores a mca file with reult .
        """
       return 0

    def isCounting(self):
        return self._counting

    def startCount(self):
        self.setCountStart()

    def stopCount(self):
        self.setCountStop()

    def setPresetValue(self, channel, val):
        pass
