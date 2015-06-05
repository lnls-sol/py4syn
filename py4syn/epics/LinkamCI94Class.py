"""Linkam CI94 temperature controller class

Python class for Linkam CI94 temperature controllers

:platform: Unix
:synopsis: Python class for Linkam CI94 temperature controllers

.. moduleauthor:: Henrique Dante de Almeida <henrique.almeida@lnls.br>

"""
from epics import Device

from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice

class LinkamCI94(StandardDevice, IScannable):
    """
    Class to control Linkam CI94 temperature controllers via EPICS.
    """

    STATUS_STOPPED = 0

    def __init__(self, pvName, mnemonic):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`

        Parameters
        ----------
        pvName : `string`
            Power supply base naming of the PV (Process Variable)
        mnemonic : `string`
            Temperature controller mnemonic
        """
        super().__init__(mnemonic)
        self.pvName = pvName

        self.linkam = Device(pvName + ':', ['setRate', 'setLimit', 'pending', 'temp',
                                            'stop', 'setSpeed', 'pumpMode', 'status',
                                            'start'])
    def __str__(self):
        return '%s (%s)' % (self.getMnemonic(), self.pvName)

    def isRunning(self):
        """
        Returns true if the controller is in program mode. Whenever it is program mode,
        it is following a target temperature.

        Returns
        -------
        `bool`
        """

        v = self.linkam.get('status')
        return v != self.STATUS_STOPPED

    def getValue(self):
        """
        Returns the current measured temperature.

        Returns
        -------
        `float`
        """
        return self.linkam.get('temp')

    def getRealPosition(self):
        """
        Returns the same as :meth:`getValue`.

        See: :meth:`getValue`

        Returns
        -------
        `float`
        """
        return self.getValue()

    def setRate(self, r):
        """
        Sets the ramp speed in degrees per minutes for use with :meth:`setValue`.

        See: :meth:`setValue`

        Parameters
        ----------
        r : `float`
            Ramp speed in °C/min
        """
        self.linkam.put('setRate', r)

    def getLowLimitValue(self):
        """
        Returns the controller low limit temperature.

        Returns
        -------
        `float`
        """
        return -196

    def getHighLimitValue(self):
        """
        Returns the controller high limit temperature.

        Returns
        -------
        `float`
        """
        return 1500

    def run(self):
        """
        Starts or resumes executing the current temperature program.
        """
        self.linkam.put('start', 1)

    def stop(self):
        """
        Stops executing the current temperature program, stops the nitrogen pump and puts
        the device in idle state. In the idle state, the device will not try to set a
        target temperature.
        """
        self.linkam.put('stop', 1)
