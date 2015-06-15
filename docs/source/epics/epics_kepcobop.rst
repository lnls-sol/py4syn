
=========================
Kepco BOP GL Power Supply
=========================

.. module:: py4syn.epics.KepcoBOPClass
   :synopsis: Python class for Kepco BOP GL power supplies
   
The Kepco BOP GL power supplies are programmable power supplies that operate in current
or voltage mode. The current implementation supports the Kepco BOP 50-20GL model.

.. warning::
    During tests with the Kepco power supply available in the lab, it was noticed that
    there were malfunctioning issues with it. The malfunctioning includes not being
    able to set voltage values, queries returning empty results and "out of range" errors
    when there should be none. The malfunctioning seemed to be triggered
    by either one of two events:
    
    1) it's believed that sometimes the power supply powers up in an invalid state.
    2) it's believed that some commands that result in errors may put the power supply in an invalid state.
    
    In either case, the malfunction is persistent and software commands to reset the
    power supply to a sane state may not work. Only power resetting the device seems
    to solve the problem. Because of this, the power supply must be used with extra
    caution.

Using EPICS Kepco BOP GL power supply module
============================================

Usage of Python class for EPICS Kepco BOP GL power supplies.

.. autoclass:: KepcoBOP
   :members:

