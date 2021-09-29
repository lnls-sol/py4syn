from epics import PV
from py4syn.epics.MotorClass import Motor


class MotorWithReadBack(Motor):
    '''A motor class with separate read back value PV'''
    def __init__(self, mnemonic, pvName, readBackName):
        super().__init__(pvName, mnemonic)
        self.readBack = PV(readBackName)

    def getRealPosition(self):
        return self.readBack.get()
