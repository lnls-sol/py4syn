"""
AreaDetector class

Python class for AreaDetector devices using EPICS area detector IOC.

:platform: Unix
:synopsis: Python class for AreaDetector devices

.. moduleauthor::   Luciano Carneiro Guedes<luciano.guedes@lnls.br>
"""

from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
from epics import PV, poll
from epics.devices.ad_base import AD_Camera
from epics.devices.ad_fileplugin import AD_FilePlugin
from time import sleep, time


class AreaDetectorClass(StandardDevice, ICountable):
    """
    Class to control AreaDetector via EPICS.
    Examples
    --------
    """


    def onAcquireChange(self, value, **kw):
        self._done = (value == 0)

    def onArrayCounterChange(self, value, **kw):
        self._done = (value != self.counter)
        if value != self.counter:
            self.counter = value 


    def __init__(self, mnemonic, pv,device, fileplugin,
                 write, autowrite, path,trigger):
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
        self.timi = time()
        self.counter= None,
        self.detector_name = pv+':'+device+':'
        self.write_name = pv+':'+fileplugin+':'
        self.path = path
        self.detector = AD_Camera(self.detector_name)
        self.detector.add_pv(self.detector_name+"Acquire_RBV",
                             attr='Scan')
        self.trigger = trigger

        self.detector.Acquire = 0
        if self.trigger == 'External':
            print("External")
            self.setImageMode(2)
            self.detector.add_callback("ArrayCounter_RBV",
                                   callback=self.onArrayCounterChange)
        else:
            self.detector.add_callback("Acquire_RBV",
                                   callback=self.onAcquireChange)
            self.setImageMode(0)

        self.detector.Scan = 9
        self.detector.ImageMode = self.getImageMode()
        self.detector.AcquirePeriod = 0
        self.autowrite = autowrite

        if write and autowrite:
            self.file = AD_FilePlugin(self.write_name)
            self.file.add_pv(self.write_name+"NumExtraDims",
                             attr="NumExtraDims")
            self.file.add_pv(self.write_name+"ExtraDimSizeX",
                             attr="ExtraDimSizeX")
            self.file.add_pv(self.write_name+"ExtraDimSizeY",
                             attr="ExtraDimSizeY")
            self.file.EnableCallbacks = 1
            for i in range (3,10):
                self.file.add_pv(self.write_name+"ExtraDimSize"+str(i),
                                 attr="ExtraDimSize"+str(i))

            self.setFilePath(self.path)
            if self.trigger == 'External':
                self.setImageMode(2)
            else:
                self.setImageMode(2)
   
            self.setEnableCallback(1)
            self.setAutoSave(1)
            self.setWriteMode(1)
            self.setOutputFormat("%s%s_%03d.hdf5")
            self.stopCapture()
    
        if self.trigger == 'External':
            self.setTriggerMode(4)
        else:
            self.setTriggerMode(4)
        self.detector.ImageMode = self.getImageMode()


    def getNframes(self):
        """
        Gets the number of frames to acquire.
        
        Returns
        ----------
        nframes : `int`
            The name of the image.
        """
        return self._nframes

    def setNframes(self,val):
        """
        Sets the number of frames to acquire.
        
        Parameters
        ----------
        nframes : `int`
            The name of the image.
        """
        self._nframes = val
    
    def getFileName(self):
        """
        Returns the output image file name.
        
        Returns
        ----------
        name : `string`
            The name of the image.
        """
        return self._filename

    def setFileName(self,val):
        """
        Sets the output image file name. The image will be saved with this name
        after the acquisition.
        
        Parameters
        ----------
        name : `string`
            The name of the image.
        """
        self._filename = val
        
    def getFilePath(self):
        """
        Gets the output image file path. The image will be saved in this location
        after the acquisition.
        
        Parameters
        ----------
        name : `string`
            The path of location to save the image.
        """
        return self._filepath


    def setFilePath(self,val):
        """
        Sets the output image file path. The image will be saved in this location
        after the acquisition.
        
        Parameters
        ----------
        name : `string`
            The path of location to save the image.
        """
        self._filepath = val
        
    def getImageMode(self):
        """
        Gets the image mode. 
 
        Returns
        ----------
        _imagemode : `int`
            The value of one of these options.
            0 - Single 
            1 - Multiple
            2 - Continuous
        """
        return self._imagemode

    def setImageMode(self,val):
        """
        Sets the image mode. 
        
        Paramters
        ----------
        _imagemode : `int`
            The value of one of these options.
                0 - Single 
                1 - Multiple
                2 - Continuous
        """
        self._imagemode = val
    
    def getTriggerMode(self):
        """
        Gets the trigger mode. 
        
        Returns
        ----------
        _triggermode : `int`
            The value of one of these options:
                0 - Internal 
                1 - External
        """
        return self._triggermode

    def setTriggerMode(self,val):
        """
        Sets the trigger mode. 
        
        Returns
        ----------
        _triggermode : `int`
            The value of one of these options:
                0 - Internal 
                1 - External
        """
        self._triggermode = val    

    def getEnableCallback(self):
        """
        Gets if the Pluging to Write Files is enabled. 
        
        Returns
        ----------
        _enablecallbak : `int`
            The value of one of these options:
                0 - ON
                1 - OFF
        """
        return self._enablecallbak

    def setEnableCallback(self,val):
        """
        Enables the Pluging to Write Files. 
        
        Parameters
        ----------
        _enablecallbak : `int`
            The value of one of these options:
                0 - ON
                1 - OFF
        """
        self._enablecallbak = val

    def getAutoSave(self):
        return self._autosave

    def setAutoSave(self,val):
        self._autosave = val

    def getNextraDim(self):
        return self._nextradim

    def setNextraDim(self,val):
        self._nextradim = val

    def getDimX(self):
        return self._dimx

    def setDimX(self,val):
        self._dimx = val

    def getDimY(self):
        return self._dimy

    def setDimY(self,val):
        self._dimy = val

    def getWriteMode(self):
        return self._writemode

    def setWriteMode(self,val):
        self._writemode = val

    def getOutputFormat(self):
        return self._outputformat

    def setOutputFormat(self,val):
        self._outputformat = val
    
    def setRepeatNumber(self, val):
        self._repeat_number = val
    
    def getRepeatNumber(self):
        return self._repeat_number

    def startCapture(self):
        self.file.Capture = 1

    def stopCapture(self):
        self.file.Capture = 0
                
    def setParams(self,dictionary):
        self.dimensions = []

        nframes = 1
        for ipoints_motor in dictionary['points']:
            # Gambiarra pq ele conta o ultimo ponto
            self.dimensions.append(len(set(ipoints_motor)) - 1)
        self.setNextraDim(len(self.dimensions))

        for i in range(len(self.dimensions),10):
            self.dimensions.append(1)

        self.setDimX(self.dimensions[0])
        self.setDimY(self.dimensions[1])

        for i in range(3,10):
            self.file.put("ExtraDimSize"+str(i),self.dimensions[i-1])

        for i in self.dimensions:
            nframes = nframes * i
        self.setNframes(nframes)

        self.setRepeatNumber(dictionary['repetition'])

    def setWriteParams(self):
        self.detector.ImageMode     =   self.getImageMode()
        self.detector.TriggerMode   =   self.getTriggerMode()
        self.file.EnableCallbacks   =   self.getEnableCallback()

        #points
        self.file.NumExtraDims      =   self.getNextraDim()
        self.file.ExtraDimSizeX     =   self.getDimX()
        self.file.ExtraDimSizeY     =   self.getDimY()
        self.file.setWriteMode(mode=self.getWriteMode())

        #Set output path
        self.file.AutoSave          =   self.getAutoSave()
        self.file.setPath(self.getFilePath())
        self.file.setTemplate(self.getOutputFormat())
        self.file.setFileName(self.getFileName())
        self.file.setNumCapture(self.getNframes())
        self.file.FileNumber        =   self.getRepeatNumber()

    def close(self):
        """
        Stops an ongoing acquisition, if any, and puts the EPICS IOC in idle state.
        """
        self._done = 1

    def getIntensity(self):
        return self.detector.ArrayCounter_RBV

    def getValue(self, **kwargs):        
        value = self.getIntensity()
        val = time()-self.timi
        self.timi = time()
        return value


    def setCountTime(self, t):
        """
        Sets the image acquisition time.
        Parameters
        ----------
        t : `float`
            Acquisition time
        """
        self.detector.AcquireTime = t
        self.detector.AcquirePeriod = 0
        print('inside setCountTime', self.detector.AcquireTime)

    def getAcquireTime(self):
        return self.detector.AcquireTime, self.detector.AcquirePeriod


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
        self.detector.Acquire = 1
        self._done = 0 # force the confirmation that the detector has already received acquire function
        


    def stopCount(self):
        """
        Stops acquiring. This method simply calls :meth:`close`.
        
        See: :meth:`close`
        """
        
        self.detector.Acquire = 0
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
            poll(evt=1.e-5, iot=0.1)
