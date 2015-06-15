from time import sleep
from epics import PV
from py4syn.epics.StandardDevice import StandardDevice


class Shutter(StandardDevice):
    
    #CALLBACK FUNCTION FOR THE SHUTTER STATUS PV
    #def onStatusChange(self, **kw):
    #self._open = not self._open

    #CONSTRUCTOR OF SHUTTER CLASS
    def __init__(self, pvStatusName="", pvControlName="", pvHutchName="", mnemonic="", invert=False):
        StandardDevice.__init__(self, mnemonic)
        self.delay = 0.01
        self.invert = invert
        self.pvStatus = PV(pvStatusName)
        self.pvControl = PV(pvControlName)
        self.pvHutch = PV(pvHutchName)

        #IF POSSIBLE, OPEN THE SHUTTER AND WAIT UNTIL THE SHUTTER IS REALLY OPEN
    def open(self):

        if not self.isHutchReady():
            raise Exception('Error: ','Hutch Not Ready')

        try:
            if not self.isOpen():
                self.pvControl.put(1, wait=True)
                while not self.isOpen():
                    sleep(self.delay)
            else:
                print('Warning: ','Shutter already open')
        except Exception as e:
            print(e.args[0],e.args[1])

    #IF POSSIBLE, CLOSE THE SHUTTER AND WAIT UNTIL THE SHUTTER IS REALLY CLOSE
    def close(self):    
        try:
            if self.isOpen():        
                self.pvControl.put(1, wait=True)
                while self.isOpen():
                    sleep(self.delay)
            else:
                print('Warning: ','Shutter already closed')
        except Exception as e:
            print(e.args[0],e.args[1])

    def isHutchReady(self):
        if(self.invert):
            return 1 - self.pvHutch.get()
        else:
            return self.pvHutch.get()

    def isOpen(self):
        if(self.invert):
            return 1 - self.pvStatus.get()
        else:
            return self.pvStatus.get()        
            
