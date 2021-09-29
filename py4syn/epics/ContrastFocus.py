
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
from epics.devices.ad_base import AD_Camera
from epics.devices.ad_fileplugin import AD_FilePlugin
from epics.devices.ad_image import AD_ImagePlugin
from epics import PV
import epics

import numpy as np
from time import sleep, time


class ContrastFocus(StandardDevice, ICountable):
    """
    Class to control Mogno's camera contrast via EPICS.
    Examples
    --------
    """
    def onAcquireChange(self, value, **kw):
        self._done = (value == 0)

    def __init__(self, mnemonic, pv, device, fileplugin):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`
        Parameters
        ----------
        mnemonic : `string`
            A mnemonic for the detector
        pv : `string`
            Base name of the EPICS process variable
        """
        super().__init__(mnemonic)
        self._done = 1
        self.detector_name = pv+':'+device+':'
        self.write_name = pv+':'+fileplugin+':'
        self.detector = AD_Camera(self.detector_name)
        self.detector.add_pv(self.detector_name+"Acquire_RBV",
                             attr='Scan') 
        self.image = AD_ImagePlugin(pv+":image1:")
        self.highestContrast = None
        self.t = 0

        self.detector.ImageMode = 0
        self.detector.TriggerMode = 1

        self.detector.add_callback("Acquire_RBV",
                                   callback=self.onAcquireChange)
	
    def getContrast(self):
        arrayData = self.image.ArrayData.astype(np.uint16) # image array
        self.contrast = np.std(arrayData)

        #if(self.highestContrast == None):
        #    self.highestContrast = self.contrast
        #if(self.contrast > self.highestContrast):
        #    self.highestContrast = self.contrast
        
        return self.contrast

    def close(self):
        """
        Stops an ongoing acquisition, if any, and puts the EPICS IOC in idle state.
        """
        self._done = 1


    def getIntensity(self, channel=1):
        pass


    def getValue(self, **kwargs):
        contrast = self.getContrast()
        return contrast


    def setCountTime(self, t):
        """
        Sets the image acquisition time.
        Parameters
        ----------
        t : `float`
            Acquisition time
        """
        self.t = t
        self.detector.Acquire = self.t
        #print('setCountTime', self.t)


#    def getAcquireTime(self):
#        pass


    def setPresetValue(self, channel, val):
        """
        Dummy method to set initial counter value.
        """
        pass


    def startCount(self):
        """
        Starts acquiring 
        """
        self.detector.Acquire = 1
        self.detector.AcquireTime = self.t
        self._done = 0
        


    def stopCount(self):
        """
        Stops acquiring. This method simply calls :meth:`close`.
        
        See: :meth:`close`
        """

        self.close()


    def canMonitor(self):
        """
        Returns false indicating that vortex cannot be used as a counter monitor.
        """
        return False


    def canStopCount(self):
        """
        Returns true indicating that vortex has a stop command.
        """
        return True

    def isCounting(self):
        """
        Returns true if the detector is acquiring, or false otherwise.
        Returns
        -------
        `bool`
        """
        return not self._done


    def wait(self):
        """
        Blocks until the acquisition completes.
        """
        while not self._done:
            epics.poll(evt=1.e-5, iot=0.1)
