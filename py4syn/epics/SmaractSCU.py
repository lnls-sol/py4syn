"""SmaractSCU piezo controller class
Python class for SmaractSCU piezo controllers
:platform: Unix
:synopsis: Python class for SmaractSCU piezo controllers
.. moduleauthor:: Douglas Henrique Araujo <douglas.araujo@lnls.br>
"""
from time import sleep
from epics import PV
from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice


class SmaractSCU(IScannable, StandardDevice):
    """
    Class to control SmacartSCU piezo controllers via EPICS.
    """

    WAIT_ACQUIRING = 0.005

    def onStatusChange(self, value, **kw):
        self._done = (value == 'S')

    def __init__(self, pvName, mnemonic, channel):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`
        Parameters
        ----------
        pvName : `string`
            Power supply base naming of the PV (Process Variable)
        mnemonic : `string`
            smaract controller mnemonic
        channel : `int`
            Channel of the module
        """

        super().__init__(mnemonic)

        self.pvMoveUP = PV(pvName + ':MOVEUP')
        self.pvMoveDOWN = PV(pvName + ':MOVEDOWN')
        self.pvAmplitude = PV(pvName + ':AMPLITUDE')
        self.pvFrequency = PV(pvName + ':FREQUENCY')
        self.pvSteps = PV(pvName + ':STEPS')
        self.pvChannel = PV(pvName + ':CHANNEL')
        self.pvStop = PV(pvName + ':STOP')
        self.pvStatus = PV(pvName + ':STATUS', callback=self.onStatusChange)
        self.pvPosRBV = PV(pvName + ':CH' + str(channel) + ':POSITION')
        self._done = 0

        self.pvChannel.put(channel, wait=True)

    def getLowLimitValue(self):
        """
        Returns the controller low limit position.
        Returns
        -------
        `float`
        """
        return -10000

    def getHighLimitValue(self):
        """
        Returns the controller high limit position.
        Returns
        -------
        `float`
        """
        return 10000

    def getValue(self):
        """
        Returns the current position.
        Returns
        -------
        `float`
        """
        return self.pvPosRBV.get()

    def getRealPosition(self):
        """
        Returns the current position.
        Returns
        -------
        `float`
        """
        return self.pvPosRBV.get()

    def getDialRealPosition(self):
        """
        Returns the current position.
        Returns
        -------
        `float`
        """
        return self.pvPosRBV.get()

    def setValue(self, value, wait=True):
        if value < self.getLowLimitValue() or value > self.getHighLimitValue():
            raise ValueError('Value exceeds limits')
        getPos = self.getValue()
        self.pvSteps.put(abs(value-getPos), wait=True)
        self._done = 0
        if (value < getPos):
            sleep(.1)
            self.pvMoveDOWN.put(1)
        else:
            sleep(.1)
            self.pvMoveUP.put(1, wait=True)

        self._moving = True
        if wait:
            self.wait()

    def setAbsolutePosition(self, value, wait):
        self.setValue(value, True)

    def wait(self):
        """
        Blocks until the movement completes.
        """
        while not self._done:
            sleep(self.WAIT_ACQUIRING)

        self._moving = False
        self.stop()

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

    def stop(self):
        """
        Stop the motor
        """
        self.pvStop.put(1)

    def validateLimits(self):
        """
        Verify if motor is in a valid position. In the case it has been reached
        the HIGH or LOW limit switch, an exception will be raised.
        """
        return True
