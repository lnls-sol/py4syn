"""HD-DCM

HD-DCM has five degrees of freedom and four operation modes (see below).

The five degrees of freedom are:

- gonio (GonRx)
- long stroke (LosUy)
- short stroke uy (ShsUy)
- short stroke rx (ShsRx)
- short stroke rz (ShsRz)

Below is a brief explanation of each operation mode.

0. Asynchronous (with EPICS)

    All of the five degrees of freedom are decoupled and can be moved
    separately via PVs.

1. Synchronous

    >>> AS OF DEC. 3RD, 2021 THIS MODE DOES NOT WORK. DO NOT USE IT. <<<

2. Coupled - It is the only mode supported in this class!

    We control only the gonio (via PV) and the other four degrees of
    freedom adjust accordingly.

3. Follower

    In this mode the gonio will follow the beamline undulator phase and the
    remaining degrees of freedom will follow the gonio.

    Note that in this mode we do not actually control the DCM, the class will
    (purposely) refuse to control the DCM and raise an error.

:platform: Unix
:synopsis: Python3 class for HD-DCM

.. moduleauthors:: Carlos Doro Neto <carlos.doro@lnls.br>
                   João Leandro de Brito Neto <joao.brito@lnls.br>
"""

from epics import PV
from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice


class HD_DCM(StandardDevice, IScannable):

    def __init__(self, mnemonic, pvPrefix):
        """Class for controlling an HD-DCM.

        parameters
        ----------
        mnemonic : `string`
            Class mnemonic, see :class:`py4syn.epics.StandardDevice`.
        pvPrefix : `string`
            PV prefix.
        """

        super().__init__(mnemonic)

        opMode = PV(pvPrefix + ":DcmOpModeSel")
        assert opMode.wait_for_connection()
        assert opMode.get() == 2, "DCM not in Coupled mode. Refusing to control it."

        self._setpoint = PV(pvPrefix + ":GonRxR")
        self._velocity = PV(pvPrefix + ":GonRxTrajVdes")
        self._planTrajectory = PV(pvPrefix + ":GonRxTrajPlan")
        self._trajectoryFound = PV(pvPrefix + ":GonRxTrajStatus_RBV")
        self._move = PV(pvPrefix + ":DcmTrajMove")
        self._inPos = PV(pvPrefix + ":DcmInPos")
        self._stop = PV(pvPrefix + ":DcmTrajAbort")

        energyMode = PV(pvPrefix + ":DcmTrajEnergy")
        assert energyMode.wait_for_connection()
        if energyMode.get():
            self._readback = PV(pvPrefix + ":GonRxEnergy_RBV")
        else:
            self._readback = PV(pvPrefix + ":GonRxS_RBV")

        assert self._setpoint.wait_for_connection()
        assert self._velocity.wait_for_connection()
        assert self._planTrajectory.wait_for_connection()
        assert self._trajectoryFound.wait_for_connection()
        assert self._move.wait_for_connection()
        assert self._inPos.wait_for_connection()
        assert self._stop.wait_for_connection()
        assert self._readback.wait_for_connection()

    # IScannable methods overriding

    def getValue(self):
        """Return the current angle/energy.

        returns
        -------
        `float`
        """

        return self._readback.get()

    def setValue(self, v):
        """Sends move command.

        parameters
        ----------
        v : `float`
            The target angle/energy.
        """

        max_velocity = 9e-3
        velocity = min(max_velocity, .9*v)

        self._setpoint.put(v, wait=True)
        self._velocity.put(velocity, wait=True)
        self._planTrajectory.put(1, wait=True)

        while not self.trajectoryFound():
            pass

        self._move.put(1, wait=True)
        self.wait()

    def wait(self):
        """Waits for the DCM to be in position."""
        while self.isMoving():
            pass

    def getLowLimitValue(self):
        """Return the lower movement limit.

        returns
        -------
        `float`
        """

        return float("-inf")

    def getHighLimitValue(self):
        """Return the upper movement limit.

        returns
        -------
        `float`
        """

        return float("inf")

    # HD-DCM specific methods

    def stop(self):
        """Sends stop command."""
        self._stop.put(1, wait=True)
        self.wait()

    def isMoving(self):
        """Checks whether or not the DCM is moving.

        Returns
        -------
        `boolean`
        """

        return not self._inPos.get()

    def trajectoryFound(self):
        """Returns True if the DCM controller found a trajectory for the
        current setpoint.

        Returns
        -------
        `boolean`
        """

        return self._trajectoryFound.get() == "Row 0 t 2"
