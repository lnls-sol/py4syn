"""
FILENAME... XIADigitalClass.py
USAGE...    Python Class for EPICS XIA Shutter Control

/*
*      Original Author: Hugo Henrique Slepicka
*      Date: 11/07/2012
*
* Modification Log:
* -----------------
* .01 30/06/2012 first version released
*/
"""
from time import sleep
from epics import PV
from py4syn.epics.StandardDevice import StandardDevice

class XIADigital(StandardDevice):    
    def __init__(self, pvName="", pvHutchName="", mnemonic=""):
        StandardDevice.__init__(self, mnemonic)
        self.delay = 0.01
        self.pvFilter1 = PV(pvName+":DIO:XIA:Filter1")
        self.pvFilter2 = PV(pvName+":DIO:XIA:Filter2")
        self.pvFilter3 = PV(pvName+":DIO:XIA:Filter3")
        self.pvFilter4 = PV(pvName+":DIO:XIA:Filter4")
        self.pvHutch = PV(pvHutchName)
        
    def isHutchReady(self):
        return self.pvHutch.get()

    def openFilter(self, idx):
        try:
            if idx == 1:
                self.pvFilter1.put(1)
            elif idx == 2:
                self.pvFilter2.put(1)
            elif idx == 3:
                self.pvFilter3.put(1)
            elif idx == 4:
                self.pvFilter4.put(1)
            else:
                raise Exception('Error:','Filter does not exist')
            sleep(0.4)
        except Exception as e:
            print(e.args[0])
            

    def closeFilter(self, idx):
        try:
            if idx == 1:
                self.pvFilter1.put(0)
            elif idx == 2:
                self.pvFilter2.put(0)
            elif idx == 3:
                self.pvFilter3.put(0)
            elif idx == 4:
                self.pvFilter4.put(0)
            else:
                raise Exception('Error:','Filter does not exist')
            sleep(0.4)
        except Exception as e:
            print(e.args[0])


    #IF POSSIBLE, OPEN THE SHUTTER AND WAIT UNTIL THE SHUTTER IS REALLY OPEN
    def openShutter(self):
        if not self.isHutchReady():
            raise Exception('Error: ','Hutch Not Ready')

        try:
            self.pvFilter4.put(1)
            sleep(0.4)
        except Exception as e:
            print(e.args[0])

    #IF POSSIBLE, CLOSE THE SHUTTER AND WAIT UNTIL THE SHUTTER IS REALLY CLOSE
    def closeShutter(self):    
        try:
            self.pvFilter4.put(0)
            sleep(0.3)
        except Exception as e:
            print(e.args[0])
