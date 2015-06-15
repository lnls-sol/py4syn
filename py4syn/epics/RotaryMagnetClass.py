"""
Rotary Magnet Class

Python Class for EPICS control of Rotary Magnet.

:platform: Unix
:synopsis: Python Class for EPICS control of Rotary Magnet.

.. moduleauthor:: Douglas Bezerra Beniz <douglas.beniz@lnls.br>
"""
from epics import PV, ca
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.IScannable import IScannable

class RotaryMagnet(StandardDevice, IScannable):
    """
    Class to add ICountable support for rotary magnet.

    Examples
    --------
    >>> from py4syn.epics.RotaryMagnetClass import RotaryMagnet
    >>>
    >>> myMagnet = RotaryMagnet('myMagnet')
    >>> myMagnet.setValue(0)
    >>>     
    """
    
    # Callback function for the RotaryMagnet's PV value change
    def onValChange(self, value, **kw):
        self._active = (value == 1)
    
    # Constructor of RotaryMagnet
    def __init__(self, pvRotaryMagnetName="", mnemonic=""):
        StandardDevice.__init__(self, mnemonic)
        self._active = False
        self._done = self.isDone()
        self.pvRotaryMagnetDESC = PV(pvRotaryMagnetName+".DESC")
        self.pvRotaryMagnetVAL = PV(pvRotaryMagnetName+".VAL", self.onValChange)
    
    def getDescription(self):
        """
        Obtain the current description of rotary magnet device or its identification.
        
        Returns
        -------
        `String`
            A detail about the device or its identification.
        """
        return self.pvRotaryMagnetDESC.get()            
    
    def setDescription(self, magnetDescription):
        """
        Method to set a description to the rotary magnet device.
        
        Parameters
        ----------
        `String`
            A detail about the device or its identification.

        Returns
        -------
        `None` 
        """
        self.pvRotaryMagnetDESC.put(magnetDescription)
    
    def getValue(self):
        """
        Obtain the current value of rotary magnet device or its identification.
        
        Returns
        -------
        `integer`
        
        .. note::
            - **1**  -- Active rotary magnet;
            - **0**  -- Inactive rotary magnet.
        """
        return self.pvRotaryMagnetVAL.get()            
    
    def setValue(self, v):
        """
        Method to set a value to the rotary magnet device.
        
        Parameters
        ----------
        `integer`
        
        .. note::
            - **1**  -- Active rotary magnet;
            - **0**  -- Inactive rotary magnet.
        """
        self.pvRotaryMagnetVAL.put(v)
    
    def isActive(self):
        """
        Return whether Rotary Magnet is currently active (set to 1).
        
        Returns
        -------
        `boolean`
        
        .. note::
            - **True**  -- Rotary magnet is active (1);
            - **False** -- Rotary magnet is inactive (0). 
        """
        return self._active
    
    def isDone(self):
        return True
    
    def wait(self):
        while(not self._done):
            sleep(0.001)

    def getLowLimitValue(self):
        """
        Obtain low limit value of rotary magnet.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        `double`
        """
        return -1
    
    def getHighLimitValue(self):
        """
        Obtain high limit value of rotary magnet.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        `double`
        """
        return 2
