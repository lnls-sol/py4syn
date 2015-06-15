"""Standard Device Class

Python Class for Standard Device informations.

:platform: Unix
:synopsis: Python Class for Standard Device informations.

.. moduleauthor:: Hugo Henrique Slepicka <hugo.slepicka@lnls.br>
    .. note:: 30/08/2014 [hugo.slepicka]  first version released
"""

class StandardDevice():
    """
    Class to be inherited by all devices implemented in order to have common information in all devices.
    """    
    def __init__(self, mnemonic):
        """
        **Constructor**

        Parameters
        ----------
        mnemonic : `string`
            Device mnemonic
        """        
        self.__mnemonic = mnemonic
        
    def getMnemonic(self):
        """
        Returns the device mnemonic

        Returns
        -------
        `string`
        """        
        return self.__mnemonic
    
    def setMnemonic(self, mnemonic):
        """
        Set the device mnemonic

        Parameters
        ----------
        mnemonic : `string`
            Device mnemonic
        """            
        self.__mnemonic = mnemonic