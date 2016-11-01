"""XIA Dxp Detector class

Python class for XIA Dxp using EPICS area detector IOC.

:platform: Unix
:synopsis: Python class for XIA Dxp detector at XRF beamline

.. moduleauthor:: Juliano Murari <juliano.murari@lnls.br>
.. based on Pilatus Class from Henrique Almeida

"""
from threading import Event
from numpy import *

from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable
from py4syn.utils.timer import Timer
from py4syn.utils.scan import *
from epics import PV, ca, caput

class Dxp(StandardDevice, ICountable):
    """
    Class to control Dxp cameras via EPICS.

    Examples
    --------
    >>> from shutil import move
    >>> from py4syn.epics.DxpClass import Dxp
    >>> 
    >>> def getImage(pv, fileName='image.tif', shutter=''):
    ...     dxp = Dxp('dxp', pv)
    ...     dxp.setFileName('/remote/' + fileName)
    ...     dxp.setCountTime(10)
    ...     dxp.startCount()
    ...     dxp.wait()
    ...     dxp.stopCount()
    ...     dxp.close()
    ...
    """
    RESPONSE_TIMEOUT = 15

    def __init__(self, mnemonic, numberOfChannels, numberOfRois, pv):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`

        Parameters
        ----------
        mnemonic : `string`
            A mnemonic for the camera
        pv : `string`
            Base name of the EPICS process variable
        """
        super().__init__(mnemonic)
        self.acquireChanged = Event()
        self.acquiring = False
        self.pvAcquire = PV(pv + ':Acquiring')
        self.pvStopAll = PV(pv + ':StopAll')
        self.pvEraseStart = PV(pv + ':EraseStart')
        self.pvAcquire.add_callback(self.statusChange)

        self.pvAcquireTime = []
        self.numberOfChannels = numberOfChannels
        self.pvDxpRois = []
        self.numberOfRois = numberOfRois
#        self.pvMcas = []

        for i in range(0,numberOfChannels):
            self.pvAcquireTime.append(PV(pv+':mca%d.PLTM'%(i+1)))    # count time for each channel
#            self.pvMcas.append(PV(pv+':mca%d'%(i+1)))                # spectrum for each channel
            for j in range(0,numberOfRois):
                self.pvDxpRois.append(PV(pv+':mca%d.R%d'%(i+1,j)))   # ROIs

        self.timer = Timer(self.RESPONSE_TIMEOUT)

    def statusChange(self, value, **kw):
        """
        Helper callback used to wait for the end of the acquisition.
        """
        self.acquiring = value
        self.acquireChanged.set()

    def close(self):
        """
        Stops an ongoing acquisition, if any, and puts the EPICS IOC in idle state.
        """
        self.pvStopAll.put(1, wait=True)

#    def saveSpectrum(self, ch, **kwargs):
#        fileName = getOutput()
#        idx = 0
#        if(fileName):
#            spectrum = self.pvMcas[ch].get(as_numpy=True)
#            if fileName[-4] == '.':
#                while os.path.exists(fileName.split('.')[0] + '_mca%d_%04d.mca'%(ch,idx)):
#                    idx += 1
#                fileName = fileName.split('.')[0] + '_mca%d_%04d.mca'%(ch,idx)
#            else:
#                while os.path.exists(fileName + '_mca%d_%04d.mca'%(ch,idx)):
#                    idx += 1
#                fileName = fileName + '_mca%d_%04d.mca'%(ch,idx)
#        savetxt(fileName, spectrum, fmt='%d')

    def getValueChannel(self, channel, **kwargs):
        ch = int(channel[3])      # channel[3] is the channel id
#        if(len(channel) == 4):    # mcaX is a spectrum
#            self.saveSpectrum(ch)
#            return sum(self.pvMcas[ch].get())
#        elif(channel[5] == 'R'):                   # mcaX.Ry is a ROI
        if(len(channel) > 4):    
            idx = ((ch-1)*32)+int(channel[6])    # channel[6] is the ROI id
            return self.pvDxpRois[idx].get()
        else:
            return 1.0    # TO DO: decide what to return when is spectrum

    def getValue(self, **kwargs):
        """
        This is a dummy method that always returns zero, which is part of the
        :class:`py4syn.epics.ICountable` interface. Dxp does not return
        a value while scanning. Instead, it stores a file with the resulting image.
        """
        if(kwargs):
            return self.getValueChannel(kwargs['channel'])
        return self.getValueChannel()

    def setCountTime(self, t):
        """
        Sets the image acquisition time.

        Parameters
        ----------
        t : `float`
            Acquisition time
        """
        for i in range(0,self.numberOfChannels):
            self.pvAcquireTime[i].put(t, wait=True)
        self.timer = Timer(t + self.RESPONSE_TIMEOUT)


    def setPresetValue(self, channel, val):
        """
        Dummy method to set initial counter value.
        """
        pass

    def startCount(self):
        """
        Starts acquiring an spectrum. It will acquire for the duration set with
        :meth:`setCountTime`. The resulting file will be stored in the file set with
        :meth:`setImageName`.

        See: :meth:`setCountTime`, :meth:`setImageName`

            Examples
            --------
            >>> def acquire(dxp, time, filename):
            ...     dxp.setCountTime(time)
            ...     dxp.startCount()
            ...     dxp.wait()
            ...     dxp.stopCount()
            ...
        """
        if self.acquiring:
            raise RuntimeError('Already counting')

        self.acquiring = True
        self.pvEraseStart.put(1)
        self.timer.mark()

    def stopCount(self):
        """
        Stops acquiring the image. This method simply calls :meth:`close`.
        
        See: :meth:`close`
        """
        self.close()

    def canMonitor(self):
        """
        Returns false indicating that Dxp cannot be used as a counter monitor.
        """
        return False

    def canStopCount(self):
        """
        Returns true indicating that Dxp has a stop command.
        """
        return True


    def isCounting(self):
        """
        Returns true if the camera is acquiring an image, or false otherwise.

        Returns
        -------
        `bool`
        """
        return self.acquiring

    def wait(self):
        """
        Blocks until the acquisition completes.
        """
        if self.acquiring == False:
            return

        self.acquireChanged.clear()
        while self.acquiring and self.timer.check():
            self.acquireChanged.wait(0.001)
            self.acquireChanged.clear()

        if self.timer.expired():
            raise RuntimeError('DXP is not answering')
