"""
FILENAME... MotomanClass.py
USAGE...    Python Class for EPICS Motoman DX100 controller
 
/*
 *      Original Author: Henrique Ferreira Canova
 *      Date: 10/03/2014
 */
"""

from epics import PV
from time import sleep
from py4syn.epics.StandardDevice import StandardDevice

class Motoman(StandardDevice):

    def finish(self, value, **kw):
        if value == "Done":
            self.motomanfinish = True
        else:
            self.motomanfinish = False

    def __init__ (self,pvPrefix="", mnemonic=""):
        StandardDevice.__init__(self, mnemonic)
        self.pvBVAL_RBV = PV(pvPrefix + ":BVAL_RBV")
        self.pvBVAL = PV(pvPrefix + ":BVAL")
        self.pvBPOS = PV(pvPrefix+ ":BPOS")
        self.pvSVON = PV(pvPrefix+":SVON")
        self.pvRUNNING = PV(pvPrefix+":RUNNING")
        self.pvRUNNING.add_callback(self.finish)
        self.pvJOB = PV(pvPrefix+":JOB") 
        self.pvGOJOB = PV(pvPrefix+":GOJOB")
        self.pvSTA1 = PV(pvPrefix+":STA1")
        self.pvSTA2 = PV(pvPrefix + ":STA2")
   
        self.motomanfinish = False

    def changeJOB(self,job=""):
        self.pvJOB.put(job)
    
    def goJOB(self):
        self.pvGOJOB.put(1)
        self.motomanfinish = False
        while not self.motomanfinish:
            sleep(0.1)

    def waitFinish(self):
        while not self.motomanfinish:
            sleep(0.01)
    
    def servoON(self,bool):
        if ((bool != 0) and (bool !=1)):
            self.pvSVON.put(0)
        else:
            self.pvSVON.put(bool)
        
    def readBVAL(self):
        return self.pvBVAL_RBV.get()

    def setBVAL(self,val):
        if ((val < 0) or (val > 50)):
            self.pvBVAL.put(0)
            self.pvSVON.put(0)
        else:
            self.pvBVAL.put(val)

    def setBPOS(self,pos):
        if ((pos < 0) or (pos > 2)):
            self.pvBPOS.put(000)
        else:
            self.pvBPOS.put(pos)

    def readSTA1(self):
        return self.pvSTA1.get()

    def readSTA2(self):
        return self.pvSTA2.get()

    def setSample(self,val):
        self.setBPOS(0)
        self.setBVAL(val)

    def removeSample(self):
        self.setBPOS(2)
        self.setBVAL(1)

    def run (self):
        self.changeJOB("CICLO")
        self.goJOB() 
