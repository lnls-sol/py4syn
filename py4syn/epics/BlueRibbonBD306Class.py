"""Blue Ribbon Corp Bulldog 306 Class

Python Class for EPICS Blue Ribbon Corp Bulldog 306 device

:platform: Unix
:synopsis: Python Class for EPICS Blue Ribbon Corp Bulldog 306 device

.. moduleauthor:: Douglas Bezerra Beniz <douglas.beniz@lnls.br>
    .. note:: 18/04/2017 [douglas.beniz]  first version released
"""

from epics import PV
from time import sleep

from py4syn.epics.StandardDevice import StandardDevice

class BlueRibbonBD306(StandardDevice):
    """
    Python class to help configuration and control of Blue Ribbon Corp Bulldog 306 devices over EPICS.

    Examples
    --------
    >>> from py4syn.epics.BlueRibbonBD306Class import BlueRibbonBD306
    >>> bd306 = BlueRibbonBD306("BL:BD306A", 'bd306a')
    >>>
    """

    def __init__ (self,pvPrefix="", mnemonic=""):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`

        Parameters
        ----------
        pvPrefix : `string`
            Blue Ribbon BD306's device base naming of the PV (Process Variable)
        mnemonic : `string`
            Blue Ribbon BD306's mnemonic
        """
        StandardDevice.__init__(self, mnemonic)

        self.pvP1 = PV(pvPrefix + ":P1")
        self.pvP2 = PV(pvPrefix + ":P2")

    def getPressure1(self):
        return self.pvP1.get()

    def getPressure2(self):
        return self.pvP2.get()

