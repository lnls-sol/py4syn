"""HD-DCM

HD-DCM has five degrees of freedom and five operation modes (see below).

The five degrees of freedom are:

- gonio (GonRx)
- long stroke (LosUy)
- short stroke uy (ShsUy)
- short stroke rx (ShsRx)
- short stroke rz (ShsRz)

During the class initialization the constructor checks the current operation
mode and the rest of the class methods adjusts their behavior accordingly.

Regardless of the operation mode the operation steps are roughly the same:

1st) Send the desired set point to the DCM controller.
2nd) Wait for the DCM controller to calculate all the trajectories.
3rd) Confirm that we really want to move by sending the real move command.
4th) Wait for the DCM to finish its movement and to be in position.

Below is a brief explanation of each operation mode.

A. Fully independent (with EPICS)

    All of the five degrees of freedom are decoupled and can be adjusted
    individually via PVs.

B. Gonio as leader

    We control only the gonio angle (via PV) and the other four degrees of
    freedom adjusts accordingly.

C. Gonio as leader + undulator phase control

    Same as above but the DCM will control the undulator phase as well.

D. Gonio as follower

    In this mode the gonio will move automatically following the beamline
    undulator phase and the remaining four degrees of freedom will move
    automatically following the DCM gonio.

    Note that in this mode we do not actually control the DCM, the class will
    (purposely) refuse to control the DCM and raise an error.

E. Fully independent (without EPICS)

    We generate a file with the trajectory for all five degrees of freedom and
    send it to the DCM controller.

    In this mode we can ignore the 1st and 2nd operation steps, but we still
    need to confirm that we really want to start moving.

    Optionally we can also generate the trajectory for the undulator phase.

:platform: Unix
:synopsis: Python3 class for ...

.. moduleauthors:: Carlos Doro Neto <carlos.doro@lnls.br>
                   João Leandro de Brito Neto <joao.brito@lnls.br>
                   Letícia Garcez Capovilla <leticia.capovilla@lnls.br>
"""

from epics import PV
from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice


class HD_DCM(StandardDevice, IScannable):

    def __init__(self, mnemonic, pvName):
        """Class for controlling an HD-DCM.

        parameters
        ----------
        mnemonic : `string`
            Class mnemonic, see :class:`py4syn.epics.StandardDevice`.
        pvPrefix : `string`
            PV prefix.
        """

        # Assuming pvName follows the PV naming convention for Sirius beamlines
        # the pvPrefix (including the last colon) is 12 characters long.

        assert len(pvName) > 12
        pvPrefix = pvName[:12]
        pvSuffix = pvName[12:]

        super().__init__(mnemonic)

        self._opMode = PV(pvPrefix + "???")
        assert self._opMode.wait_for_connection()

        # Not all modes are valid and not all degrees of freedom are available
        # for all modes, let's check everything is all right before continuing.

        if self._opMode.get() == "D":
                raise Exception("Refusing to control the DCM in Gonio as follower")

        if self._opMode.get() == "B" or self._opMode.get() == "C":
            if pvSuffix != "GonRx":
                raise Exception("Can only control Gonio in Gonio as leader")

        if self._opMode.get() == "E":
            raise NotImplementedError
            # import ref3

        else:
            self._setpoint = PV(pvPrefix)
            self._foundTrajectory = PV(pvPrefix)
            assert self._setpoint.wait_for_connection()
            assert self._foundTrajectory.wait_for_connection()

        # Regardless of the operation mode the readback value, move and stop
        # commands, limits and in position flag are always read/set by PVs.

        self._readback = PV(pvName + "_RBV")
        self._move = PV(pvPrefix + "???")
        self._stop = PV(pvPrefix + "???")
        self._lowLimit = PV(pvPrefix + "???")
        self._highLimit = PV(pvPrefix + "???")
        self._inPos = PV(pvPrefix + "???")

        assert self._readback.wait_for_connection()
        assert self._move.wait_for_connection()
        assert self._stop.wait_for_connection()
        assert self._lowLimit.wait_for_connection()
        assert self._highLimit.wait_for_connection()
        assert self._inPos.wait_for_connection()

    # IScannable methods overriding

    def getValue(self):
        """Return the current position.

        returns
        -------
        `double`
        """

        return self._readback.get()

    def setValue(self, v):
        """Sends move command.

        parameters
        ----------
        v : `double`
            The target position.
        """

        if self._opMode.get() == "E":
            raise NotImplementedError

        else:
            # Send set point to DCM controller.
            self._setpoint.put(v, wait=True)

            # Wait for the DCM controller to acknowledge out setpoint request.
            while self.foundTrajectory():
                pass

            # Wait for tragetory calculations.
            while not self.foundTrajectory():
                pass

        # Send move command.
        self._moveCmd.put(1, wait=True)

        # Wait for it to start moving.
        while not self.isMoving():
            pass

        # Wait for it to reach target position.
        self.wait()

    def wait(self):
        """Waits for the DCM to be in position."""
        while self.isMoving():
            pass

    def getLowLimitValue(self):
        """Return the lower movement limit.

        returns
        -------
        `double`
        """

        return self._lowLimit.get()

    def getHighLimitValue(self):
        """Return the higher movement limit.

        returns
        -------
        `double`
        """

        return self._highLimit.get()

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

    def foundTrajectory(self):
        """Returns True if the DCM controller found a trajectory for the
        current setpoint.

        Returns
        -------
        `boolean`
        """

        return self._foundTrajectory.get()
