"""Eurotherm 2408 temperature controller class

Python class for Eurotherm 2408 temperature controllers

:platform: Unix
:synopsis: Python class for Eurotherm 2408 temperature controllers

.. moduleauthor:: Gabriel de Souza Fedel <gabriel.fedel@lnls.br>

"""
import time
from threading import Event

from epics import Device, ca
from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice

DELTA = 0.5

class Eurotherm2408(StandardDevice, IScannable):
    """
    Class to control Eurotherm 2408 temperature controllers via EPICS.
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

        self.device = Device(pvName + ':', ['PV:RBV', 'SP','RR', 'RR:RBV',
        'WSP:RBV', 'O:RBV'])

        self.newTemp = Event()
        self.pvName = pvName



    def getValue(self):
        """
        Returns the current measured temperature.

        Returns
        -------
        `float`
        """
        return self.device.get('PV:RBV')


    def getSP(self):
        """
        Returns the current Set Point.

        Returns
        -------
        `float
        """
        time.sleep(0.5)
        return self.device.get('SP')


    def getTarget(self):
        """
        Returns the current target temperature.

        Returns
        -------
        `float`
        """
        time.sleep(0.5)
        return self.device.get('WSP:RBV')

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
        return self.device.get('RR:RBV')

    def getLowLimitValue(self):
        """
        Returns the controller low limit temperature.

        Returns
        -------
        `float`
        """
        return 25.0

    def getHighLimitValue(self):
        """
        Returns the controller high limit temperature.

        Returns
        -------
        `float`
        """
        return 1000

    def getRRHighLimitValue(self):
        return 25.0

    def getRRLowLimitValue(self):
        return 1.0

    def setRampRate(self, value):
        self.device.put('RR', value)

    def stop(self):
        '''Define SP to minimum temperature on maximum ramp rate'''
        self.setRampRate(self.getRRHighLimitValue)
        self.setValue(self.getLowLimitValue())

    def hold(self):
        '''Set temperature to actual temperature'''
        actual_temp = self.getValue()
        self.setValue(actual_temp)

    def setValue(self, value, wait = False):
        if value < self.getLowLimitValue() or value > self.getHighLimitValue():
            raise ValueError('Value exceeds limits')
        self.device.put('SP', value)
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
        getPV = self.device.PV('O:RBV')

        return getPV.get()

    def reachTemp(self):
        if self.getValue() < self.getTarget() + DELTA and \
          self.getValue() > self.getTarget() - DELTA:
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

    def setVelocity(self, velo):
        """
        Same as :meth:`setRampRate`.

        See: :meth:`setRampRate`

        Parameters
        ----------
        r : `float`
            Ramp speed
        """
        self.setRampRate(velo)

