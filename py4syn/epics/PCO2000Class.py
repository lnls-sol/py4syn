"""
FILENAME... PCO2000Class.py
USAGE...    Python Class for EPICS PCO 2000 Camera Using LABVIEW IOC
 
/*
 *      Original Author: IMX Beamline Group
 *      Date: 19/07/2013
 *
 * Modification Log:
 * -----------------
 * .01 19/07/2013 first version released
 */
"""
from time import sleep
from epics import PV
from py4syn.epics.StandardDevice import StandardDevice

class PCO2000(StandardDevice):
    TYPE_TIFF = "TIFF"
    TYPE_HDF = "HDF"

    #CALLBACK FUNCTION FOR THE CCD ACQUIRE STATUS PV
    def onAcquireChange(self, value, **kw):
        self._doneRecord = (value == 0)

    def onAcquireRBVChange(self, value, **kw):
        self._doneReadOut = (value == 0)

    def onDataChange(self, value, **kw):
        if(self.initCamera):
            self.initCamera = False
            return
        self.imageBufferQueue.put(value)
        self.NData = self.NData + 1

    def onNELMChange(self, value, **kw):
        if(self.initNELM):
            self.initNELM = False
            return
        self.NCount = self.NCount + 1

    #CONSTRUCTOR OF CCD CLASS
    def __init__(self, pvName, mnemonic, imageBufferQueue=None, processName=""):
        StandardDevice.__init__(self, mnemonic)
        self.processName = processName
        self.initCamera = True
        self.initNELM = True
        self.NCount = 0
        self.NData = 0
        self.imageBufferQueue = imageBufferQueue

        self.pvData = PV(pvName+":Data", auto_monitor=True)
        self.pvData.add_callback(self.onDataChange)

        self.pvAcquire = PV(pvName+":Acquire", callback=self.onAcquireChange, auto_monitor=True)
        self.pvAcquireRBV = PV(pvName+":Acquire_RBV", callback=self.onAcquireRBVChange, auto_monitor=True)
        self.pvNELM = PV(pvName+":Data.NELM", callback=self.onNELMChange)

        self._done = self.isDone()

        self.pvPixelSize = PV(pvName + ":PixelSize")
        self.pvCheckImage = PV(pvName + ":CheckImage")
        self.pvMinX = PV(pvName + ":MinX")
        self.pvMinY = PV(pvName + ":MinY")
        self.pvSizeX = PV(pvName + ":SizeX")
        self.pvSizeY = PV(pvName + ":SizeY")
        self.pvAcquireTime = PV(pvName+":AcquireTime")
        self.pvAcquireTimeBase = PV(pvName+":AcquireTimeBase")
        self.pvDelayTime = PV(pvName + ":DelayTime")
        self.pvDelayTimeBase = PV(pvName + ":DelayTimeBase")

        self.pvFileFormat = PV(pvName + ":FileFormat")
        self.pvFileName = PV(pvName + ":FileName")
        self.pvFileNumber = PV(pvName + ":FileNumber")
        self.pvFilePath = PV(pvName + ":FilePath")

#         #### PVS Bellow are used only for information display, no need to be here in the Python Class
#         #### If needed just uncomment and create the proper methods for GET and SET values.
#         self.pvADC = PV(pvName+":ADC")
#         self.pvAutoIncrement = PV(pvName+":AutoIncrement")
#         self.pvBinHorz = PV(pvName + ":BinHorz")
#         self.pvBinVert = PV(pvName + ":BinVert")
#         self.pvBoolTest = PV(pvName + ":BoolTest")
#         self.pvCamTemp = PV(pvName + ":CamTemp")
#         self.pvCCDTemp = PV(pvName + ":CCDTemp")
#         self.pvDoubleImage = PV(pvName + ":DoubleImage")
#         self.pvHotPixelCorrection = PV(pvName + ":HotPixelCorrection")
#         self.pvHotPixelX = PV(pvName + ":HotPixelX")
#         self.pvHotPixelY = PV(pvName + ":HotPixelY")
#         self.pvNoiseFiltering = PV(pvName + ":NoiseFiltering")
#         self.pvPixelRate = PV(pvName + ":PixelRate")
#         self.pvPixelSize = PV(pvName + ":PixelSize")
#         self.pvPowTemp = PV(pvName + ":PowTemp")
#         self.pvTimestamp = PV(pvName + ":Timestamp")
#         self.pvStatus = PV(pvName + ":Status")

    def getPixelSize(self):
        return self.pvPixelSize.get()

    def getCheckImage(self):
        return self.pvCheckImage.get()

    def setCheckImage(self, v):
        self.pvCheckImage.put(v)

    def getMinX(self):
        return self.pvMinX.get()
        
    def setMinX(self, v):
        self.pvMinX.put(v)

    def getMinY(self):
        return self.pvMinY.get()

    def setMinY(self, v):
        self.pvMinY.put(v)

    def getSizeX(self):
        return self.pvSizeX.get()

    def setSizeX(self, v):
        self.pvSizeX.put(v)

    def getSizeY(self):
        return self.pvSizeY.get() 

    def setSizeY(self, v):
        self.pvSizeY.put(v)

    def getAcquireTime(self):
        return self.pvAcquireTime.get()
    
    def setAcquireTime(self, v):
        self.pvAcquireTime.put(v)
    
    
    def getAcquireTimeBase(self):
        return self.pvAcquireTimeBase.get()
    
    def setAcquireTimeBase(self, v):
        self.pvAcquireTimeBase.put(v)
    
    def getDelayTime(self):
        return self.pvDelayTime.get()
    
    def setDelayTime(self, v):
        self.pvDelayTime.put(v)
        
    def getDelayTimeBase(self):
        return self.pvDelayTimeBase.get()
    
    def setDelaytimeBase(self, v):
        self.pvDelayTimeBase.put(v)
    
    
    def getFileFormat(self):
        return self.pvFileFormat.get()
    
    def setFileFormat(self, v):
        if(v in [self.TYPE_HDF, self.TYPE_TIFF]):
            self.pvFileFormat.put(v)
        else:
            msg = 'File format "' + v + '" not supported. Only supported are: '
            raise Exception('Error: ',msg)
        
    def getFileName(self):
        return self.pvFileName.get()
    
    def setFileName(self, v):
        self.pvFileName.put(v)
        
    def getFileNumber(self):
        return self.pvFileNumber.get()
    
    def setFuleNumber(self, v):
        self.pvFileNumber.put(v)
        
    def getFilePath(self):
        return self.pvFilePath.get()
    
    def setFilePath(self, v):
        self.pvFilePath.put(v)
    

    def getCompleteFilePath(self):
        if(self.getFileFormat() == self.TYPE_TIFF):
            ext = ".tif"
        elif(self.getFileFormat() == self.TYPE_HDF):
            ext = ".h5"
        else:
            ext = "" 
        
        return self.getFilePath()+"/"+self.getFileName()+ext
    
    def getNELMChangeCount(self):
        return self.NCount

    def getData(self):
        self._newData = False
        return self.pvData.get()

    def isDone(self):
        return (self.pvAcquireRBV.get() == 0)

    def isRecordDone(self):
        return (self.pvAcquire.get() == 0)

    def isReadOutDone(self):
        return (self.pvAcquireRBV.get() == 0)
    
    def getIntensity(self):
        return self.scaler.getIntensity()

    def acquire(self, waitRecord=False, waitReadOut=False):
        #self.scaler.setCountTime(self.time)
        #self.scaler.setCountStart()
        self.pvAcquire.put(1)

        self._doneRecord = False
        self._doneReadOut = False
        self._newData = False

        if(waitRecord):
            self.waitRecord()

        if(waitReadOut):
            self.waitReadOut()

        #self.scaler.setCountStop()

    def waitConfig(self):
        self._doneConfig = False
        while(not self._doneConfig):
            sleep(0.001)

    def waitRecord(self):
        while(not self._doneRecord):
            sleep(0.001)

    def waitReadOut(self):
        while(not self._doneReadOut):
            sleep(0.001)

    def destroy(self):
        self.pvData.disconnect()
        self.pvAcquire.disconnect()
        self.pvAcquireRBV.disconnect()
        self.pvNELM.disconnect()
        self.imageBufferQueue = None