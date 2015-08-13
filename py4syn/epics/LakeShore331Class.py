"""LakeShore 331 Class

Python Class for EPICS LakeShore 331

:platform: Unix
:synopsis: Python Class for EPICS LakeShore 331 

.. moduleauthor:: Douglas Bezerra Beniz <douglas.beniz@lnls.br>
    .. note:: 06/07/2015 [douglas.beniz]  first version released
"""

from epics import PV, Device
from enum import Enum
from time import sleep
from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice

class LakeShore_t(Enum):
    """
    Enumeration of LakeShore channels.
    """
    Channel_A = 0       # channel A
    Channel_B = 1       # channel B

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

class LakeShore331 (IScannable, StandardDevice):
    """
    Python class to help configuration and control of LakeShore 331 devices via Hyppie
    over EPICS.

    Examples
    --------
    >>> from py4syn.epics.MotorClass import Motor
    >>>    
    >>> def createMotor(pvPrefix=""):
    ...    
    ...    new_motor = ''
    ...    
    ...    try:
    ...        new_motor = Motor(PV)
    ...            print "Motor " + pvPrefix + " created with success!"
    ...    except Exception,e:
    ...        print "Error: ",e
    ...    
    ...    return new_motor
    """

    def __init__ (self, pvPrefix="", mnemonic="", channel=0):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`
        
        Parameters
        ----------
        pvPrefix : `string`
            LakeShore331's device base naming of the PV (Process Variable); Like DXAS:LS331;
        mnemonic : `string`
            LakeShore331's mnemonic
        """
        StandardDevice.__init__(self, mnemonic)
        self.lakeshore331 = Device(pvPrefix+':', 
                               ('GetHEAT', 'GetHeaterRange', 'GetAPIDD', 'GetAPIDI', 'GetAPIDP',
                                'GetASetPoint', 'GetBPIDD', 'GetBPIDI',
                                'GetBPIDP', 'GetBSetPoint', 'GetCTempA', 'GetCTempB', 'GetKTempA', 
                                'GetKTempB', 'SetHeaterRange', 'SetAPIDD', 'SetAPIDI', 'SetAPIDP', 
                                'SetASetPoint', 'SetBPIDD', 'SetBPIDI', 'SetBPIDP',
                                'SetBSetPoint', 'GetCmode', 'SetCmode'))
        self.ls331_control = Device(pvPrefix + ':CONTROL:', ['SetAPID', 'SetBPID', 'Trigger'])
        
        if (channel == 1):
            self.ls331_channel = LakeShore_t.Channel_B
        else:
            # Default
            self.ls331_channel = LakeShore_t.Channel_A

    def getHeat(self):
        """
        Heater output query

        Returns
        -------
        Value: Float, e.g.: 0.001

        Examples
        --------
        >>> ls331.getHeat()
        >>> 51.530
        """

        return self.lakeshore331.get('GetHEAT')

    def getHeaterRange(self):
        """
        Heater range command.

        Returns
        -------
        Value: Float, e.g.: 0.001

        Examples
        --------
        >>> ls331.getHeaterRange()
        >>> 51.530
        """

        return self.lakeshore331.get('GetHeaterRange')

    def getAPIDD(self):
        """
        Returns Value D of PID for channel A.

        Returns
        -------
        Value: Integer, e.g.: 10

        Examples
        --------
        >>> ls331.getAPIDD()
        >>> 31
        """

        return self.lakeshore331.get('GetAPIDD')

    def getBPIDD(self):
        """
        Returns Value D of PID for channel B.

        Returns
        -------
        Value: Integer, e.g.: 10

        Examples
        --------
        >>> ls331.getBPIDD()
        >>> 32
        """

        return self.lakeshore331.get('GetBPIDD')
    
    def getAPIDI(self):
        """
        Returns Value I of PID for channel A.

        Returns
        -------
        Value: Integer, e.g.: 10

        Examples
        --------
        >>> ls331.getAPIDI()
        >>> 31
        """

        return self.lakeshore331.get('GetAPIDI')

    def getBPIDI(self):
        """
        Returns Value I of PID for channel B.

        Returns
        -------
        Value: Integer, e.g.: 10

        Examples
        --------
        >>> ls331.getBPIDI()
        >>> 32
        """

        return self.lakeshore331.get('GetBPIDI')

    def getAPIDP(self):
        """
        Returns Value P of PID for channel A.

        Returns
        -------
        Value: Integer, e.g.: 10

        Examples
        --------
        >>> ls331.getAPIDP()
        >>> 31
        """

        return self.lakeshore331.get('GetAPIDP')

    def getBPIDP(self):
        """
        Returns Value P of PID for channel B.

        Returns
        -------
        Value: Integer, e.g.: 10

        Examples
        --------
        >>> ls331.getBPIDP()
        >>> 32
        """

        return self.lakeshore331.get('GetBPIDP')


    def getASetPoint(self):
        """
        Returns setpoint value for channel A.

        Returns
        -------
        Value: float, e.g.: 0.001 
        
        Examples
        --------
        >>> ls331.getASetPoint()
        >>> 67.87
        """

        return self.lakeshore331.get('GetASetPoint')

    def getBSetPoint(self):
        """
        Returns setpoint value for channel B.

        Returns
        -------
        Value: float, e.g.: 0.001 
        
        Examples
        --------
        >>> ls331.getBSetPoint()
        >>> 67.87
        """

        return self.lakeshore331.get('GetBSetPoint')

    def getCTempA(self):
        """
        Returns channel A temperature in Celsius degrees.

        Returns
        -------
        Value: float, e.g.: 0.001

        Examples
        --------
        >>> ls331.getCTempA()
        >>> 32.56
        """

        return self.lakeshore331.get('GetCTempA')

    def getCTempB(self):
        """
        Returns channel B temperature in Celsius degrees.

        Returns
        -------
        Value: float, e.g.: 0.001

        Examples
        --------
        >>> ls331.getCTempB()
        >>> 32.56
        """

        return self.lakeshore331.get('GetCTempB')

    def getKTempA(self):
        """
        Returns channel A temperature in Kelvin.

        Returns
        -------
        Value: float, e.g.: 0.001

        Examples
        --------
        >>> ls331.getKTempA()
        >>> 32.56
        """

        return self.lakeshore331.get('GetKTempA')

    def getKTempB(self):
        """
        Returns channel B temperature in Kelvin.

        Returns
        -------
        Value: float, e.g.: 0.001

        Examples
        --------
        >>> ls331.getKTempB()
        >>> 32.56
        """

        return self.lakeshore331.get('GetKTempB')

    def setHeaterRange(self, heaterRange):
        """
        Heater range command.
            
        Parameters
        ----------
        heaterRange : `float`
        """

        self.lakeshore331.put('SetHeaterRange', heaterRange, wait=True)

    def setASetPoint(self, setPoint):
        """
        Set a setpoint value for channel A.
            
        Parameters
        ----------
        setPoint : `float`
        """

        self.lakeshore331.put('SetASetPoint', setPoint, wait=True)

    def setBSetPoint(self, setPoint):
        """
        Set a setpoint value for channel B.
            
        Parameters
        ----------
        setPoint : `float`
        """

        self.lakeshore331.put('SetBSetPoint', setPoint, wait=True)

    def setAPIDD(self, pid_d):
        """
        D parameter value of PID for channel A.
            
        Parameters
        ----------
        pid_d : `integer`
        """

        self.lakeshore331.put('SetAPIDD', pid_d, wait=True)

    def setBPIDD(self, pid_d):
        """
        D parameter value of PID for channel B.
            
        Parameters
        ----------
        pid_d : `integer`
        """

        self.lakeshore331.put('SetBPIDD', pid_d, wait=True)

    def setAPIDI(self, pid_i):
        """
        I parameter value of PID for channel A.
            
        Parameters
        ----------
        pid_i : `integer`
        """

        self.lakeshore331.put('SetAPIDI', pid_i, wait=True)

    def setBPIDI(self, pid_i):
        """
        I parameter value of PID for channel B.
            
        Parameters
        ----------
        pid_i : `integer`
        """

        self.lakeshore331.put('SetBPIDI', pid_i, wait=True)
        
    def setAPIDP(self, pid_p):
        """
        P parameter value of PID for channel A.
            
        Parameters
        ----------
        pid_p : `integer`
        """

        self.lakeshore331.put('SetAPIDP', pid_p, wait=True)

    def setBPIDP(self, pid_p):
        """
        P parameter value of PID for channel B.
            
        Parameters
        ----------
        pid_p : `integer`
        """

        self.lakeshore331.put('SetBPIDP', pid_p, wait=True)

    # Get Control Loop Mode
    def getCMode(self):
    	return self.lakeshore331.get('GetCmode')

    # Set CMode (Control Loop Mode)
    def setCMode(self, cmode):
        self.lakeshore331.put('SetCmode', cmode, wait=True)

    def setControlAPID(self, a_pid):
        """
        PID for channel A.
            
        Parameters
        ----------
        a_pid : `integer`
        """

        self.ls331_control.put('SetAPID', a_pid, wait=True)

    def setControlBPID(self, b_pid):
        """
        PID for channel B.
            
        Parameters
        ----------
        b_pid : `integer`
        """

        self.ls331_control.put('SetBPID', b_pid, wait=True)

    def setControlTrigger(self, trigger):
        """
        Trigger.
            
        Parameters
        ----------
        trigger : `integer`
        """

        self.ls331_control.put('Trigger', trigger, wait=True)

    def getValue(self):
        """
        Returns ...

        Returns
        -------
            `float`, Temperature in Celsius degrees
        """

        if (self.ls331_channel == LakeShore_t.Channel_A):
            return self.getCTempA()
        else:
            return self.getCTempB()

    def setValue(self, temperature):
        """
        Sets ...

        Parameters
        ----------
        temperature : `float`, Temperature in Celsius degrees
        """

        if (self.ls331_channel == LakeShore_t.Channel_A):
            self.setASetPoint(temperature)
        else:
            self.setBSetPoint(temperature)

    def wait(self):
        """
        Wait...
        """

        sleep(0)

    def getLowLimitValue(self):
        """
        Gets ...

        Returns
        -------
            `float`
        """
        # Mininum is 0 K... -272.15 .oC
        return -272.15

    def getHighLimitValue(self):
        """
        Gets ...

        Returns
        -------
            `float`
        """
        # Unsure about maximum... let's put 325 K... 51.85 .oC
        return 51.85

