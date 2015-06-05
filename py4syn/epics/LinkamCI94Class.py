"""Linkam CI94 temperature controller class

Python class for Linkam CI94 temperature controllers

:platform: Unix
:synopsis: Python class for Linkam CI94 temperature controllers

.. moduleauthor:: Henrique Dante de Almeida <henrique.almeida@lnls.br>

"""
from threading import Event

from epics import Device, ca

from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.utils.timer import Timer

class LinkamCI94(StandardDevice, IScannable):
    """
    Class to control Linkam CI94 temperature controllers via EPICS.
    """

    STATUS_STOPPED = 0
    PUMP_AUTOMATIC = 0
    PUMP_MANUAL = 1

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
        self.done = Event()
        self.newTemperature = Event()
        self.pending = bool(self.linkam.get('pending'))
        self.setRate(5)
        self.linkam.add_callback('pending', self.onPendingChange)
        self.linkam.add_callback('temp', self.onTemperatureChange)

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

    def onPendingChange(self, value, **kwargs):
        """
        Helper callback that tracks when the IOC finished changing
        to a requested temperature.
        """
        self.pending = bool(value)
        if not self.pending:
            self.done.set()

    def onTemperatureChange(self, **kwargs):
        """
        Helper callback that indicates when the measured temperature changed.
        """
        self.newTemperature.set()

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

    def setValue(self, v):
        """
        Changes the temperature to a new value. The speed that the new temperature is
        reached is set with :meth:`setRate`. The default rate is 5 °C/minute.

        See: :meth:`setRate`

        Parameters
        ----------
        v : `float`
            The target temperature in °C
        """
        self.done.clear()
        self.pending = True
        self.requestedValue = v
        self.linkam.put('setLimit', v)

        if not self.isRunning():
            self.run()

    def wait(self):
        """
        Blocks until the requested temperature is achieved.
        """
        if not self.pending:
            return

        # Waiting is done in two steps. First step waits until the IOC deasserts
        # the pending flag to indicate a complete operation. Second step waits util the
        # measured temperature reaches the requested temperature.
        ca.flush_io()
        self.done.wait()

        self.newTemperature.clear()
        timeout = Timer(7)
        while self.getValue() != self.requestedValue and timeout.check():
            self.newTemperature.wait(1)
            self.newTemperature.clear()

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
        self.setPumpSpeed(0)
        self.linkam.put('stop', 1)

    def setPumpSpeed(self, speed):
        """
        Changes the nitrogen pump speed, or enables automatic pump speed control.

        .. note::
            The Linkam front panel only has 5 LEDs to indicate speed, but internally
            it supports 30 different speed levels.

        Parameters
        ----------
        speed : `int`
            The requested pump speed, ranging from 0 (pump off) to 30 (pump top speed),
            or -1 to enable automatic pump control.
        """

        if speed < -1 or speed > 30:
            raise ValueError('Invalid speed')

        if speed == -1:
            self.linkam.put('pumpMode', self.PUMP_AUTOMATIC)
            return

        self.linkam.put('pumpMode', self.PUMP_MANUAL, wait=True)
        self.linkam.put('setSpeed', speed)
