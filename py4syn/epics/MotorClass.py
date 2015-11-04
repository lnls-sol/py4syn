"""Motor Class

Python class using basic Motor Record fields.

:platform: Unix
:synopsis: Python Class for EPICS Motor control

.. moduleauthor:: Hugo Slepicka <hugo.slepicka@lnls.br>
.. moduleauthor:: Henrique Ferreira Canova <henrique.canova@lnls.br>

"""
from epics import PV, Device, ca
from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice

class Motor(IScannable, StandardDevice):
    """
    Class to control motor devices via EPICS.

    Examples
    --------
    >>> from py4syn.epics.MotorClass import Motor
    >>>    
    >>> def createMotor(pvName="", mne=""):
    ...    
    ...    new_motor = ''
    ...    
    ...    try:
    ...        new_motor = Motor(pvName, mne)
    ...            print "Motor " + pvName + " created with success!"
    ...    except Exception,e:
    ...        print "Error: ",e
    ...    
    ...    return new_motor
    """

    def onStatusChange(self, value, **kw):
        self._moving = not value

    def __init__(self, pvName, mnemonic):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`
        
        Parameters
        ----------
        pvName : `string`
            Motor's base naming of the PV (Process Variable)
        mnemonic : `string`
            Motor's mnemonic
        """
        StandardDevice.__init__(self, mnemonic)
        self.pvName = pvName

        self.pvType = PV(pvName+".RTYP", connection_timeout=3)

        if(self.pvType.status == None):
            raise Exception("Epics PV "+ pvName+" seems to be offline or not reachable")

        if(self.pvType.get()!= "motor"):
            raise Exception(pvName+" is not an Epics Motor")
            

        self.motor = Device(pvName+'.', ('RBV','VAL', 'DRBV', 'DVAL','RLV', 'RVAL', 'RRBV',
                                         'STOP','MOVN','LLS','HLS','SSET','SUSE',
                                         'SET','VELO','EGU','DMOV','STUP', 'DESC',
                                         'BDST', 'HLM', 'LLM', 'DHLM', 'DLLM',
                                         'VOF','FOF','OFF', 'DIR','LVIO', 'HOMF', 'HOMR'))

        self.motor.add_callback('DMOV',self.onStatusChange)
        self._moving = self.isMovingPV()
        
        self.motorDesc = self.getDescription()

    def __str__(self):
        return self.getMnemonic() + "("+self.pvName+")"

    def getDirection(self):
        """
        Read the motor direction based on the `DIR` (User Direction) field of
        Motor Record

        Returns
        -------
        `integer`

        .. note::
            0. Positive direction;
            1. Negative direction.
        """
        return self.motor.get('DIR')

    def isMovingPV(self):
        """
        Check if a motor is moving or not from the PV

        Returns
        -------
        `boolean`

        .. note::
            - **True**  -- Motor is moving;
            - **False** -- Motor is stopped.
        """

        return (self.motor.get('DMOV') == 0)

    def isMoving(self):
        """
        Check if a motor is moving or not based on the callback

        Returns
        -------
        `boolean`

        .. note::
            - **True** -- Motor is moving;
            - **False** -- Motor is stopped.
        """

        return self._moving

    def isAtLowLimitSwitch(self):
        """
        Check if a motor low limit switch is activated, based on the `LLS` (At
        Low Limit Switch) field of Motor Record

        Returns
        -------
        `boolean`

        .. note::
            - **True** -- Motor is at Low Limit;
            - **False** -- Motor is **NOT** at Low Limit.
        """

        return self.motor.get('LLS')

    def isAtHighLimitSwitch(self):
        """
        Check if a motor high limit switch is activated, based on the `HLS`
        (At High Limit Switch) field of Motor Record

        Returns
        -------
        `boolean`

        .. note::
            - **True** -- Motor is at High Limit;
            - **False** -- Motor is **NOT** at High Limit.
        """

        return self.motor.get('HLS')

    def getDescription(self):
        """
        Read the motor descrition based on the `DESC` field of Motor Record

        Returns
        -------
        `string`
        """

        return self.motor.get('DESC')

    def getHighLimitValue(self):
        """
        Read the motor high limit based on the `HLM` (User High Limit) field of
        Motor Record

        Returns
        -------
        `double`
        """

        return self.motor.get('HLM')

    def getLowLimitValue(self):
        """
        Read the motor low limit based on the `LLM` (User Low Limit) field of
        Motor Record

        Returns
        -------
        `double`
        """

        return self.motor.get('LLM')

    def getDialHighLimitValue(self):
        """
        Read the motor dial high limit based on the `DHLM` (Dial High Limit)
        field of Motor Record

        Returns
        -------
        `double`
        """

        return self.motor.get('DHLM')

    def getDialLowLimitValue(self):
        """
        Read the motor dial low limit based on the `DLLM` (Dial Low Limit)
        field of Motor Record

        Returns
        -------
        `double`
        """

        return self.motor.get('DLLM')

    def getBacklashDistanceValue(self):
        """
        Read the motor backlash distance based on the `BDST` (Backlash Distance,
        `EGU`) field of Motor Record

        Returns
        -------
        `double`
        """

        return self.motor.get('BDST')

    def getVariableOffset(self):
        """
        Read the motor variable offset based on the `VOF` (Variable Offset)
        field of Motor Record

        Returns
        -------
        `integer`
        """

        return self.motor.get('VOF')

    def getFreezeOffset(self):
        """
        Read the motor freeze offset based on the `FOF` (Freeze Offset) field
        of Motor Record

        Returns
        -------
        `integer`
        """

        return self.motor.get('FOF')

    def getOffset(self):
        """
        Read the motor offset based on the `OFF` (User Offset, `EGU`) field of
        Motor Record

        Returns
        -------
        `string`
        """

        return self.motor.get('OFF')

    def getRealPosition(self):
        """
        Read the motor real position based on the `RBV` (User Readback Value)
        field of Motor Record

        Returns
        -------
        `double`
        """

        return self.motor.get('RBV')


    def getDialRealPosition(self):
        """
        Read the motor DIAL real position based on the `DRBV` (Dial Readback
        Value) field of Motor Record

        Returns
        -------
        `double`
        """

        return self.motor.get('DRBV')

    def getDialPosition(self):
        """
        Read the motor target DIAL position based on the `DVAL` (Dial Desired
        Value) field of Motor Record

        Returns
        -------
        `double`
        """

        return self.motor.get('DVAL')

    def getRawPosition(self):
        """
        Read the motor RAW position based on the `RVAL` (Raw Desired Value)
        field of Motor Record

        Returns
        -------
        `double`
        """

        return self.motor.get('RVAL')

    def setRawPosition(self, position):
        """
        Sets the motor RAW position based on the `RVAL` (Raw Desired Value)
        field of Motor Record

        Returns
        -------
        `double`
        """
        self._moving = True
        self.motor.put('RVAL', position)

        ca.poll(evt=0.05)

    def getRawRealPosition(self):
        """
        Read the motor RAW real position based on the `RRBV` (Raw Readback Value)
        field of Motor Record

        Returns
        -------
        `double`
        """

        return self.motor.get('RRBV')

    def getPosition(self):
        """
        Read the motor target position based on the `VAL` (User Desired Value)
        field of Motor Record

        Returns
        -------
        `double`
        """

        return self.motor.get('VAL')

    def getEGU(self):
        """
        Read the motor engineering unit based on the `EGU` (Engineering Units)
        field of Motor Record

        Returns
        -------
        `string`
        """

        return self.motor.get('EGU')

    def getLVIO(self):
        """
        Read the motor limit violation `LVIO` (Limit Violation) field of
        Motor Record

        Returns
        -------
        `short`
        """

        return self.motor.get('LVIO')

    def setEGU(self, unit):
        """
        Set the motor engineering unit to the `EGU` (Engineering Units) field
        of Motor Record

        Parameters
        ----------
        unit : `string`
            The desired engineering unit.

            .. note::
                **Example:** "mm.", "deg."
        """

        return self.motor.set('EGU', unit)

    def setHighLimitValue(self, val):
        """
        Set the motor high limit based on the `HLM` (User High Limit) field of
        Motor Record

        Parameters
        ----------
        val : `double`
            The desired value to set
        """

        self.motor.put('HLM', val)

    def setLowLimitValue(self, val):
        """
        Set the motor low limit based on the `LLM` (User Low Limit) field of
        Motor Record

        Parameters
        ----------
        val : `double`
            The desired value to set
        """

        self.motor.put('LLM', val)

    def setDialHighLimitValue(self, val):
        """
        Set the motor dial high limit based on the `DHLM` (Dial High Limit)
        field of Motor Record

        Parameters
        ----------
        val : `double`
            The desired value to set
        """

        self.motor.put('DHLM', val)

    def setDialLowLimitValue(self, val):
        """
        Set the motor dial low limit based on the `DLLM` (Dial Low Limit)
        field of Motor Record

        Parameters
        ----------
        val : `double`
            The desired value to set
        """

        self.motor.put('DLLM', val)

    def setSETMode(self):
        """
        Put the motor in SET mode

        .. note::
            Motor will **NOT** move until it is in in **USE mode**
        """

        self.motor.put('SSET', 1, wait=True)

    def setUSEMode(self):
        """
        Put the motor in **USE mode**
        """

        self.motor.put('SUSE', 1, wait=True)


    def setVariableOffset(self, val):
        """
        Set the motor variable offset based on the `VOF` (Variable Offset)
        field of Motor Record

        Parameters
        ----------
        val : `integer`
            The desired value to set
        """

        self.motor.put('VOF', val)

    def setFreezeOffset(self, val):
        """
        Set the motor freeze offset based on the `FOF` (Freeze Offset) field
        of Motor Record

        Parameters
        ----------
        val : `integer`
            The desired value to set
        """

        self.motor.put('FOF', val)

    def setOffset(self, val):
        """
        Set the motor offset based on the `OFF` (User Offset, `EGU`) field of
        Motor Record

        Parameters
        ----------
        val : `double`
            The desired value to set
        """

        self.motor.put('OFF', val)

    def setDialPosition(self, pos, waitComplete=False):
        """
        Set the motor target DIAL position based on the `DVAL` (Dial Desired
        Value) field of Motor Record

        Parameters
        ----------
        pos : `double`
            The desired position to set
        waitComplete : `boolean` (default is **False**)
            .. note::
                If **True**, the function will wait until the movement finish
                to return, otherwise don't.
        """

        if(self.getDialRealPosition() == pos):
            return

        self.motor.put('DVAL', pos)
        self._moving = True
        if(waitComplete):
            self.wait()

    def setAbsolutePosition(self, pos, waitComplete=False):
        """
        Move the motor to an absolute position received by an input parameter

        Parameters
        ----------
        pos : `double`
            The desired position to set
        waitComplete : `boolean` (default is **False**)
            .. note::
                If **True**, the function will wait until the movement finish
                to return, otherwise don't.
        """

        if(self.getRealPosition() == pos):
            return

        ret, msg = self.canPerformMovement(pos)
        if(not ret):
            raise Exception("Can't move motor "+self.motorDesc+" ("+self.pvName+") to desired position: "+str(pos)+ ", " + msg)

        self._moving = True
        self.motor.put('VAL',pos)

        ca.poll(evt=0.05)

        if(waitComplete):
            self.wait()

    def setRelativePosition(self, pos, waitComplete=False):
        """
        Move the motor a distance, received by an input parameter, to a position
        relative to that current one

        Parameters
        ----------
        pos : `double`
            The desired distance to move based on current position
        waitComplete : `boolean` (default is **False**)
            .. note:
                If **True**, the function will wait until the movement finish
                to return, otherwise don't.
        """
        if(pos == 0):
            return

        ret, msg = self.canPerformMovement(self.getRealPosition()+pos)
        if(not ret):
            raise Exception("Can't move motor "+self.motorDesc+" ("+
                            self.pvName+") to desired position: "+
                            str(self.getRealPosition()+pos)+ ", " + msg)

        self.motor.put('RLV',pos)

        ca.poll(evt=0.05)

        self._moving = True
        if(waitComplete):
            self.wait()

    def setVelocity(self, velo):
        """
        Set the motor velocity up based on the `VELO` (Velocity, EGU/s) field
        from Motor Record

        Parameters
        ----------
        velo : `double`
            The desired velocity to set
        """

        self.motor.put('VELO',velo)

    def setAcceleration(self, accl):
        """
        Set the motor acceleration time based on the `ACCL` (Seconds to
        Velocity) field from Motor Record

        Parameters
        ----------
        accl : `double`
            The desired acceleration to set
        """

        self.motor.put('ACCL',accl)

    def setUpdateRequest(self,val):
        """
        Set the motor update request flag based on the `STUP` (Status Update
        Request) field from Motor Record

        Parameters
        ----------
        val : `integer`
            The desired value to set for the flag
        """

        self.motor.put('STUP',val)

    def validateLimits(self):
        """
        Verify if motor is in a valid position.  In the case it has been reached
        the HIGH or LOW limit switch, an exception will be raised.
        """
        message = ""
        if(self.isAtHighLimitSwitch()):
            message = 'Motor: '+self.motorDesc+' ('+self.pvName+') reached the HIGH limit switch.'
        elif(self.isAtLowLimitSwitch()):
            message = 'Motor: '+self.motorDesc+' ('+self.pvName+') reached the LOW limit switch.'
        if(message != ""):
            raise Exception(message)

    def canPerformMovement(self, target):
        """
        Check if a movement to a given position is possible using the limit
        values and backlash distance

        Returns
        -------
        `boolean`

        .. note::
            - **True** -- Motor CAN perform the desired movement;
            - **False** -- Motor **CANNOT** perform the desired movement.
        """
        # Moving to high limit
        if(target > self.getRealPosition()):
            if(self.isAtHighLimitSwitch()):
                return False, "Motor at high limit switch"
        # Moving to low limit
        else:
            if(self.isAtLowLimitSwitch()):
                return False, "Motor at low limit switch"

        if(self.getLVIO()==0):
            return True, ""
        
        return False, "Movement beyond soft limits"

    def canPerformMovementCalc(self, target):
        """
        Check if a movement to a given position is possible using the limit
        values and backlash distance calculating the values

        Returns
        -------
        `boolean`

        .. note::
            - **True** -- Motor CAN perform the desired movement;
            - **False** -- Motor **CANNOT** perform the desired movement.
        """
        
        if self.getHighLimitValue() == 0.0 and self.getLowLimitValue() == 0.0:
                return True
        
        backlashCalc = self.calculateBacklash(target)

        if(self.getDirection()==0):
        
            if(backlashCalc > 0):
                vFinal = target - backlashCalc
            else:
                vFinal = target + backlashCalc
        else:
            if(backlashCalc > 0):
                vFinal = target + backlashCalc
            else:
                vFinal = target - backlashCalc

        if(target > self.getRealPosition()):
            if(self.isAtHighLimitSwitch()):
                return False

            if vFinal <= self.getHighLimitValue():
                return True
            
        # Moving to low limit
        else:
            if(self.isAtLowLimitSwitch()):
                return False

            if vFinal >= self.getLowLimitValue():
                return True
            
        return False

    def calculateBacklash(self, target):
        """
        Calculates the backlash distance of a given motor

        Returns
        -------
        `double`

        """

        # Positive Movement
        if(self.getDirection() == 0):
            if(self.getBacklashDistanceValue() > 0 and target < self.getRealPosition()) or (self.getBacklashDistanceValue() < 0 and target > self.getRealPosition()):
                return self.getBacklashDistanceValue()
        else:
            if(self.getBacklashDistanceValue() > 0 and target > self.getRealPosition()) or (self.getBacklashDistanceValue() < 0 and target < self.getRealPosition()):
                return self.getBacklashDistanceValue()
        return 0    

    def stop(self):
        """
        Stop the motor
        """
        self.motor.put('STOP',1)

    def wait(self):
        """
        Wait until the motor movement finishes
        """
        while(self._moving):
            ca.poll(evt=0.01)
            
    def getValue(self):
        """
        Get the current position of the motor.
        See :class:`py4syn.epics.IScannable`

        Returns
        -------
        `double`
            Read the current value (Motor Real Position)
        """

        return self.getRealPosition()
        
    def setValue(self, v):
        """
        Set the desired motor position.
        See :class:`py4syn.epics.IScannable`

        Parameters
        ----------
        v : `double`
            The desired value (Absolute Position) to set 
        """
        self.setAbsolutePosition(v)

    def homeForward(self):
        """
        Move the motor until it hits the forward limit switch or the software limit.
        """
        self._moving = True
        self.motor.put('HOMF', 1)

    def homeReverse(self):
        """
        Move the motor until it hits the reverse limit switch or the software limit.
        """
        self._moving = True
        self.motor.put('HOMR', 1)
