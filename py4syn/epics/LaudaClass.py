"""Lauda Class

Python Class for EPICS Lauda

:platform: Unix
:synopsis: Python Class for EPICS Lauda 

.. moduleauthor:: Henrique Ferreira Canova <henrique.canova@lnls.br>
    .. note:: 31/03/2014 [henrique.canova]  first version released
"""

from epics import PV
from time import sleep
from py4syn.epics.StandardDevice import StandardDevice

class Lauda(StandardDevice):
    """
    Python class to help configuration and control of Lauda devices via Hyppie over EPICS.

    Examples
    --------
    >>> from py4syn.epics.LaudaClass import Lauda
    >>> lauda = Lauda("TEST:LAUDA", 'lauda1')
    >>> lauda.changeSetPoint(20)
    >>> lauda.start()
    >>> lauda.getInternalTemp()
    >>>
    """

    def __init__ (self,pvPrefix="", mnemonic=""):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`
        
        Parameters
        ----------
        pvPrefix : `string`
            Lauda's device base naming of the PV (Process Variable)
        mnemonic : `string`
            Lauda's mnemonic
        """
        StandardDevice.__init__(self, mnemonic)
        self.pvBTemp = PV(pvPrefix + ":BTEMP")
        self.pvETemp = PV(pvPrefix + ":ETEMP")
        self.pvBLevel = PV(pvPrefix+ ":BLEVEL")
        self.pvBSP = PV(pvPrefix+":BSP")
        self.pvBPower = PV(pvPrefix+":BPOWER") 
        self.pvBOverTemp = PV(pvPrefix+":BOVERTEMP")
        self.pvBTN = PV(pvPrefix+":BTN")
        self.pvBStatus = PV(pvPrefix + ":BSTATS")
        self.pvBThermoStatus = PV(pvPrefix + ":BTHERMOSTATS")
        self.pvWSP = PV(pvPrefix + ":WSP")
        self.pvWPump = PV(pvPrefix + ":WPUMP")
        self.pvWTN = PV(pvPrefix + ":WTN")
        self.pvWStart = PV(pvPrefix + ":WSTART")
        self.pvWStop = PV(pvPrefix + ":WSTOP")

    def getInternalTemp(self):
        return self.pvBTemp.get() 
    def getExternalTemp(self):
        return self.pvETemp.get()
    def getLevel(self):
        return self.pvBLevel.get()
    def getSetPoint(self):
        return self.pvBSP.get()
    def getPower(self):
        return self.pvBPower.get()
    def getOverTemp(self):
        return self.pvBOverTemp.get()
    def getTN(self):
        return self.pvBTN.get()
    def getStatus(self):
        return self.pvBStatus.get()
    def getThermoStatus(self):
        return self.pvBThermoStatus.get()


    def changeSetPoint(self,val):
        self.pvWSP.put(val)
    def changePump(self,val):
        self.pvWPump.put(val)
    def changeTN(self,val):
        self.pvWTN.put(val)

    def start(self,val):
        self.pvWStart.put(val)
    def stop(self,val):
        self.pvWStop.put(val)
  



