"""
Keysight 33500B class

Python class for Keysight 33500B using EPICS area detector IOC.

:platform: Unix
:synopsis: Python class for Keysight 33500B

.. moduleauthor:: Douglas Bezerra Beniz <douglas.beniz@lnls.br>

"""
from threading import Event

from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.IScannable import IScannable
from epics import PV, ca, caput

from time import sleep

RESPONSE_TIMEOUT = 15
WAIT_ACQUIRING = 0.005


class Keysight33500B(StandardDevice, IScannable):
    """
    Class to control Keysight 33500B via EPICS.

    Examples
    --------
    """
    def onAcquireChange(self, value, **kw):
        self._done = (value == 0)


    def __init__(self, pv, mnemonic):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`

        Parameters
        ----------
        mnemonic : `string`
            A mnemonic for the Keysight 33500B
        pv : `string`
            Base name of the EPICS process variable
        """
        super().__init__(mnemonic)
        # self.pvStatus = PV(pv + ':Acquiring', callback=self.onAcquireChange)

        # -------------------------------------------------
        # General Process Variabels
        self.pvFunction = PV(pv + ':Function')
        self.pvFunction_RBV = PV(pv + ':Function_RBV')
        self.pvFrequency = PV(pv + ':Frequency')
        self.pvFrequency_RBV = PV(pv + ':Frequency_RBV')
        self.pvOutput = PV(pv + ':Output')
        self.pvOutput_RBV = PV(pv + ':Output_RBV')
        self.pvPhase = PV(pv + ':Phase')
        self.pvPhase_RBV = PV(pv + ':Phase_RBV')
        # -------------------------------------------------
        # Pulse Process Variabels
        self.pvPulseDutyCycle = PV(pv + ':Pulse:DutyCycle')
        self.pvPulseDutyCycle_RBV = PV(pv + ':Pulse:DutyCycle_RBV')
        self.pvPulseHold = PV(pv + ':Pulse:Hold')
        self.pvPulseHold_RBV = PV(pv + ':Pulse:Hold_RBV')
        self.pvPulsePeriod = PV(pv + ':Pulse:Period')
        self.pvPulsePeriod_RBV = PV(pv + ':Pulse:Period_RBV')
        self.pvPulseWidth = PV(pv + ':Pulse:Width')
        self.pvPulseWidth_RBV = PV(pv + ':Pulse:Width_RBV')
        self.pvPulseTransitionLeading = PV(pv + ':Pulse:Transition:Leading')
        self.pvPulseTransitionLeading_RBV = PV(pv + ':Pulse:Transition:Leading_RBV')
        self.pvPulseTransitionTrailing = PV(pv + ':Pulse:Transition:Trailing')
        self.pvPulseTransitionTrailing_RBV = PV(pv + ':Pulse:Transition:Trailing_RBV')
        # -------------------------------------------------
        # Ramp Process Variabels
        self.pvRampSymmetry = PV(pv + ':Ramp:Symmetry')
        self.pvRampSymmetry_RBV = PV(pv + ':Ramp:Symmetry_RBV')
        # -------------------------------------------------
        # Square Process Variabels
        self.pvSquareDutyCycle = PV(pv + ':Square:DutyCycle')
        self.pvSquareDutyCycle_RBV = PV(pv + ':Square:DutyCycle_RBV')
        self.pvSquarePeriod = PV(pv + ':Square:Period')
        self.pvSquarePeriod_RBV = PV(pv + ':Square:Period_RBV')
        # -------------------------------------------------
        # Voltage Process Variabels
        self.pvVoltage = PV(pv + ':Voltage')
        self.pvVoltage_RBV = PV(pv + ':Voltage_RBV')
        self.pvVoltageHigh = PV(pv + ':Voltage:High')
        self.pvVoltageHigh_RBV = PV(pv + ':Voltage:High_RBV')
        self.pvVoltageLow = PV(pv + ':Voltage:Low')
        self.pvVoltageLow_RBV = PV(pv + ':Voltage:Low_RBV')
        self.pvVoltageOffset = PV(pv + ':Voltage:Offset')
        self.pvVoltageOffset_RBV = PV(pv + ':Voltage:Offset_RBV')
        self.pvVoltageUnit = PV(pv + ':Voltage:Unit')
        self.pvVoltageUnit_RBV = PV(pv + ':Voltage:Unit_RBV')
        self.pvVoltageRangeAuto = PV(pv + ':Voltage:Range:Auto')
        self.pvVoltageRangeAuto_RBV = PV(pv + ':Voltage:Range:Auto_RBV')

        # For tests
        self._done = True
        self.waitTime = 0.5


    def getRealPosition(self):
        return self.getValue()


    def getValue(self):
        """
        Obtain the current value of keysight 33500B device or its identification.

        Returns
        -------
        `integer`

        .. note::
            - **1**  -- Active keysight 33500B;
            - **0**  -- Inactive keysight 33500B.
        """
        return self.pvVoltageOffset_RBV.get()


    def setAbsolutePosition(self, p, wait=True):
        self.setValue(p, wait)


    def setValue(self, v, wait=True):
        """
        Method to set a value to the keysight 33500B device.

        Parameters
        ----------
        `integer`

        .. note::
            - **1**  -- Active keysight 33500B;
            - **0**  -- Inactive keysight 33500B.
        """
        if (v < self.getLowLimitValue()):
            v = self.getLowLimitValue()
        elif (v > self.getHighLimitValue()):
            v = self.getHighLimitValue()

        self.pvVoltageOffset.put(v, wait=wait)

        if (wait):
            sleep(self.getWaitTime())


    def isActive(self):
        """
        Return whether keysight 33500B is currently active (set to 1).

        Returns
        -------
        `boolean`

        .. note::
            - **True**  -- keysight 33500B is active (1);
            - **False** -- keysight 33500B is inactive (0).
        """
        return self._active


    def isDone(self):
        return True


    def wait(self):
        while(not self._done):
            ca.poll(0.001)


    def isMoving(self):
        return False


    def getLowLimitValue(self):
        """
        Obtain low limit value of keysight 33500B.

        Parameters
        ----------
        None

        Returns
        -------
        `double`
        """
        return (-2/2)


    def getHighLimitValue(self):
        """
        Obtain high limit value of keysight 33500B.

        Parameters
        ----------
        None

        Returns
        -------
        `double`
        """
        return (12/2)


    def setFunction(self, function=0, wait=True):
        self.pvFunction.put(function, wait=wait)


    def getFunction(self):
        return self.pvFunction_RBV.get()

    def setOutput(self, output=0, wait=True):
        # 0: off; 1: on
        self.pvOutput.put(0 if (output == 0) else 1, wait=wait)


    def getOutput(self):
        return self.pvOutput_RBV.get()

    def stop(self):
        pass

    def setWaitTime(self, time):
        self.waitTime = time

    def getWaitTime(self):
        return self.waitTime