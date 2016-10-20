"""Spectro Class

Python Class for EPICS Spectro Control.

:platform: Unix
:synopsis: Python Class for EPICS Spectro control.

.. moduleauthor:: Gabriel Fedel <gabirel.fedel@lnls.br>
    .. note:: /06/2016 [gabrielfedel]  first version released
"""
from epics import PV, ca
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable

class Dxp(StandardDevice, ICountable):

    def onValChange(self, value, **kw):
        self._counting = value

    #CONSTRUCTOR OF DXP CLASS
    def __init__(self, pvDxpName="", dxpType="mca", detectors = 4, mnemonic=""):
        StandardDevice.__init__(self, mnemonic)
        self._counting = False

        # determines the exposition time (live time)
        self.pvDxpTime = PV(pvDxpName+":PresetLive.VAL")
        # determines the start of counting
        self.pvDxpEraseStart = PV(pvScalerDxpName+":EraseStart.VAL")
        # determines mode of counting (Live Time, Real Time, ...)
        self.pvDxpPresetMode = PV(pvScalerDxpName+":PresetMode.VAL")
        # TODO:maybe this is not necessary
        self.pvDxpStop = PV(pvScalerDxpName+":StopAll.VAL")
        # store all detectors
        self.pvDxpDetectors = []
        for d in range(1,detectors+1):
            self.pvDxpDetectors.append(PV(pvScalerDxpName+":"+dxpType+d))

        #TODO: verify if onValchange is working correctly
        self.pvDxpAcquiring = PV(pvScalerDxpName+":Aqcquiring",onValChange)
        self.detectors = 4
        self.dxpType = dxpType

#        self.pvScalerTP = PV(pvScalerName+".TP") # envia para o IOC do cintilador o tempo de exposicao

#        self.pvScalerCNT = PV(pvScalerName+".CNT") # envia para o IOC o disparo da medida
#        self.pvScalerFREQ = PV(pvScalerName+".FREQ")                
#        self.pvScalerVAL = PV(pvScalerName+".VAL", self.onValChange) 

#        if(self.pvScalerCNT.get() == 0 and self.pvScalerVAL.get() == 0):
#            self._counting = False

#        for i in range(1,2+numberOfChannels):
#            self.pvScalerCounters.append(PV(pvScalerName+".S"+str(i), auto_monitor=False)) # valor do contador i
 #           self.pvScalerGates.append(PV(pvScalerName+".G"+str(i)))
 #           self.pvScalerPresets.append(PV(pvScalerName+".PR"+str(i)))

#    def setPresetValue(self, channel, v):
#        for g in self.pvScalerGates:
#            g.put(0)
#        for pr in self.pvScalerPresets:
#            pr.put(0)

#        self.pvScalerPresets[channel-1].put(v)
         

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

#        for g in self.pvScalerGates:
#            g.put(0)
#        for pr in self.pvScalerPresets:
#            pr.put(0)
            
#        self.pvScalerGates[0].put(1)
#        self.pvScalerTP.put(time)

    def getCountTime(self):
        return self.pvDxpTime.get()

    def setCountStart(self):
        self._counting = True
        self.pvDxpEraseStart.put(1)
#        self.pvScalerVAL.put(0)
#        self.pvScalerCNT.put(1)

    def setCountStop(self):
        self.pvDxpStop.put(1)
#        self.pvScalerCNT.put(0)
#        self.pvScalerVAL.put(1)

    def getIntensity(self, channel=1):
        return self.pvDxpDetectors[channel].get()
#        return self.pvScalerCounters[channel-1].get()

    def getIntensityInTime(self, time, channel=2):
        self.setCountTime(time)
        self.setCountStart()
        self.wait()
        return self.getIntensity(channel)

#        self.setCountTime(tempoMedida)
#        self.setCountStart()
#        self.wait()
#        self.setCountStop()
#        return self.getIntensity(channel)

    def isCountRunning(self):
        return (self.pvDxpAcquiring.get())

    def wait(self):
        while(self._counting):
            ca.poll()

    def getIntensityCheck(self):
        self.setCountStart()
        self.wait()
        return self.getIntensity()

    def canMonitor(self):
        return True

    def canStopCount(self):
        return True

    def getValue(self, **kwargs):
        if(kwargs):
            return self.getIntensity(kwargs['channel'])
        return self.getIntensity()

    def isCounting(self):
        return self._counting

    def startCount(self):
        self.setCountStart()

    def stopCount(self):
        self.setCountStop()