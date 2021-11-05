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
        self._sampling_rate = 1e5
        pvPrefix = pvName[:12]

        # We assume that the CompactRIO is running the new firmware and if
        # we cannot connect to the averaging time PVs we change to the old one.

        self._firmware = "new"
        self._pvAvgTime = PV(pvPrefix + "PvAvgTime")
        self._fileAvgTime = PV(pvPrefix + "FileAvgTime")

        if not (self._pvAvgTime.wait_for_connection() and
                self._fileAvgTime.wait_for_connection()):

            self._firmware = "old"
            self._pvAvgTime = PV(pvPrefix + "PvDownsampling")
            self._fileAvgTime = PV(pvPrefix + "FileDownsampling")
            assert self._pvAvgTime.wait_for_connection()
            assert self._fileAvgTime.wait_for_connection()

        self._pv = PV(pvName)
        self._acquireTrigger = PV(pvPrefix + "AnalogAcqSwTrigger")
        self._filedir = PV(pvPrefix + "AnalogAcqFilepath")
        self._filename = PV(pvPrefix + "AnalogAcqFilename")

        assert self._pv.wait_for_connection()
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

        if self._firmware == "old":
            t *= self._sampling_rate

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
            sleep_time = self._fileAvgTime.get()
        else:
            sleep_time = self._pvAvgTime.get()

        if self._firmware == "old":
            sleep_time /= self._sampling_rate

        sleep(sleep_time)
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
