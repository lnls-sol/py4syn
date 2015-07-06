"""LakeShore 331 Class

Python Class for EPICS LakeShore 331

:platform: Unix
:synopsis: Python Class for EPICS LakeShore 331 

.. moduleauthor:: Douglas Bezerra Beniz <douglas.beniz@lnls.br>
    .. note:: 06/07/2015 [douglas.beniz]  first version released
"""

from epics import PV
from time import sleep
from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice

class LakeShore331 (IScannable, StandardDevice):
    """
    Python class to help configuration and control of LakeShore 331 devices via Hyppie
    over EPICS.

    Examples
    --------
    >>> from py4syn.epics.MotorClass import Motor
    >>>    
    >>> def createMotor(pvName=""):
    ...    
    ...    new_motor = ''
    ...    
    ...    try:
    ...        new_motor = Motor(PV)
    ...            print "Motor " + pvName + " created with success!"
    ...    except Exception,e:
    ...        print "Error: ",e
    ...    
    ...    return new_motor
    """

    def __init__ (self, pvPrefix="", mnemonic=""):
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
        self.lakeshore331 = Device(pvName+':', 
                               ('GetAHEAT', 'GetAHeaterRange', 'GetAPIDD', 'GetAPIDI', 'GetAPIDP',
                                'GetASetPoint', 'GetBHEAT', 'GetBHeaterRange', 'GetBPIDD', 'GetBPIDI',
                                'GetBPIDP', 'GetBSetPoint', 'GetCTempA', 'GetCTempB', 'GetKTempA', 
                                'GetKTempB', 'SetAHeaterRange', 'SetAPIDD', 'SetAPIDI', 'SetAPIDP', 
                                'SetASetPoint', 'SetBHeaterRange', 'SetBPIDD', 'SetBPIDI', 'SetBPIDP',
                                'SetBSetPoint'))
        self.ls331_control = Device(pvName + ':CONTROL:', ['SetAPID', 'SetBPID', 'Trigger'])

    def getAHeat(self):
        """
        Heater output query for A channel.

        Returns
        -------
        Value: Float, e.g.: 0.001

        Examples
        --------
        >>> ls331.getAHeat()
        >>> 51.530
        """

        return self.lakeshore331.get('GetAHEAT')

    def getBHeat(self):
        """
        Heater output query for B channel.

        Returns
        -------
        Value: Float, e.g.: 0.001

        Examples
        --------
        >>> ls331.getBHeat()
        >>> 51.530
        """

        return self.lakeshore331.get('GetBHEAT')

    def getAHeaterRange(self):
        """
        Heater range command for A channel.

        Returns
        -------
        Value: Float, e.g.: 0.001

        Examples
        --------
        >>> ls331.getAHeaterRange()
        >>> 51.530
        """

        return self.lakeshore331.get('GetAHeaterRange')

    def getBHeaterRange(self):
        """
        Heater range command for B channel.

        Returns
        -------
        Value: Float, e.g.: 0.001

        Examples
        --------
        >>> ls331.getBHeaterRange()
        >>> 51.530
        """

        return self.lakeshore331.get('GetBHeaterRange')

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

    def setAHeaterRange(self, heaterRange):
        """
        Heater range command for channel A.
            
        Parameters
        ----------
        heaterRange : `float`
        """

        self.lakeshore331.put('SetAHeaterRange', heaterRange, wait=True)

    def setBHeaterRange(self, heaterRange):
        """
        Heater range command for channel B.
            
        Parameters
        ----------
        heaterRange : `float`
        """

        self.lakeshore331.put('SetBHeaterRange', heaterRange, wait=True)

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
            `float`
        """

        return 0

    def setValue(self, v):
        """
        Sets ...

        Parameters
        ----------
        v : `float`
        """

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

        return 0

    def getHighLimitValue(self):
        """
        Gets ...

        Returns
        -------
            `float`
        """

        return 0
