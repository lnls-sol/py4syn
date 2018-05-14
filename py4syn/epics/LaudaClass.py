"""Lauda temperature controller class

Python class for Lauda temperature controllers

:platform: Unix
:synopsis: Python class for Lauda temperature controllers

.. moduleauthor:: Henrique Dante de Almeida <henrique.almeida@lnls.br>

"""
from threading import Event

from epics import Device, ca

from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.utils.timer import Timer

class Lauda(StandardDevice, IScannable):
    """
    Class to control Lauda temperature controllers via EPICS.

    Examples
    --------
    >>> from py4syn.epics.LaudaClass import Lauda
    >>>    
    >>> def showTemperature(pv):
    ...    lauda = Lauda(pv, 'lauda')
    ...    print('Temperature is: %d' % lauda.getValue())
    ...
    >>> def setTemperature(lauda, temperature):
    ...    lauda.setValue(temperature)
    ...    lauda.run()
    """

    EPSILON = 0.1

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

        self.lauda = Device(pvName + ':', ['BLEVEL', 'BOVERTEMP', 'BPOWER', 'BSP',
                            'BSTATS', 'BTEMP', 'BTN', 'BTHERMOSTATS', 'WSP', 'WSTART',
                            'ETEMP', 'WPUMP', 'WSTOP', 'WTN'])
        self.newTemperature = Event()
        self.lauda.add_callback('BTEMP', self.onTemperatureChange)
        # Skip initial callback
        self.newTemperature.wait(1)

    def __str__(self):
        return '%s (%s)' % (self.getMnemonic(), self.pvName)

    def getValue(self):
        """
        Returns the current measured temperature.

        Returns
        -------
        `int`
        """
        return self.lauda.get('BTEMP')

    def getRealPosition(self):
        """
        Returns the same as :meth:`getValue`.

        See: :meth:`getValue`

        Returns
        -------
        `int`
        """
        return self.getValue()

    def onTemperatureChange(self, **kwargs):
        """
        Helper callback that indicates when the measured temperature changed.
        """
        self.newTemperature.set()

    def setVelocity(self, r):
        """
        Dummy method setVelocity()

        Parameters
        ----------
        r : `float`
            Ramp speed in °C/min
        """
        pass

    def setValue(self, v):
        """
        Changes the temperature to a new value.

        Parameters
        ----------
        v : `int`
            The target temperature in °C
        """
        self.lauda.put('WSP', v)
        self.run()
        self.requestedValue = v

    def wait(self):
        """
        Blocks until the requested temperature is achieved.
        """

        ca.flush_io()
        self.newTemperature.clear()

        while abs(self.getValue()-self.requestedValue) > self.EPSILON:
            # Give up after 60 seconds without an update
            if not self.newTemperature.wait(60):
                break

            self.newTemperature.clear()

    def getLowLimitValue(self):
        """
        Returns the controller low limit temperature.

        Returns
        -------
        `int`
        """
        return -20

    def getHighLimitValue(self):
        """
        Returns the controller high limit temperature.

        Returns
        -------
        `int`
        """
        return 200

    def run(self):
        """
        Starts or resumes executing the current temperature program.
        """
        self.lauda.put('WSTART', 1)

    def stop(self):
        """
        Stops executing the current temperature program and puts the device in idle state.
        In the idle state, the device will not try to set a target temperature.
        """
        self.lauda.put('WSTOP', 1)

    def setPumpSpeed(self, speed):
        """
        Changes the pump speed.

        Parameters
        ----------
        speed : `int`
            The requested pump speed, ranging from 1 to 8.
        """

        if speed < 1 or speed > 8:
            raise ValueError('Invalid speed')

        self.lauda.put('WPUMP', speed)

    def getInternalTemp(self):
        """
        Same as :meth:`getValue`.

        See :meth:`getValue`

        Returns
        -------
        `int`
        """
        return self.getValue()

    def getExternalTemp(self):
        """
        Returns the device's external temperature.

        Returns
        -------
        `int`
        """
        return self.lauda.get('ETEMP')

    def getLevel(self):
        """
        Returns the device's bath level.

        Returns
        -------
        `int`
        """
        return self.lauda.get('BLEVEL')

    def getSetPoint(self):
        """
        Returns the current target temperature.

        Returns
        -------
        `int`
        """
        return self.lauda.get('BSP')

    def getPower(self):
        """
        Returns the current device power.

        Returns
        ----------
        `int`
        """
        return self.lauda.get('BPOWER')

    def getOverTemp(self):
        """
        Returns the maximum temperature software defined limit.

        Returns
        ----------
        `int`
        """
        return self.lauda.get('BOVERTEMP')

    def getTN(self):
        """
        Returns
        ----------
        `int`
        """
        return self.lauda.get('BTN')

    def getStatus(self):
        """
        Returns the device status word.

        Returns
        ----------
        `int`
        """
        return self.lauda.get('BSTATS')

    def getThermoStatus(self):
        """
        Returns the device thermostat error word.

        Returns
        ----------
        `int`
        """
        return self.lauda.get('BTHERMOSTATS')

    def changeSetPoint(self, val):
        """
        Same as :meth:`setValue`.

        See :meth:`setValue`

        Parameters
        ----------
        val : `int`
            The requested temperature.
        """
        self.setValue(val)

    def changePump(self, val):
        """
        Same as :meth:`setPumpSpeed`.

        See :meth:`setPumpSpeed`

        Parameters
        ----------
        val : `int`
            The requested pump speed.
        """
        self.setPumpSpeed(val)

    def changeTN(self, val):
        self.lauda.put('WTN', val)

    def start(self):
        """
        Same as :meth:`run`.

        See :meth:`run`
        """
        self.run()
