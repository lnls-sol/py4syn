
============================
MarCCD X-ray Detector System
============================

.. module:: py4syn.epics.MarCCDClass
   :synopsis: Python class for MarCCD cameras

The MarCCD X-ray detectors are programmable cameras. Access to the camera is not done
with EPICS. Instead, the camera host machine provides a TCP socket with a custom
protocol for communication. The camera may be used as a standard Py4Syn ICountable,
but instead of returning values to be plotted, the acquired images are stored into files.

The MarCCD Py4Syn class supports using software controlled shutters. The shutters
supported can be one of two types: normal shutters and toggle shutters. Both shutters
are accessed as EPICS PVs representing bits. The difference is that normal
shutters have zero and one values to represent the open and closed states, while the
toggle shutter uses one PV to toggle the shutter state and another to read back the
current state.

Using EPICS MarCCD camera module
================================

Usage of Python class for EPICS MarCCD cameras.

.. autoclass:: MarCCD
   :members:
