
=================
EPICS Digital I/O
=================

.. module:: py4syn.epics.DigitalIOClass
   :synopsis: Python Class for Digital I/O control using EPICS.

This is a Python class which allows the control of a set of digital I/O ports defined by the user. 
Ports are named with a common prefix followed by its number.
Once it is based on EPICS resources, one can get and set PV values related to the ports. 
Its also possible to add and delete ports from the set, and list their names.

Using EPICS Digital I/O module
==============================

Usage of Python class for EPICS Digital I/O control

.. autoclass:: DigitalIO
   :members:
