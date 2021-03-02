"""Symetrie hexapod (PowerPmac)

Class for controlling a single axis of a Symetrie hexapod (limited to x, y, z and respective rotations).
Supports Symetrie IOCs that use PowerPmac controllers while maintaining the same API as SymetrieTurboClass.py.
Tested on Bora and Breva models.

:platform: Unix
:synopsis: Python3 class for Symetrie hexapods that use PowerPmac controllers

.. moduleauthors:: Carlos Doro Neto <carlos.doro@lnls.br>
"""

from warnings import warn

from epics import PV

from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice


class Hexapode(StandardDevice, IScannable):

    def __init__(self, mnemonic, pvName, axis):
        """

        parameters
        ----------
        mnemonic : `string`
            Class mnemonic, see :class:`py4syn.epics.StandardDevice`.
        pvName : `string`
            PV prefix.
        axis : `string`
            Which axis to control, valid values are: X, Y, Z, RX, RY and RZ.
        """

        if axis in ("X", "Y", "Z"):
            axis = "T{}".format(axis)

        super().__init__(mnemonic)

        self._sUtoAxisRbv = PV("{}:s_uto_{}_RBV".format(pvName, axis.lower()))
        self._movePtpAxis = PV("{}:MOVE_PTP:{}".format(pvName, axis.capitalize()))
        self._movePtp = PV("{}:MOVE_PTP".format(pvName))
        self._inPositionRbv = PV("{}:s_hexa:InPosition_RBV".format(pvName))
        self._userAxisNegRbv = PV("{}:CFG_LIMIT:User_{}_Neg_RBV".format(pvName, axis.capitalize()))
        self._userAxisPosRbv = PV("{}:CFG_LIMIT:User_{}_Pos_RBV".format(pvName, axis.capitalize()))
        self._validRbv = PV("{}:Drv:ValidateMove:Valid_RBV".format(pvName))
        self._stop = PV("{}:STOP".format(pvName))

        self._sUtoAxisRbv.wait_for_connection()
        self._movePtpAxis.wait_for_connection()
        self._movePtp.wait_for_connection()
        self._inPositionRbv.wait_for_connection()
        self._userAxisNegRbv.wait_for_connection()
        self._userAxisPosRbv.wait_for_connection()
        self._validRbv.wait_for_connection()
        self._stop.wait_for_connection()

    ### IScannable methods overriding ###

    def getValue(self):
        """Returns axis' current position.

        returns
        -------
        `double`
        """

        return self._sUtoAxisRbv.get()

    def setValue(self, v, waitComplete=True, autoMove=True):
        """Move axis.

        parameters
        ----------
        v : `double`
            The target position.
        waitComplete : `boolean`
            If set to False returns immediately after sending the command, otherwise waits for the axis to reach the target position.
        autoMove : `boolean`
            If set to False sends the target position without actually moving the axis. Useful when moving more than one axis at the same time.

        In order to reduce dead time it purposely:
            1. do not check if the hexapod is already in position,
            2. do not check if the hexapod is already moving,
            3. do not validate the movement beforehand.
        What if:
            1. the hexapod is already in position? A new move command is sent.
            2. the hexapod is already moving? The command will be queued.
            3. an invalid movement is issued? We will be stuck in an infinite loop waiting for it to move.
        """

        self._movePtpAxis.put(v, wait=True)
        if autoMove:
            self._movePtp.put(0, wait=True)
            while not self.isMoving():
                pass
            if waitComplete:
                self.wait()

    def wait(self):
        """Waits for all axes to stop moving."""
        while self.isMoving():
            pass

    def getLowLimitValue(self):
        """Returns axis' lower soft limit.

        returns
        -------
        `double`

        For any given axis its upper and lower limits depend on the position of the other axes.

        E.g.: x upper limit can be +50 mm when z equals 0 mm, but only +10 mm when z equals -30 mm (hypothetical values).

        However the PVs associated with them do not reflect this dynamic behavior.
        Because of this :meth:`getLowLimitValue` and :meth:`getHighLimitValue` MUST NOT be used for movement validation; :meth:`canPerformMovement` must be used instead.
        """

        warn("getLowLimitValue() MUST NOT be used for movement validation, use canPerformMovement() instead.")
        return self._userAxisNegRbv.get()

    def getHighLimitValue(self):
        """Returns axis' upper soft limit.

        See :meth:`getLowLimitValue`.
        """

        warn("getHighLimitValue() MUST NOT be used for movement validation, use canPerformMovement() instead.")
        return self._userAxisPosRbv.get()

    ### HexapodeClass.py API compatibility ###

    def onStatusChange(self, value, *args, **kwargs):
        """Does nothing, implemented only to maintain API compatibility with HexapodeClass.py."""
        pass

    def setAbsolutePosition(self, pos, *args, **kwargs):
        """Wrapper for :meth:`setValue`"""
        return self.setValue(pos, *args, **kwargs)

    def stop(self, waitComplete=True):
        """Stops all axes.

        parameters
        ----------
        waitComplete : `boolean`
            If True waits for the hexapod to stop moving, otherwise only sends the command.
        """

        self._stop.put(1, wait=True)
        if waitComplete:
            self.wait()

    def canPerformMovement(self, target):
        """Check whether axis can move to target or not.

        parameters
        ----------
        target : `double`

        returns
        -------
        `tuple`
            - [0] : `boolean`
                True if axis can move to target, False otherwise.
            - [1] : `string`
                Reason why it cannot reach target, empty if it can.
        """

        rollback = self._movePtpAxis.get()
        self._movePtpAxis.put(target, wait=True)
        answer = not self._validRbv.get()
        self._movePtpAxis.put(rollback, wait=True)
        if answer:
            return answer, ""
        else:
            return answer, "Out of SYMETRIE workspace."

    def getLimits(self, coord, axis=0):
        """Not implemented yet."""
        warn("getLimits: not implemented yet")

    def getDialLowLimitValue(self):
        """Not implemented yet."""
        warn("getDialLowLimitValue: not implemented yet")
        return 0.

    def getDialHighLimitValue(self):
        """Not implemented yet."""
        warn("getDialHighLimitValue: not implemented yet")
        return 0.

    def isMoving(self):
        """Check whether the hexapod is moving or not.

        Returns
        -------
        `boolean`
            True if any of the axes is moving, False otherwise.
        """

        return not self._inPositionRbv.get()

    def getRealPosition(self, *args, **kwargs):
        """Wrapper for :meth:`getValue`."""
        return self.getValue(*args, **kwargs)

    def getDialRealPosition(self):
        """Not implemented yet."""
        warn("getDialRealPosition: not implemented yet")
        return 0.

    def validateLimits(self):
        """Not implemented yet."""
        warn("validateLimits: not implemented yet")

    def setRelativePosition(self, pos, waitComplete=False):
        """Not implemented yet."""
        warn("setRelativePosition: not implemented yet")
