"""Undulator class
Python class Undulator controller
:platform: Unix
:synopsis: Python class for undulator controller
.. moduleauthor:: Douglas Henrique Araujo <douglas.araujo@lnls.br>
"""
from time import sleep
from epics import PV
from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice


class Undulator(IScannable, StandardDevice):
    """
    Class to control Undulator via EPICS.
    """

    WAIT_ACQUIRING = 0.005

    def onStatusChange(self, value, **kw):
        print("value: ", value)
        if self._moving:
            self._done = value

    def __init__(self, pvName, mnemonic):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`
        Parameters
        ----------
        pvName : `string`
            Power supply base naming of the PV (Process Variable)
        mnemonic : `string`
            smaract controller mnemonic
        """

        super().__init__(mnemonic)

        self.pv_und_phase_read = PV(pvName + ':Phase-Mon')
        self.pv_und_phase_write = PV(pvName + ':Phase-SP')
        self.pv_und_phase_moving = PV(pvName + ':Moving-Mon',
                                      callback=self.onStatusChange)
        self.pv_und_phase_command = PV(pvName + ':DevCtrl-Cmd')
        self._done = False
        self._moving = False

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
        return self.pv_und_phase_read.get()

    def getRealPosition(self):
        """
        Returns the current position.
        Returns
        -------
        `float`
        """
        return self.pv_und_phase_read.get()

    def getDialRealPosition(self):
        """
        Returns the current position.
        Returns
        -------
        `float`
        """
        return self.pv_und_phase_read.get()

    def setValue(self, value, wait=True):
        if value < self.getLowLimitValue() or value > self.getHighLimitValue():
            raise ValueError('Value exceeds limits')
        self.pv_und_phase_write.put(value, wait=True)

        # Send start (3) to DevCtrl-CMD
        self.pv_und_phase_command.put(3, wait=True)

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
        Stop the undulator
        Send stop (1) to DevCtrl-CMD
        """
        self.pv_und_phase_command.put(1)

    def validateLimits(self):
        """
        Verify if motor is in a valid position. In the case it has been reached
        the HIGH or LOW limit switch, an exception will be raised.
        """
        return True
