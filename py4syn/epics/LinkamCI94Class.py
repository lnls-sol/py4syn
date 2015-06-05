"""Linkam CI94 temperature controller class

Python class for Linkam CI94 temperature controllers

:platform: Unix
:synopsis: Python class for Linkam CI94 temperature controllers

.. moduleauthor:: Henrique Dante de Almeida <henrique.almeida@lnls.br>

"""
from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice

class LinkamCI94(StandardDevice, IScannable):
    """
    Class to control Linkam CI94 temperature controllers via EPICS.
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
        self.pvName = pvName

    def __str__(self):
        return '%s (%s)' % (self.getMnemonic(), self.pvName)
