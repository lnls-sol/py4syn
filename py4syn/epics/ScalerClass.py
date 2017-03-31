"""Scaler Class

Python Class for EPICS Scaler control.

:platform: Unix
:synopsis: Python Class for EPICS Scaler control.

.. moduleauthor:: Hugo Henrique Slepicka <hugo.slepicka@lnls.br>
    .. note:: 30/06/2012 [hugo.slepicka]  first version released
    .. note:: 31/03/2014 [hugo.slepicka]  support for more than one channel
    .. note:: 07/04/2014 [hugo.slepicka]  fix to read the correct values after
                                    count, based on Tim Mooney's recommendation
"""
from epics import PV, ca
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
from time import sleep

class Scaler(StandardDevice, ICountable):


    #CALLBACK FUNCTION FOR THE MOTOR STATUS PV
    #def onStatusChange(self, value, **kw):
    #    self._counting = (value == 1)

    def onValChange(self, value, **kw):
        self._counting = (value == 0)

    #CONSTRUCTOR OF SHUTTER CLASS
    def __init__(self, pvScalerName="", numberOfChannels=1, mnemonic=""):
        StandardDevice.__init__(self, mnemonic)
        self._counting = False
        self.pvScalerTP = PV(pvScalerName+".TP") # envia para o IOC do cintilador o tempo de exposicao
        #self.pvScalerCNT = PV(pvScalerName+".CNT", self.onStatusChange) # envia para o IOC o disparo da medida
        self.pvScalerCNT = PV(pvScalerName+".CNT") # envia para o IOC o disparo da medida
        self.pvScalerFREQ = PV(pvScalerName+".FREQ")                
        self.pvScalerVAL = PV(pvScalerName+".VAL", self.onValChange) 
        self.pvScalerCounters = []
        self.pvScalerGates = []
        self.pvScalerPresets = []
        
        # Initial State
        if(self.pvScalerCNT.get() == 0 and self.pvScalerVAL.get() == 0):
            self._counting = False
            
        for i in range(1,2+numberOfChannels):
            self.pvScalerCounters.append(PV(pvScalerName+".S"+str(i), auto_monitor=False)) # valor do contador i
            self.pvScalerGates.append(PV(pvScalerName+".G"+str(i)))
            self.pvScalerPresets.append(PV(pvScalerName+".PR"+str(i)))

    def setPresetValue(self, channel, v):
        for g in self.pvScalerGates:
            g.put(0)
        for pr in self.pvScalerPresets:
            pr.put(0)
         
        self.pvScalerPresets[channel-1].put(v)
         

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
        for g in self.pvScalerGates:
            g.put(0)
        for pr in self.pvScalerPresets:
            pr.put(0)
            
        self.pvScalerGates[0].put(1)
        self.pvScalerTP.put(time)

    def getCountTime(self):
        return self.pvScalerTP.get()

    def setCountStart(self):
        self._counting = True
        self.pvScalerVAL.put(0)
        self.pvScalerCNT.put(1)

    def setCountStop(self):
        self.pvScalerCNT.put(0)
        self.pvScalerVAL.put(1)

    def getIntensity(self, channel=2):
        return self.pvScalerCounters[channel-1].get()

    def getIntensityInTime(self, tempoMedida, channel=2):
        self.setCountTime(tempoMedida)
        self.setCountStart()
        self.wait()
        self.setCountStop()
        return self.getIntensity(channel)

    def isCountRunning(self):
        return (self.pvScalerVAL.get()== 0)

    def wait(self):
        while(self._counting):
            sleep(0.1)
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
