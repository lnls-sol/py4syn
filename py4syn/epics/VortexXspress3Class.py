"""
Vorter XSPRESS3 class

Python class for Vortex using EPICS area detector IOC.

:platform: Unix
:synopsis: Python class for Vortex with xspress3

.. moduleauthor:: Douglas Araujo<douglas.araujo@lnls.br>
                  Luciano Carneiro Guedes<luciano.guedes@lnls.br>
"""

from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
from epics import PV

from time import sleep, time


class VortexXspress3(StandardDevice, ICountable):
    """
    Class to control Vortex via EPICS.
    Examples
    --------
    """


    RESPONSE_TIMEOUT = 15
    WAIT_ACQUIRING = 0.005


    def onAcquireChange(self, value, **kw):
        self._done = (value == 0)


    def __init__(self, mnemonic, pv):
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
        self.pvAcquire = PV(pv + ':Acquire')
        self.pvStatus = PV(pv + ':Acquire_RBV', callback=self.onAcquireChange)
        self.pvAcquireTime = PV(pv + ':AcquireTime')
        self.pvClear = PV(pv + ':ERASE')

        self.pvMcaCounters = []
        self.pvStatusScan = PV(pv + ':Acquire_RBV.SCAN')
        self.pvStatusScan.put(9)

        # Channels 1-4
        for i in range(1, 5):
            for j in range(1, 5):            
               self.pvMcaCounters.append(PV('{}:C{}_ROI{}:Value_RBV'.format(pv, j, i)))
        P = pv+":HDF5:"
        self.pvClear.put(1, wait=True)
        self.n_extra_dim_pv =PV(P+"NumExtraDims")
        self.x_dim_pv = PV(P+"ExtraDimSizeX")
        self.y_dim_pv = PV(P+"ExtraDimSizeY")
        self.write_mode_pv = PV(P+"FileWriteMode")
        self.file_path_pv = PV(P+"FilePath")
        self.file_name_pv = PV(P+"FileName")
        self.start_capture_pv = PV(P+"Capture")
        self.n_frames = PV(pv+":NumImages")
        numb_frames = 1
        name = 'teste'
        #Stop writing
        self.start_capture_pv.put(0)
        #Set dimensions
        self.n_extra_dim_pv.put(1)
        #points
        self.x_dim_pv.put(numb_frames)
        self.y_dim_pv.put(0)
        #Set Write Mode
        #2=Stream
        self.write_mode_pv.put(2)
        #Set output path
        self.file_path_pv.put("/data/")
        self.file_name_pv.put(name)
        self.n_frames.put(numb_frames)
        self.filenumb =PV(P+"FileNumber")
        self.filenumb.put(0)

	
    def close(self):
        """
        Stops an ongoing acquisition, if any, and puts the EPICS IOC in idle state.
        """
        self._done = 1


    def getIntensity(self, channel=1):
        return self.pvMcaCounters[channel-1].get()


    def getValue(self, **kwargs):
        if(kwargs):                 
            count = 0            
            value = self.getIntensity(kwargs['channel'])
            while (value==0 and count<3):
                sleep(.05) 
                value = self.getIntensity(kwargs['channel'])
                count += 1
            return value


    def setCountTime(self, t):
        """
        Sets the image acquisition time.
        Parameters
        ----------
        t : `float`
            Acquisition time
        """
        self.pvAcquireTime.put(t, wait=True)


    def getAcquireTime(self):
        return self.pvAcquireTime.get()


    def setPresetValue(self, channel, val):
        """
        Dummy method to set initial counter value.
        """
        pass


    def startCount(self):
        """
        Starts acquiring 
        """
        if not self._done:
            raise RuntimeError('Already counting')
        self.pvClear.put(1, wait=True) # clear the ROI value before start a new acquire
        self.start_capture_pv.put(1)
        self.pvAcquire.put(1)
        self._done = 0 # force the confirmation that the detector has already received acquire function
        


    def stopCount(self):
        """
        Stops acquiring. This method simply calls :meth:`close`.
        
        See: :meth:`close`
        """
        self.pvAcquire.put(0)
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
            sleep(self.WAIT_ACQUIRING)
        sleep(0.2)
