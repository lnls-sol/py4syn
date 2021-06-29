"""CompactRIO Analog Acquisition

Class for acquiring CompactRIO analog inputs (via PV or file) with automated
control of downsampling rate (averaging time).

:platform: Unix
:synopsis: Python3 class for analog acquisitions using CompactRIO's IOC

.. moduleauthors:: Carlos Doro Neto <carlos.doro@lnls.br>
                   João Leandro de Brito Neto <joao.brito@lnls.br>
"""

from os.path import join
from time import sleep
from epics import PV
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable


class CompactRIOAnalog(StandardDevice, ICountable):

    def __init__(self, mnemonic, pvName, tdms=False):
        """

        parameters
        ----------
        mnemonic : `string`
            Class mnemonic, see :class:`py4syn.epics.StandardDevice`.
        pvName : `string`
            PV name.
        tdms : `bool`
            If tdms is True uses NI tdms files instead of EPICS PVs.
        """

        super().__init__(mnemonic)

        self.tdms = tdms

        pvPrefix = pvName[:12]

        self._pv = PV(pvName)
        self._pvAvgTime = PV(pvPrefix + "PvAvgTime")
        self._fileAvgTime = PV(pvPrefix + "FileAvgTime")
        self._acquireTrigger = PV(pvPrefix + "AnalogAcqSwTrigger")
        self._filedir = PV(pvPrefix + "AnalogAcqFilepath")
        self._filename = PV(pvPrefix + "AnalogAcqFilename")

        assert self._pv.wait_for_connection()
        assert self._pvAvgTime.wait_for_connection()
        assert self._fileAvgTime.wait_for_connection()
        assert self._acquireTrigger.wait_for_connection()
        assert self._filedir.wait_for_connection()
        assert self._filename.wait_for_connection()

    # ICountable methods overriding

    def getValue(self, **kwargs):
        """If self.tdms is set returns the analogic reading (after downsampling)
           by opening the TDMS file, otherwise gets the value from the PV.

        returns
        -------
        `double`
        """

        if self.tdms:
            return self._fileGetValue()
        else:
            return self._pv.get()

    def setCountTime(self, t):
        """Sets the downsampling period. Note that TDMS files and PVs have
           independent values and are controlled by the self.tdms flag.

        parameters
        ----------
        t : `double`
            The desired downsampling time.
        """

        if self.tdms:
            self._fileAvgTime.put(t, wait=True)
        else:
            self._pvAvgTime.put(t, wait=True)

    def setPresetValue(self, channel, val):
        """Not available on CompactRIO. Does nothing."""
        pass

    def startCount(self):
        """Sync the downsampling phase and starts saving data to TDSM file.
           For more detailed information contact <joao.brito@lnls.br>"""
        self._acquireTrigger.put(1, wait=True)

    def stopCount(self):
        """Stops saving data to TDSM file."""
        self._acquireTrigger.put(0, wait=True)

    def canStopCount(self):
        """CompactRIO cannot stop a measurement half way through."""
        return False

    def canMonitor(self):
        """CompactRIO cannot work as or with a spec monitor."""
        return False

    def isCounting(self):
        """Check whether CompactRIO is acquiring or not.

        Returns
        -------
        `boolean`
            True if it is acquiring, False otherwise.
        """

        return self._acquireTrigger.get()

    def wait(self):
        """This is a workaround! CompactRIO does NOT set AnalogAcqSwTrigger back
           to zero after it is done acquiring so we must set it manually."""
        if self.tdms:
            sleep(self._fileAvgTime.get())
        else:
            sleep(self._pvAvgTime.get())
        self.stopCount()

    # CompactRIOAnalog specific functions

    def _fileGetValue(self):
        """Not implemented yet."""
        raise NotImplementedError
        # from nptdms import TdmsFile

    def _fileGetPath(self):
        """Returns the path of the TDMS file in which the data is being saved.

        Returns
        -------
        `string`
        """

        return join(self._filedir.get(), self._filename.get())
