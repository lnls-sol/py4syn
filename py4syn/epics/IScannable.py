"""Scannable Interface

Python interface to support Abstract methods related to Scan process.

:platform: Unix
:synopsis: Python Interface with Abstract methods for Scan process (Scannable Devices). 

.. moduleauthor:: Hugo Henrique Slepicka <hugo.slepicka@lnls.br>
    .. note:: 22/07/2014 [hugo.slepicka]  first version released
"""

from abc import ABCMeta, abstractmethod

class IScannable:
    """

    Python interface to be implemented in all devices in order to create default methods for Scan process

    A scannable is any device in which the scan process is feasible to be performed.

    """
    @abstractmethod
    def getValue(self):
        """
        Abstract method to get the current value of a scannable device.

        Parameters
        ----------
        None

        Returns
        -------
        out : value
            Returns the current value of the device. Type of the value depends on device settings.
        """

        raise NotImplementedError

    @abstractmethod
    def setValue(self, v):
        """
        Abstract method to set the target value of a scannable device.

        Parameters
        ----------
        v : value
            The target value to be set.

        Returns
        -------
        out : None
        """

        raise NotImplementedError

    @abstractmethod
    def wait(self):
        """
        Abstract method to wait for a scannable device to reach the desired value.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        raise NotImplementedError

    @abstractmethod
    def getLowLimitValue(self):
        """
        Abstract method to get the scannable device software low limit value

        Parameters
        ----------
        None

        Returns
        -------
        `double`
        """

        raise NotImplementedError

    @abstractmethod
    def getHighLimitValue(self):
        """
        Abstract method to get the scannable device software high limit value

        Parameters
        ----------
        None

        Returns
        -------
        `double`
        """

        raise NotImplementedError
