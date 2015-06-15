"""Pseudo Class

Python class using basic a set of Epics Motor and formulas to create a Pseudo Motor.

:platform: Unix
:synopsis: Python Class for Pseudo Motors control

.. moduleauthor:: Hugo Slepicka <hugo.slepicka@lnls.br>
.. moduleauthor:: Henrique Ferreira Canova <henrique.canova@lnls.br>

"""

from epics import ca
from math import *
import numpy
from py4syn import *
from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics import MotorClass
from py4syn.epics.MotorClass import Motor

class motorTarget():
    """
    Class to globally control virtual Motor targets
    """

    def __init__(self):
        """
        **Constructor**

        Parameters
        ----------
        None
        """
        self.targets = {}

    def __getitem__(self, m):
        """
        Get current value of the virtual Motor positioning

        Parameters
        ----------
        m : `dictionary`
            Represents the device target, virtual Motor, in the `mtrDB` global array of devices

        Returns
        -------
        `double` or `dictionary` item
            Read the current Positioning value of virtual Motor (Real)

            .. note::
                If `m` parameter is received and it is in the targets list, then its
                correspondent target is returned (as a `dictionary` item), otherwise,
                real position of virtual Motor is returned (as
                a `double` value)
        """

        global mtrDB
        if m in self.targets: 
            return self.targets[m]
        return mtrDB[m].getRealPosition()

    def __setitem__(self, m, pos):
        """
        Set a position value to the virtual Motor target received as input parameter 

        Parameters
        ----------
        m : `dictionary`
            Represents the target device, virtual Motor, in the `mtrDB` global array of devices

        pos : `double`
            The desired position to set
        """

        self.targets[m] = pos

    def keys(self):
        """
        Get keys (indexes) of all virtual Motor targets 

        Returns
        -------
        `integer array`
            Read the keys (indexes) from all targets
        """
        return self.targets.keys()

class motorPosition():
    """
    Class to globally control positioning of virtual Motor
    """

    def __getitem__(self, m):
        """
        Get current value of the virtual Motor positionin 

        Parameters
        ----------
        m : `dictionary`
            Represents the device, virtual Motor, in the `mtrDB` global array of devices

        Returns
        -------
        `double`
            Read the current value (virtual Motor Real Position)
        """

        global mtrDB
        return mtrDB[m].getRealPosition()

class motorTargetDial():
    """
    Class to globally control virtual Motor target using Dial fields
    """

    def __init__(self):
        """
        **Constructor**

        Parameters
        ----------
        None
        """
        self.targets = {}

    def __getitem__(self, m):
        """
        Get current value of the virtual Motor positioning using Dial field

        Parameters
        ----------
        m : `dictionary`
            Represents the device target, virtual Motor, in the `mtrDB` global array of devices

        Returns
        -------
        `double` or `dictionary` item
            Read the current Positioning value of virtual Motor (Real)

            .. note::
                If `m` parameter is received and it is in the targets list, then its
                correspondent target is returned (as a `dictionary` item), otherwise,
                real position of virtual Motor, using the Dial field, is returned (as
                a `double` value)
        """

        global mtrDB
        if m in self.targets: 
            return self.targets[m]
        return mtrDB[m].getDialRealPosition()

    def __setitem__(self, m, pos):
        """
        Set a position value to the virtual Motor target received as input parameter 

        Parameters
        ----------
        m : `dictionary`
            Represents the target device, virtual Motor, in the `mtrDB` global array of devices

        pos : `double`
            The desired position to set
        """

        self.targets[m] = pos

    def keys(self):
        """
        Get keys (indexes) of all virtual Motor targets 

        Returns
        -------
        `integer array`
            Read the keys (indexes) from all targets
        """

        return self.targets.keys()

class motorPositionDial():
    """
    Class to globally control positioning of virtual Motor using Dial fields
    """

    def __getitem__(self, m):
        """
        Get current value of the virtual Motor positioning using Dial field

        Parameters
        ----------
        m : `dictionary`
            Represents the device, virtual Motor, in the `mtrDB` global array of devices

        Returns
        -------
        `double`
            Read the current Positioning value of virtual Motor (Real) using
            Dial field
        """

        global mtrDB
        return mtrDB[m].getDialRealPosition()

class motorTargetRaw():
    """
    Class to globally control virtual Motor target using Raw fields
    """

    def __init__(self):
        """
        **Constructor**

        Parameters
        ----------
        None
        """
        self.targets = {}

    def __getitem__(self, m):
        """
        Get current value of the virtual Motor positioning using Raw field

        Parameters
        ----------
        m : `dictionary`
            Represents the device target, virtual Motor, in the `mtrDB` global array of devices

        Returns
        -------
        `double` or `dictionary` item
            Read the current Positioning value of virtual Motor (Real)

            .. note::
                If `m` parameter is received and it is in the targets list, then its
                correspondent target is returned (as a `dictionary` item), otherwise,
                real position of virtual Motor, using the Raw field, is returned (as
                a `double` value)
        """

        global mtrDB
        if m in self.targets: 
            return self.targets[m]
        return mtrDB[m].getRawRealPosition()

    def __setitem__(self, m, pos):
        """
        Set a position value to the virtual Motor target received as input parameter 

        Parameters
        ----------
        m : `dictionary`
            Represents the target device, virtual Motor, in the `mtrDB` global array of devices

        pos : `double`
            The desired position to set
        """

        self.targets[m] = pos

    def keys(self):
        """
        Get keys (indexes) of all virtual Motor targets 

        Returns
        -------
        `integer array`
            Read the keys (indexes) from all targets
        """

        return self.targets.keys()

class motorPositionRaw():
    """
    Class to globally control positioning of virtual Motor using Raw fields
    """

    def __getitem__(self, m):
        """
        Get current value of the virtual Motor positioning using Raw field

        Parameters
        ----------
        m : `dictionary`
            Represents the device, virtual Motor, in the `mtrDB` global array of devices

        Returns
        -------
        `double`
            Read the current Positioning value of virtual Motor (Real) using
            Raw field
        """

        global mtrDB
        return mtrDB[m].getRawRealPosition()

class PseudoMotor(IScannable, StandardDevice):
    """
    Class to control Pseudo-Motor (virtual Motor).

    Examples
    --------
    >>> from py4syn.epics.PseudoMotorClass import PseudoMotor
    >>>    
    >>> def createPseudoMotor(mnemonic="", description="", backwardFormula="", forwardFormulasDict= []):
    ...    
    ...    new_pseudo_motor = ''
    ...    
    ...    try:
    ...        new_motor = PseudoMotor("motorName", "pseudo-motor to help controlling experiment", "", [])
    ...            print "Motor " + pvName + " created with success!"
    ...    except Exception,e:
    ...        print "Error: ",e
    ...    
    ...    return new_pseudo_motor
    """

    def __init__(self, mnemonic, description, backwardFormula, forwardFormulasDict):
        """
        **Pseudo Motor class Constructor**

        Parameters
        ----------
        mnemonic : `string`
            Motor mnemonic

        description : `string`
            Motor Description

        backwardFormula : `string`
            Mathematical Formula used to calculate the Pseudo motor position based on other motors

        forwardFormulasDict : `dictionary`
            Dictionary containing mathematical relations to move each of the motors involved in the pseudo motor movement
        """
        StandardDevice.__init__(self, mnemonic)        
        self.name = mnemonic

        self.description = description
        self.backFormula = backwardFormula
        self.forwardDict = forwardFormulasDict

    def __str__(self):
        return self.getMnemonic()

    def getDirection(self):
        """
        Read the Pseudo motor direction

        Returns
        -------
        `integer`

        .. note::
            0. Positive direction;
            1. Negative direction.
        """
        pass

    def isMoving(self):
        """
        Check if any of the motors are moving

        Returns
        -------
        `boolean`

        .. note::
            - **True**  -- At least one Motor is being moved;
            - **False** -- **NO** one of the Motors is being moved.
        """
        global mtrDB
        aux = False
        for m in self.forwardDict:
            if not mtrDB[m].isMoving() and (mtrDB[m].isAtHighLimitSwitch() or mtrDB[m].isAtLowLimitSwitch()):
                self.stop()
                return False
                
            if mtrDB[m].isMoving():
                aux = True

        return aux

    def isAtLowLimitSwitch(self):
        """
        Check if the low limit switch of any of the motors is activated

        Returns
        -------
        `int`

        .. note::
            - **1** -- At least one Motor is at Low Limit;
            - **0** -- **NO** one of the Motors is at Low Limit.
        """
        global mtrDB
        for m in self.forwardDict:
            if mtrDB[m].isAtLowLimitSwitch():
                return 1

        return 0

    def isAtHighLimitSwitch(self):
        """
        Check if the high limit switch of any of the motors is activated

        Returns
        -------
        `int`

        .. note::
            - **1** -- At least one Motor is at High Limit;
            - **0** -- **NO** one of the Motors is at High Limit.
        """
        global mtrDB
        for m in self.forwardDict:
            if mtrDB[m].isAtHighLimitSwitch():
                return 1

        return 0

    def getDescription(self):
        """
        Read the motor description based on the `DESC` (Description) field of
        virtual Motor

        Returns
        -------
        `string`
        """

        return self.description

    def getHighLimitValue(self):
        """
        Read the motor high limit based on the `HLM` (User High Limit) field of
        virtual Motor

        Returns
        -------
        `double`
        """

        return numpy.nan

    def getLowLimitValue(self):
        """
        Read the motor low limit based on the `LLM` (User Low Limit) field of
        virtual Motor

        Returns
        -------
        `double`
        """

        return numpy.nan

    def getDialHighLimitValue(self):
        """
        Read the motor dial high limit based on the `DHLM` (Dial High Limit)
        field of virtual Motor

        Returns
        -------
        `double`
        """

        return numpy.nan

    def getDialLowLimitValue(self):
        """
        Read the motor dial low limit based on the `DLLM` (Dial Low Limit)
        field of virtual Motor

        Returns
        -------
        `double`
        """

        return numpy.nan

    def getBacklashDistanceValue(self):
        """
        Read the motor backlash distance based on the `BDST` (Backlash Distance,
        `EGU`) field of virtual Motor

        Returns
        -------
        `double`
        """

        return numpy.nan

    def getVariableOffset(self):
        """
        Read the motor variable offset based on the `VOF` (Variable Offset)
        field of virtual Motor

        Returns
        -------
        `integer`
        """

        return numpy.nan

    def getFreezeOffset(self):
        """
        Read the motor freeze offset based on the `FOF` (Freeze Offset) field
        of virtual Motor

        Returns
        -------
        `integer`
        """

        return numpy.nan

    def getOffset(self):
        """
        Read the motor offset based on the `OFF` (User Offset, `EGU`) field of
        virtual Motor

        Returns
        -------
        `string`
        """

        return numpy.nan

    def getRealPosition(self):
        """
        Read the motor real position based on the `RBV` (User Readback Value)
        field of virtual Motor

        Returns
        -------
        `double`
        """

        global mtrDB
        global A
        global T
        exec(self.__defineMotors())

        return eval(self.backFormula)

    def getRawPosition(self):
        """
        Read the motor RAW position based on the `RVAL` (Raw Desired Value)
        field of Motor Record

        Returns
        -------
        `double`
        """

        return self.getRawRealPosition()

    def getRawRealPosition(self):
        """
        Read the motor RAW real position based on the `RRBV` (Raw Readback Value)
        field of Motor Record

        Returns
        -------
        `double`
        """
        global mtrDB
        global AR
        global TR
        exec(self.__defineMotors())
        dformula = self.backFormula.replace("A[", "AR[").replace("T[","TR[")
        return eval(dformula)


    def getDialRealPosition(self):
        """
        Read the motor DIAL real position based on the `DRBV` (Dial Readback
        Value) field of virtual Motor

        Returns
        -------
        `double`
        """

        global mtrDB
        global AD
        global TD
        exec(self.__defineMotors())
        dformula = self.backFormula.replace("A[", "AD[").replace("T[","TD[")
        return eval(dformula)

    def getDialPosition(self):
        """
        Read the motor target DIAL position based on the `DVAL` (Dial Desired
        Value) field of virtual Motor

        Returns
        -------
        `double`
        """

        return self.getDialRealPosition()
 
    def getPosition(self):
        """
        Read the motor target position based on the `VAL` (User Desired Value)
        field of virtual Motor

        Returns
        -------
        `double`
        """

        return self.getRealPosition()

    def getEGU(self):
        """
        Read the motor engineering unit based on the `EGU` (Engineering Units)
        field of the virtual Motor

        Returns
        -------
        `string`
        """

        return self.virtualEGU

    def getLVIO(self):
        """
        Read the motor limit violation `LVIO` (Limit Violation) field of
        the virtual Motor

        Returns
        -------
        `short`
        """

        pass

    def setEGU(self, unit):
        """
        Set the motor engineering unit to the `EGU` (Engineering Units) field
        of virtual Motor

        Parameters
        ----------
        unit : `string`
            The desired engineering unit.

            .. note::
                **Example:** "mm.", "deg."
        """

        self.virtualEGU = unit

    def setHighLimitValue(self, val):
        """
        Set the motor high limit based on the `HLM` (User High Limit) field of
        virtual Motor

        Parameters
        ----------
        val : `double`
            The desired value to set
        """

        pass

    def setLowLimitValue(self, val):
        """
        Set the motor low limit based on the `LLM` (User Low Limit) field of
        virtual Motor

        Parameters
        ----------
        val : `double`
            The desired value to set
        """

        pass

    def setDialHighLimitValue(self, val):
        """
        Set the motor dial high limit based on the `DHLM` (Dial High Limit)
        field of virtual Motor

        Parameters
        ----------
        val : `double`
            The desired value to set
        """

        pass

    def setDialLowLimitValue(self, val):
        """
        Set the motor dial low limit based on the `DLLM` (Dial Low Limit)
        field of virtual Motor

        Parameters
        ----------
        val : `double`
            The desired value to set
        """

        pass

    def setSETMode(self):
        """
        Put the motor in SET mode

        .. note::
            Motor will **NOT** move until it is in in **USE mode**
        """

        pass

    def setUSEMode(self):
        """
        Put the motor in **USE mode**
        """

        pass

    def setVariableOffset(self, val):
        """
        Set the motor variable offset based on the `VOF` (Variable Offset)
        field of virtual Motor

        Parameters
        ----------
        val : `integer`
            The desired value to set
        """

        pass

    def setFreezeOffset(self, val):
        """
        Set the motor freeze offset based on the `FOF` (Freeze Offset) field
        of virtual Motor

        Parameters
        ----------
        val : `integer`
            The desired value to set
        """

        pass

    def setOffset(self, val):
        """
        Set the motor offset based on the `OFF` (User Offset, `EGU`) field of
        virtual Motor

        Parameters
        ----------
        val : `double`
            The desired value to set
        """

        global mtrDB
        for m in self.forwardDict:
            mtrDB[m].setSETMode()
            
        self.setAbsolutePosition(val)
        
        for m in self.forwardDict:
            mtrDB[m].setUSEMode()

    def setDialPosition(self, pos, waitComplete=False):
        """
        Set the motor target DIAL position based on the `DVAL` (Dial Desired
        Value) field of virtual Motor

        Parameters
        ----------
        pos : `double`
            The desired position to set
        waitComplete : `boolean` (default is **False**)
            .. note::
                If **True**, the function will wait until the movement finish
                to return, otherwise don't.
        """

        pass

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

        global mtrDB
        global A
        global T

        exec(self.__defineMotors())

        ca.poll(evt=0.05)

        ret, msg = self.canPerformMovement(pos)
        if(not ret):
            raise Exception("Can't move motor "+self.name+" to desired position: "+str(pos)+ ", " + msg)

        for m in self.forwardDict:
            mtrDB[m].setAbsolutePosition(T[m])

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

        newPos = self.getRealPosition() + pos
        self.setAbsolutePosition(newPos, waitComplete)

    def setVelocity(self, velo):
        """
        Set the motor velocity up based on the `VELO` (Velocity, EGU/s) field
        from virtual Motor

        Parameters
        ----------
        velo : `double`
            The desired velocity to set
        """

        pass

    def setAcceleration(self, accl):
        """
        Set the motor acceleration time based on the `ACCL` (Seconds to
        Velocity) field from virtual Motor

        Parameters
        ----------
        accl : `double`
            The desired acceleration to set
        """

        pass

    def setUpdateRequest(self,val):
        """
        Set the motor update request flag based on the `STUP` (Status Update
        Request) field from virtual Motor

        Parameters
        ----------
        val : `integer`
            The desired value to set for the flag
        """

        pass

    def validateLimits(self):
        """
        Verify if motor is in a valid position.  In the case it has been reached
        the HIGH or LOW limit switch, an exception will be raised.
        """

        message = ""
        if(self.isAtHighLimitSwitch()):
            message = 'Motor: '+self.name+' reached the HIGH limit switch.'
        elif(self.isAtLowLimitSwitch()):
            message = 'Motor: '+self.name+' reached the LOW limit switch.'
        if(message != ""):
            raise Exception(message)

    def canPerformMovementCalc(self, target):
        return self.canPerformMovement(target)

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

        global mtrDB
        global A
        global T

        exec(self.__defineMotors())

        T = motorTarget()
        T[self.name] = target

        for m in self.forwardDict:
            mPos = eval(self.forwardDict[m])
            if(mtrDB[m].canPerformMovementCalc(mPos)):
                T[m] = mPos
            else:
                return False, "Motor "+m+" cannot move to: "+str(mPos)
                
        return True,""

    def stop(self):
        """
        Stop the motor
        """

        global mtrDB
        for m in self.forwardDict:
            mtrDB[m].stop()

    def wait(self):
        """
        Wait until the motor movement finishes
        """

        while(self.isMoving()):
            ca.poll(evt=0.01)

    def __defineMotors(self):
        """
        Define a set of virtual motors based on devices in the global `mtrDB`
        
        Returns
        -------
        `string`
            A command which combines all devices in `mtrDB`

        """

        global mtrDB
        cmd = '\n'.join(['%s = "%s"' % (m, m) for m in mtrDB])
        return cmd

    def getValue(self):
        """
        Get the current position of the motor.
        See :class:`py4syn.epics.IScannable`

        Returns
        -------
        `double`
            Read the current value (virtual Motor Real Position)
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

A = motorPosition()
T = motorTarget()

AD = motorPositionDial()
TD = motorTargetDial()

AR = motorPositionRaw()
TR = motorTargetRaw()