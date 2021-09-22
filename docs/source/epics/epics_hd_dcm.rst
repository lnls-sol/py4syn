
======
HD_DCM
======

.. module:: py4syn.epics.HDDCMClass
   :synopsis: Python3 class for controlling an HD-DCM.

Class for controlling an HD-DCM.

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

Using the HD-DCM class
======================

.. autoclass:: CompactRIOAnalog
   :members:
