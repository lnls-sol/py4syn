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
        self.keithley = Device(pvName+':', 
                               ('GetAHEAT', 'GetAHeaterRange', 'GetAPIDD', 'GetAPIDI', 'GetAPIDP',
                                'GetASetPoint', 'GetBHEAT', 'GetBHeaterRange', 'GetBPIDD', 'GetBPIDI',
                                'GetBPIDP', 'GetBSetPoint', 'GetCTempA', 'GetCTempB', 'GetKTempA', 
                                'GetKTempB', 'SetAHeaterRange', 'SetAPIDD', 'SetAPIDI', 'SetAPIDP', 
                                'SetASetPoint', 'SetBHeaterRange', 'SetBPIDD', 'SetBPIDI', 'SetBPIDP',
                                'SetBSetPoint'))
        self.control_setAPID = PV(pvName + ':CONTROL:SetAPID')
        self.control_setBPID = PV(pvName + ':CONTROL:SetBPID')
        self.control_trigger = PV(pvName + ':CONTROL:Trigger')

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
