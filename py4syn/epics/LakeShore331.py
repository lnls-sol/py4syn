"""LakeShore331 temperature controller class

Python class for LakeShore 331 temperature controllers

:platform: Unix
:synopsis: Python class for LakeShore 331 temperature controllers

.. moduleauthor:: Douglas Bezerra Beniz <douglas.beniz@lnls.br>
    .. note:: 08/12/2015 [douglas.beniz]  first version released
"""
from epics import Device, ca

from py4syn.epics.StandardDevice import StandardDevice

class ControoLoopMode_t(Enum):
    """
    Enumeration of Control Loop Modes.
    """
    CLM_Manual_PID   = 1
    CLM_Zone         = 2
    CLM_OpenLoop     = 3
    CLM_AutoTune_PID = 4
    CLM_AutoTune_PI  = 5
    CLM_AutoTune_P   = 6


class LakeShore331(StandardDevice):
    """
    Class to control LakeShore 331 temperature controllers (cryogenic sensors and instrumentation) via EPICS.
    """

    def __init__(self, pvName, mnemonic):
        StandardDevice.__init__(self, mnemonic)
        # Gets for A and B PID (individually)
        self.pvGetAPIDD = PV(pvName+":GetAPIDD")
        self.pvGetAPIDI = PV(pvName+":GetAPIDI")
        self.pvGetAPIDP = PV(pvName+":GetAPIDP")
        self.pvGetBPIDD = PV(pvName+":GetBPIDD")
        self.pvGetBPIDI = PV(pvName+":GetBPIDI")
        self.pvGetBPIDP = PV(pvName+":GetBPIDP")
        # Sets for A and B PID (individually)
        self.pvSetAPIDD = PV(pvName+":SetAPIDD")
        self.pvSetAPIDI = PV(pvName+":SetAPIDI")
        self.pvSetAPIDP = PV(pvName+":SetAPIDP")
        self.pvSetBPIDD = PV(pvName+":SetBPIDD")
        self.pvSetBPIDI = PV(pvName+":SetBPIDI")
        self.pvSetBPIDP = PV(pvName+":SetBPIDP")
        # Gets for A and B Temperature in Celsius and in Kelvin
        self.pvGetCTempA = PV(pvName+":GetCTempA")
        self.pvGetCTempB = PV(pvName+":GetCTempB")
        self.pvGetKTempA = PV(pvName+":GetKTempA")
        self.pvGetKTempB = PV(pvName+":GetKTempB")
        # Gets for A and B setpoints
        self.pvGetASetPoint = PV(pvName+":GetASetPoint")
        self.pvGetBSetPoint = PV(pvName+":GetBSetPoint")
        # Sets for A and B setpoints
        self.pvSetASetPoint = PV(pvName+":SetASetPoint")
        self.pvSetBSetPoint = PV(pvName+":SetBSetPoint")
        # Get Heater output
        self.pvGetHEATER = PV(pvName+":GetHEATER")
        # Get CMode (Control Loop Mode)
        self.pvGetCmode = PV(pvName+":GetCmode")
        # Set CMode (Control Loop Mode)
        self.pvSetCmode = PV(pvName+":SetCmode")
        # Get Heater range
        self.pvGetHeaterRange = PV(pvName+":GetHeaterRange")
        # Set Heater range
        self.pvSetHeaterRange = PV(pvName+":SetHeaterRange")

    # PIDs Gets and Sets for A channel
    def getAPIDD (self):
        return self.pvGetAPIDD.get()

    def setAPIDD (self, PIDDerivative):
        self.pvGetAPIDD.put(PIDDerivative, wait=True)

    def getAPIDI (self):
        return self.pvGetAPIDI.get()

    def setAPIDI (self, PIDIntegral):
        self.pvGetAPIDI.put(PIDIntegral, wait=True)

    def getAPIDP (self):
   	    return self.pvGetAPIDP.get()

    def setAPIDP (self, PIDProportional):
        self.pvGetAPIDP.put(PIDProportional, wait=True)

    # PIDs Gets and Sets for B channel
    def getBPIDD (self):
        return self.pvGetBPIDD.get()

    def setBPIDD (self, PIDDerivative):
        self.pvGetBPIDD.put(PIDDerivative, wait=True)

    def getBPIDI (self):
        return self.pvGetBPIDI.get()

    def setBPIDI (self, PIDIntegral):
        self.pvGetBPIDI.put(PIDIntegral, wait=True)

    def getBPIDP (self):
   	    return self.pvGetBPIDP.get()

    def setBPIDP (self, PIDProportional):
        self.pvGetBPIDP.put(PIDProportional, wait=True)

    # Temperatures Gets in Celsious and in Kelvin for A and B Channels
    def getCTempA (self):
        return self.pvGetCTempA.get()

    def getCTempB (self):
        return self.pvGetCTempB.get()

    def getKTempA (self):
        return self.pvGetKTempA.get()

    def getKTempB (self):
        return self.pvGetKTempB.get()

    # Get Setpoints for A and B Channesls
    def getASetPoint(self):
        return self.pvGetASetPoint.get()
    
    def getBSetPoint(self):
        return self.pvGetBSetPoint.get()

    # Set Setpoints for A and B Channesls
    def setASetPoint(self, setpoint):
        self.pvSetASetPoint.put(setpoint, wait=True)
    
    def setBSetPoint(self):
        self.pvSetBSetPoint.put(setpoint, wait=True)

    # Get Heater output
    def getHeater(self):
    	return (self.pvGetHEATER.get())

    # Get Control Loop Mode
    def getCMode(self):
    	return self.pvGetCmode.get()

    # Set CMode (Control Loop Mode)
    def setCMode(self, cmode):
        self.pvSetCmode.put(cmode, wait=True)

    # Get Heater range
    def getHeaterRange(self):
    	return self.pvGetHeaterRange.get()
    # Set Heater range
    def setHeaterRange(self, heaterRange):
        self.pvSetHeaterRange.put(heaterRange)
