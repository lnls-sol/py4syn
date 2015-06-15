"""
FILENAME... PhotonicCCDClass.py
USAGE...    Python Class for EPICS Photonic CCD Detector control
 
/*
 *      Original Author: Hugo Henrique Slepicka
 *      Date: 30/06/2012
 *
 * Modification Log:
 * -----------------
 * .01 30/06/2012 first version released
 */
"""

from time import sleep
from epics import PV
from py4syn.epics.StandardDevice import StandardDevice

class PhotonicCCD(StandardDevice):
    #CALLBACK FUNCTION FOR THE CCD ACQUIRE STATUS PV
    def onAcquireChange(self, value, **kw):
        #print datetime.datetime.now(), " - Acquisition Done = ", (value == 0)
        self._done = (value == 0)

    #CONSTRUCTOR OF CCD CLASS
    def __init__(self, pvName, mnemonic, scalerObject=""):
        StandardDevice.__init__(self, mnemonic)
        self.pvAcquire = PV(pvName+":cam1:Acquire", callback=self.onAcquireChange)
        self.pvNumImages = PV(pvName+":cam1:NumImages")
        self.pvFileName = PV(pvName+":cam1:FileName") 
        self.pvFilePath = PV(pvName+":cam1:FilePath") 
        self.pvAcquireTime = PV(pvName+":cam1:AcquireTime")
        self.pvFileNumber = PV(pvName+":cam1:FileNumber")
        self.pvArrayCounter = PV(pvName+":cam1:ArrayCounter")
        self.pvArrayCounterRBV = PV(pvName+":cam1:ArrayCounter_RBV")
        self.scaler = scalerObject
        self._done = self.isDone()
        self.time = self.pvAcquireTime.get()

    def isDone(self):
        return (self.pvAcquire.get() == 0)

    def getAcquireTime(self):
        return self.pvAcquireTime.get()

    def getFileName(self):
        #name = ''.join([chr(c) for c in self.pvFileName.get()])
        #name = name[0:-1]
        name = self.pvFileName.get(as_string=True)
        return name

    def getFilePath(self):
        #path = ''.join([chr(c) for c in self.pvFilePath.get()])
        #path = path[0:-1]
        path = self.pvFilePath.get(as_string=True)
        return path

    def getFileNumber(self):
        return self.pvArrayCounterRBV.get()

    def getCompletePreviousFileName(self):
        return self.getFileName()+str(self.getFileNumber()-1).zfill(3)

    def getCompleteFileName(self):
        return self.getFileName()+str(self.getFileNumber()).zfill(3)

    def acquire(self, waitComplete=False):
        self.scaler.setCountTime(self.time)
        self.scaler.setCountStart()
        self.pvAcquire.put(1)
        self._done = False
        if(waitComplete):
            self.wait()
        self.scaler.setCountStop()

    def getIntensity(self):
        return self.scaler.getIntensity()

    def setFileNumber(self, number):
        self.pvArrayCounter.put(number-1, wait=True)
        self.pvFileNumber.put(number, wait=True)

    def setAcquireTime(self, time):        
        self.time = time
        self.pvAcquireTime.put(time, wait=True)

    def setFileName(self, name):
        self.pvFileName.put(name+"\0", wait=True) 

    def setNumImages(self, number):
        self.pvNumImages.put(number, wait=True)

    def wait(self):
        while(not self._done):
            sleep(0.001)
