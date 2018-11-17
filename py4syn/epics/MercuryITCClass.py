"""MercuryITC temperature controller class

Python class for MercuryITC temperature controllers

:platform: Unix
:synopsis: Python class for MercuryITC temperature controllers

.. moduleauthor:: Gabriel de Souza Fedel <gabriel.fedel@lnls.br>

"""
import time
from threading import Event

from epics import Device, ca
from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice

DELTA = 0.5

class MercuryITC(IScannable, StandardDevice):
    """
    Class to control MercuryITC temperature controllers via EPICS.
    """

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

        self.device = Device(pvName + ':', ['READ_TEMP_LOOP_HSET', 'READ_TEMP_LOOP_TSET','READ_TEMP_SIG_TEMP',
        'READ_RAMP_TEMP','READ_LEVEL_METER','READ_SAMPLE_FLOW','READ_SHIELD_FLOW',
        'SET_RAMP_TEMP', 'SET_TEMP_LOOP_TSET'])

        self.newTemp = Event()
        self.pvName = pvName

    def getValue(self):
        """
        Returns the current measured temperature.

        Returns
        -------
        `float`
        """
        return self.device.get('READ_TEMP_SIG_TEMP')

    def getSP(self):
        """
        Returns the current Set Point.

        Returns
        -------
        `float
        """
        time.sleep(0.5)
        return self.device.get('SET_TEMP_LOOP_TSET')

    def getTarget(self):
        """
        Returns the current target temperature.

        Returns
        -------
        `float`
        """
        time.sleep(0.5)
        return self.device.get('READ_TEMP_LOOP_TSET')

    def getRealPosition(self):
        """
        Returns the same as :meth:`getValue`.

        See: :meth:`getValue`

        Returns
        -------
        `float`
        """
        return self.getValue()

    def getRampRate(self):
        """
        Returns the defined ramp rate.

        Returns
        -------
        `int`
        """
        return self.device.get('READ_RAMP_TEMP')

    def getLowLimitValue(self):
        """
        Returns the controller low limit temperature.

        Returns
        -------
        `float`
        """
        return 90

    def getHighLimitValue(self):
        """
        Returns the controller high limit temperature.

        Returns
        -------
        `float`
        """
        return 500

    def getRRHighLimitValue(self):
        return 25.0

    def getRRLowLimitValue(self):
        return 1.0

    def setRampRate(self, value):
        self.device.put('SET_RAMP_TEMP', value)

    def stop(self):
        '''Define SP to minimum temperature on maximum ramp rate'''
        self.setRampRate(self.getRRHighlimitValue)
        self.setValue(self.getLowLimitValue())

    def hold(self):
        '''Set temperature to actual temperature'''
        actual_temp = self.getValue()
        self.setValue(actual_temp)

    def setValue(self, value, wait = False):
        if value < self.getLowLimitValue() or value > self.getHighLimitValue():
            raise ValueError('Value exceeds limits')
        self.device.put('SET_TEMP_LOOP_TSET ', value)
        if wait:
            self.wait()

    def getP(self):
        """
        Return the current P value at the furnace

        Returns
        -------
        `double`
        """
        getPV = self.device.PV('P')

        return getPV.get()

    def getI(self):
        """
        Return the current I value at the furnace

        Returns
        -------
        `double`
        """
        getPV = self.device.PV('I')

        return getPV.get()

    def getD(self):
        """
        Return the current D value at the furnace

        Returns
        -------
        `double`
        """
        getPV = self.device.PV('D')

        return getPV.get()

    def getPower(self):
        """
        Return the current Power value at the furnace

        Returns
        -------
        `double`
        """
        getPV = self.device.PV('READ_TEMP_LOOP_HSET')

        return getPV.get()

    def getLevelMeter(self):
        """
        Return the current N2 Level Meter of the dewar

        Returns
        -------
        `double`
        """
        getPV = self.device.PV('READ_LEVEL_METER')

        return getPV.get()


    def reachTemp(self):
        if self.getValue() < self.getSP() + DELTA and \
          self.getValue() > self.getSP() - DELTA:
          return True
        return False

    def wait(self):
        """
        Blocks until the requested temperature is achieved.
        """
        self.newTemp.clear()
        while not self.reachTemp():
            ca.flush_io()
            self.newTemp.wait(5)
            self.newTemp.clear()
