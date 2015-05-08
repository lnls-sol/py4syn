"""Keithley6485 Class

Python Class for EPICS Keithley control.

:platform: Unix
:synopsis: Python Class for EPICS Keithley control.

.. moduleauthor:: Diego Henrique Dorta <diego.dorta@lnls.br>
    .. note:: 18/08/2014 [diego.dorta]    First version released for K6514
    .. note:: 19/03/2015 [douglas.beniz]  Created a version for K6485 based on K6514
    .. note:: 16/04/2015 [douglas.beniz]  Make it derives from Keithley6514 class as suggested by Henrique Dante
"""
from epics import Device, ca, PV
from py4syn.epics.Keithley6514Class import Keithley6514

class Keithley6485(Keithley6514):
    """

    Python class to help configuration and control the Keithley 6514 Electrometer.

    Keithley is an electrical instrument for measuring electric charge or electrical potential difference.
    This instrument is capable of measuring extremely low currents. E.g.: pico (10e-12), i.e.: 0,000 000 000 001.

    For more information, please, refer to: `Model 6514 System Electrometer Instruction Manual <http://www.tunl.duke.edu/documents/public/electronics/Keithley/keithley-6514-electrometer-manual.pdf>`_
    """

    def __init__(self, pvName, mnemonic, timeBased=False):
        """
        **Constructor**
        To use this Keithley Class you must pass the PV (Process Variable) prefix.

            .. Note::
                e.g.: SXS:K6514

        Examples
        --------

        >>> from KeithleyClass import *
        >>> name = Keithley('SOL:K6514', 'k1')

        """
        StandardDevice.__init__(self, mnemonic)
        self.pvName = pvName
        self.timeBased = timeBased
        self.keithley = Device(pvName+':', 
                               ('GetMed','SetMed','GetMedRank','SetMedRank','GetAver',
                                'SetAver','GetAverCoun','SetAverCoun','GetNPLC','SetNPLC',
                                'GetAutoZero', 'SetAutoZero','GetZeroCheck','SetZeroCheck',
                                'GetAverTCon','SetAverTCon','GetRange','SetRange',
                                'GetZeroCor','SetZeroCor', 'GetAutoCurrRange','SetAutoCurrRange'
                                'Count','ContinuesMode', 'CNT', 'OneMeasure'))

        self.pvMeasure = PV(pvName+':'+'Measure', auto_monitor=False)
        self._counting = self.isCountingPV()
        self.keithley.add_callback('CNT', self.onStatusChange)

    def getCurrentRange(self):
        """
        Get the value of range.
        Default: Auto range.

        Returns
        -------
        Value: Integer, i.e.: 
        0 (Undefined ZERO), 1 (Indefined UM), 2 (20 mA), 3 (2 mA), 4 (200 uA), 5 (20 uA), 6 (2 uA), 7 (200 nA), 8 (20 nA), 9 (2 nA), 10 (200 pA), 11 (20 pA).
    
        Examples
        --------
        >>> name.getCurrentRange()
        >>> 11
        """

        return self.keithley.get('GetRange')

    def setCurrentRange(self, curange):
        """
        Set the range.

        Parameters
        ----------
        Value: Integer, i.e.: 
        0 (Undefined ZERO), 1 (Indefined UM), 2 (20 mA), 3 (2 mA), 4 (200 uA), 5 (20 uA), 6 (2 uA), 7 (200 nA), 8 (20 nA), 9 (2 nA), 10 (200 pA), 11 (20 pA).

        Examples
        --------
        >>> name.setCurrentRange(5)
        """
        if (curange < 0 or curange > 11):
            raise ValueError('Invalid number - It should be 0 to 11') 
        self.keithley.put('SetRange', curange)
