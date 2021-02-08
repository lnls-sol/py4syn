"""Symetrie hexapods using Power Pmac controllers class

Python class for a single user axis of Symetrie hexapods that use Delta Tau Power Pmac controllers

:platform: Unix
:synopsis: Python class for Symetrie hexapods using Power Pmac controllers

.. moduleauthors::   Carlos Doro Neto <carlos.doro@lnls.br>

"""

from warnings import warn
from epics import PV
from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice

class Hexapode(StandardDevice, IScannable):

    def __init__(self, mnemonic, pvName, axis):

        valid_axes = ('tx', 'ty', 'tz', 'rx', 'ry', 'rz')
        axis = axis.lower()
        assert axis in valid_axes, "Got axis={}, expected one of the following: {}.".format(axis, ', '.join(valid_axes))

        super().__init__(mnemonic)

        self.s_uto_axis_RBV = PV("{}:s_uto_{}_RBV".format(pvName, axis))
        self.MOVE_PTP_Axis = PV("{}:MOVE_PTP:{}".format(pvName, axis.capitalize()))
        self.MOVE_PTP = PV("{}:MOVE_PTP".format(pvName))
        self.InPosition_RBV = PV("{}:s_hexa:InPosition_RBV".format(pvName))
        self.User_Axis_Neg_RBV = PV("{}:CFG_LIMIT:User_{}_Neg_RBV".format(pvName, axis.capitalize()))
        self.User_Axis_Pos_RBV = PV("{}:CFG_LIMIT:User_{}_Pos_RBV".format(pvName, axis.capitalize()))
        self.Valid_RBV = PV("{}:Drv:ValidateMove:Valid_RBV".format(pvName))
        self.STOP = PV("{}:STOP".format(pvName))

        self.s_uto_axis_RBV.wait_for_connection()
        self.MOVE_PTP_Axis.wait_for_connection()
        self.MOVE_PTP.wait_for_connection()
        self.InPosition_RBV.wait_for_connection()
        self.User_Axis_Neg_RBV.wait_for_connection()
        self.User_Axis_Pos_RBV.wait_for_connection()
        self.Valid_RBV.wait_for_connection()
        self.STOP.wait_for_connection()

    def getValue(self):
        return self.s_uto_axis_RBV.get()

    # In order to reduce dead time setValue() purposely:
    # 1. do not check if the hexapod is already moving,
    # 2. do not validate the movement beforehand.
    # What happens in these situations?
    # 1. If the hexapod is already moving the command will be queued.
    # 2. If an invalid movement is issued we will be stuck in an infinite loop waiting for it to move.

    def setValue(self, value, waitComplete=True):
        self.MOVE_PTP_Axis.put(value, wait=True)
        self.MOVE_PTP.put(0, wait=True)
        while not self.isMoving(): pass
        if waitComplete: self.wait()

    def wait(self):
        while self.isMoving(): pass

    # For any given axis its upper and lower limits depend on the position of the other axes.
    # E.g.: tx upper limit can be +50 mm when tz equals 0 mm, but only +10 mm when tz equals 30 mm (hypothetical values).
    # However the PVs associated with them (upper and lower limits) do not reflect this dynamic behavior.
    # Because of this getLowLimitValue() and getHighLimitValue() MUST NOT be used for movement validation, canPerformMovement() must be used instead.
    # The only reason why getLowLimitValue() and getHighLimitValue() are implemented is because IScannable requires them.

    def getLowLimitValue(self):
        warn("getLowLimitValue() and getHighLimitValue() MUST NOT be used for movement validation, use canPerformMovement() instead.")
        return self.User_Axis_Neg_RBV.get()

    def getHighLimitValue(self):
        warn("getLowLimitValue() and getHighLimitValue() MUST NOT be used for movement validation, use canPerformMovement() instead.")
        return self.User_Axis_Pos_RBV.get()

    def canPerformMovement(self, target):
        rollback = self.MOVE_PTP_Axis.get()
        self.MOVE_PTP_Axis.put(target, wait=True)
        answer = not self.Valid_RBV.get()
        self.MOVE_PTP_Axis.put(rollback, wait=True)
        return answer

    def isMoving(self):
        answer = not self.InPosition_RBV.get()

    def stop(self):
        self.STOP.put(1, wait=True)

