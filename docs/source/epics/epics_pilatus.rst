
============================
 Pilatus Detector System
============================

.. module:: py4syn.epics.PilatusClass
   :synopsis: Python class for Pilatus cameras

The Pilatus X-ray detectors are programmable cameras. Py4Syn uses the standard
area detector EPIC IOC for communicating with them. Since the IOC provides a high
level API, most of the acquisition logic is implemented in the IOC. The camera
is implemented as a standard ICountable, but instead of returning values to be plotted,
the acquired images are stored into files.

Using EPICS Pilatus camera module
================================

Usage of Python class for EPICS Pilatus cameras.

.. autoclass:: Pilatus
   :members:
