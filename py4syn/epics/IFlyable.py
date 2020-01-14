"""Scannable Interface

Python interface to support Abstract methods related to FlyScan process.

:platform: Unix
:synopsis: Python Interface with Abstract methods for FlyScan process (FlyScannable Devices).

.. moduleauthor:: Gabriel Previato de Andrade <gabriel.andrade@lnls.br>
    .. note:: 14/01/2020 [gabrielpreviato]  first version released
"""
from abc import ABCMeta, abstractmethod


class IFlyable:
    """

    Python interface to be implemented in all devices in order to create default methods for FlyScan process

    A flyscannable is any device in which the flyscan process is feasible to be performed.

    """

    @abstractmethod
    def getTriggerMode(self):
        """
        Abstract method to get the flyscannable device trigger mode.

        Parameters
        ----------
        None

        Returns
        -------
        `string`
        """

        raise NotImplementedError

    @abstractmethod
    def getTriggerParams(self):
        """
        Abstract method to get the flyscannable device trigger parameters.

        Parameters
        ----------
        None

        Returns
        -------
        `dict`
        """

        raise NotImplementedError

    @abstractmethod
    def setTriggerMode(self, m):
        """
        Abstract method to set the trigger mode of a flyscannable device.

        Parameters
        ----------
        m : mode
            The device mode to be set.

        Returns
        -------
        out : None
        """

        raise NotImplementedError

    @abstractmethod
    def setTriggerParams(self, d):
        """
        Abstract method to set the trigger parameters of a flyscannable device.

        Parameters
        ----------
        d : dictionary
            The device parameters to be set.

        Returns
        -------
        out : None
        """

        raise NotImplementedError

    @abstractmethod
    def startTrigger(self):
        """
        Abstract method to start flyscannable device trigger transmission.

        Parameters
        ----------
        None

        Returns
        -------
        out : None
        """

        raise NotImplementedError

    @abstractmethod
    def reset(self):
        """
        Abstract method to reset flyscannable device trigger.

        Parameters
        ----------
        None

        Returns
        -------
        out : None
        """

        raise NotImplementedError
