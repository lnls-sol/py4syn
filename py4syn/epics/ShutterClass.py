from threading import Event
from time import sleep
from epics import PV, ca
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
            
class ToggleShutter(StandardDevice):
    def __init__(self, mnemonic, shutter, shutterReadback):
        super().__init__(mnemonic)

        self.read = PV(shutterReadback)
        self.toggle = PV(shutter)

        self._open = self.read.get()
        self.changed = Event()
        self.read.add_callback(self.onReadChange)

    def isOpen(self):
        return self._open

    def onReadChange(self, value, **kwargs):
        self._open = value
        self.changed.set()

    def wait(self, timeout=3):
        ca.flush_io()
        self.changed.wait(timeout)

    def change(self, open, wait=False):
        if self.isOpen() == open:
            self.changed.set()
            return

        self.changed.clear()
        self.toggle.put(1)
        ca.flush_io()

        if wait:
            self.wait()

    def open(self, wait=False):
        self.change(open=True, wait=wait)

    def close(self, wait=False):
        self.change(open=False, wait=wait)

class SimpleShutter(StandardDevice):
    SHUTTER_OPEN = 0
    SHUTTER_CLOSE = 1

    def __init__(self, mnemonic, shutter, invert=False):
        super().__init__(mnemonic)

        self.shutter = PV(shutter)
        self.invert = invert

    def isOpen(self):
        if (self.invert):
            return (1 - self.shutter.get()) == self.SHUTTER_OPEN
        else:
            return self.shutter.get() == self.SHUTTER_OPEN

    def wait(self, timeout=3):
        pass

    def open(self, wait=False):
        if (self.invert):
            self.shutter.put((1 - self.SHUTTER_OPEN), wait=wait)
        else:
            self.shutter.put(self.SHUTTER_OPEN, wait=wait)

    def close(self, wait=False):
        if (self.invert):
            self.shutter.put((1 - self.SHUTTER_CLOSE), wait=wait)
        else:
            self.shutter.put(self.SHUTTER_CLOSE, wait=wait)

class NullShutter(StandardDevice):
    def __init__(self, mnemonic):
        super().__init__(mnemonic)
        self.o = False

    def isOpen(self):
        return self.o

    def wait(self, timeout=3):
        pass

    def open(self, wait=False):
        self.o = True

    def close(self, wait=False):
        self.o = False
