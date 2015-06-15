"""Hyppie Charge-Coupled Devices (CCD) Class

Python Class for EPICS LabView RT Detector control.

:platform: Unix
:synopsis: Python Class for EPICS LabView RT Detector control.

.. moduleauthor:: Hugo Henrique Slepicka <hugo.slepicka@lnls.br>
    .. note:: 30/06/2012 [hugo.slepicka]  first version released
    .. note:: 25/07/2014 [douglas.beniz]  just replacing 'tabs' by 'spaces'
"""

from time import sleep
from epics import PV
from py4syn.epics.StandardDevice import StandardDevice

class HyppieCCD(StandardDevice):
    """
    Python class to help configuration and control of Charge-Coupled Devices
    (CCD) via Hyppie over EPICS.
    
    CCD is the most common mechanism for converting optical images to electrical
    signals. In fact, the term CCD is know by many people because of their use
    of video cameras and digital still cameras.
    """

    def onAcquireChange(self, value, **kw):
        """
        Internal use method to check whether an acquisition in execution is
        done or not.

        Parameters
        ----------
        value : `integer`
            **0 (ZERO)** Indicates the process has been concluded
        kw : `matrix`
            Internal array of parameters
        """

        #print datetime.datetime.now(), " - Acquisition Done = ", (value == 0)
        self._done = (value == 0)


    def onWaitChange(self, value, **kw):
        """
        Internal use method to check whether a configuration change request
        sent to the Charge-Coupled device has been performed or not.

        Parameters
        ----------
        value : `integer`
            **0 (ZERO)** Indicates the configuration change has been conclude
        kw : `matrix`
            Internal array of parameters
        """

        #print datetime.datetime.now(), " - Acquisition Done = ", (value == 0)
        self._doneConfig = (value == 0)

    def __init__(self, pvName, mnemonic, scalerObject=""):
        """
        **Constructor**

        Parameters
        ----------
        pvName : `string`
            Charge-Coupled Device (CCD)'s naming of the PV (Process Variable)
        mnemonic : `string`
            Device mnemonic
        scalerObject : `object`
            It represents logically the Scaler device
        """

        StandardDevice.__init__(self, mnemonic)
        self.pvAcquire = PV(pvName+":Acquire", callback=self.onAcquireChange)
        self.pvConfigWait = PV(pvName+":Wait", callback=self.onWaitChange)
        self.pvAutoIncrement = PV(pvName+":AutoIncrement")
        self.pvMinX = PV(pvName+":MinX")
        self.pvMinY = PV(pvName+":MinY")
        self.pvSizeX = PV(pvName+":SizeX")
        self.pvSizeY = PV(pvName+":SizeY")
        self.pvAcquireTime = PV(pvName+":AcquireTime")
        self.pvFileNumber = PV(pvName+":FileNumber")
        self.pvNumImages = PV(pvName+":NumImages")
        self.pvFilePath = PV(pvName+":FilePath")
        self.pvFileName = PV(pvName+":FileName")
        self.pvCommand = PV(pvName+":StrInput")
        self.pvCommandOut = PV(pvName+":StrOutput")
        self.scaler = scalerObject
        self._done = self.isDone()
        self._doneConfig = self.isDoneConfig()
        self.time = float(self.pvAcquireTime.get()/1000000) #Convert from microsecond to second

    def isDone(self):
        """
        Check whether acquisition process has been concluded or not.

        Returns
        -------
        `boolean`

        .. note::
            - **True**  -- Acquisition has been concluded;
            - **False** -- Acquisition has **NOT** been concluded.
        """

        return (self.pvAcquire.get() == 0)

    def isDoneConfig(self):
        """
        Check whether configuration process has been concluded or not.

        Returns
        -------
        `boolean`

        .. note::
            - **True**  -- Configuration has been concluded;
            - **False** -- Configuration has **NOT** been concluded.
        """

        return (self.pvConfigWait.get() == 0)

    def getAcquireTime(self):
        """
        Read acquisition time of a Charge-Coupled Device (CCD).

        Returns
        -------
        `float`
        """

        return self.pvAcquireTime.get()

    def getCompletePreviousFileName(self):
        """
        Return the full file name, with extension, of the image which were
        read previously.

        Returns
        -------
        `string`
        """

        if self.pvAutoIncrement.get() == 1:
            return self.getFileName()+"_"+str(int(self.getFileNumber())-1)+".tif"
        else:
            return self.getFileName()+".tif"

    def getCompleteFileName(self):
        """
        Return the full file name, with extension, of the current image which is
        being read.

        Returns
        -------
        `string`
        """

        if self.pvAutoIncrement.get() == 1:
            return self.getFileName()+"_"+str(int(self.getFileNumber()))+".tif"
        else:
            return self.getFileName()+".tif"

    def getFileName(self):
        """
        Return the full file name of the current image which is being read.

        Returns
        -------
        `string`
        """

        #name = ''.join([chr(c) for c in self.pvFileName.get()])
        #name = name[0:-1]
        name = self.pvFileName.get(as_string=True)
        return name

    def getFilePath(self):
        """
        Return the full path where is the file of current image which is being
        read.

        Returns
        -------
        `string`
        """

        #path = ''.join([chr(c) for c in self.pvFilePath.get()])
        #path = path[0:-1]
        path = self.pvFilePath.get(as_string=True)
        return path

    def getFileNumber(self):
        """
        Return the number sequence of the file of current image which is being
        read.

        Returns
        -------
        `integer`
        """

        return self.pvFileNumber.get()

    def setCommandInput(self, cmd):
        """
        Set the input command to be submitted to the device.

        Parameters
        ----------
        unit : `string`
            Command to send to device.
        """

        self.pvCommand.put(cmd+"\0") 
        self.waitConfig()

    def getCommandInput(self, cmd):
        """
        Return the input command submitted to the device.

        Returns
        -------
        `string`
        """

        self.pvCommand.get(as_string=True) 

    def getCommandOutput(self, cmd):
        """
        Return the output of command the command sent to device.

        Returns
        -------
        `string`
        """

        return self.pvCommandOut.get(as_string=True) 

    def enableAutoIncrement(self):
        """
        Set AutoIncrement property of device to **1 (ONE)**, that is, enables
        it.

        Parameters
        ----------
        None
        """

        self.pvAutoIncrement.put(1)

    def disableAutoIncrement(self):
        """
        Set AutoIncrement property of device to **0 (ZERO)**, that is, disables
        it.

        Parameters
        ----------
        None
        """

        self.pvAutoIncrement.put(0)

    def getIntensity(self):
        """
        Return the intensity of the scaler device.

        Returns
        -------
        `string`
        """

        return self.scaler.getIntensity()

    def setFileNumber(self, number):
        """
        Set the number sequence of the file for the current image which is being
        read.

        Parameters
        ----------
        unit : `integer`
            Sequence number to set to the image file.
        """

        self.pvFileNumber.put(number)

    def setAcquireTime(self, time):
        """
        Set the acquisition time to the Charge-Coupled Device (CCD).

        Parameters
        ----------
        unit : `float`
            Time value to be configured for the acquire-time property of CCD.
        """

        self.time = time
        self.pvAcquireTime.put(float(self.time))
        self.waitConfig()

    def setFileName(self, name):
        """
        Set the full file name of current image which is being read.

        Parameters
        ----------
        unit : `string`
            Name of image file to capture.
        """

        self.pvFileName.put(name+"\0") 

    def setFilePath(self, name):
        """
        Set the full path where file of current image which is being read must
        be saved.

        Parameters
        ----------
        name : `string`
            Description of path where image file should be stored.
        """

        self.pvFilePath.put(name+"\0") 

    def setNumImages(self, number):
        """
        Set the number of images which should be read.

        Parameters
        ----------
        number : `integer`
            Number of images to be captured.
        """

        self.pvNumImages.put(number)
        self.waitConfig()

    def setROI(self, startX, sizeX, startY, sizeY):
        """
        Method to determine the Region Of Interest (ROI) of a CCD device.

        Parameters
        ----------
        startX : float
            X position to start the region of interest of the
            Charge-Coupled Device (CCD)
        sizeX : float
            size of X positioning
        startY : float
            Y position to start the region of interest of the
            Charge-Coupled Device (CCD)
        sizeY : float
            size of Y positioning

        Examples
        --------
        >>> import py4syn.epics.HyppieCCDClass.HyppieCCD as hyppie_ccd
        >>> hyppie_ccd.setROI(32, 100, 15, 49)

        .. note::
            This method must be used only after default configuration was set
            in the Charge-Coupled Devide (CCD)
        """

        print("StX = ", startX, "SiX", sizeX, "StY", startY, "SiY", sizeY)
        print("Set Min X")
        self.pvMinX.put(startX)
        print("Will Wait")
        self.waitConfig()
        print("Set Min Y")
        self.pvMinY.put(startY)
        self.waitConfig()
        self.pvSizeX.put(sizeX)
        self.waitConfig()
        self.pvSizeY.put(sizeY)
        self.waitConfig()

    def acquire(self, waitComplete=False):
        """
        Start process of image capturing.

        Parameters
        ----------
        waitComplete : `boolean  [OPTIONAL]`
            Whether to wait for all of the reading process of the image to complete, or not.

            .. note::
                - **True**  -- Wait for all image reading conclusion;
                - **False** `[DEFAULT]` -- **DON'T** wait for all image reading conclusion.
        """
        self.scaler.setCountTime(self.time)
        self.scaler.setCountStart()

        self.pvAcquire.put(1)
        self._done = False
        if(waitComplete):
            self.wait()
        self.scaler.setCountStop()

    def waitConfig(self):
        """
        Method which keeps a sleeping period meanwhile any configuration is
        being set.

        Parameters
        ----------
        None
        """

        self._doneConfig = False
        while(not self._doneConfig):
            sleep(0.001)

    def wait(self):
        """
        Method which keeps a sleeping period meanwhile any command execution is
        being performed.

        Parameters
        ----------
        None
        """

        while(not self._done):
            sleep(0.001)
