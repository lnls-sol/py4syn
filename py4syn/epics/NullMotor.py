from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice

class NullMotor(IScannable, StandardDevice):
    def __init__(self, mnemonic):
        super().__init__(mnemonic)
        self.value = 0
        self.velocity = 0

    def getValue(self):
        return self.value
    def setValue(self, v):
        self.value = v
    def wait(self):
        pass
    def stop(self):
        pass
    def getLowLimitValue(self):
        return float('-inf')
    def getHighLimitValue(self):
        return float('inf')
    def getRealPosition(self):
        return self.getValue()
    def setVelocity(self, v):
        self.velocity = v
    def getVelocity(self):
        return self.velocity
