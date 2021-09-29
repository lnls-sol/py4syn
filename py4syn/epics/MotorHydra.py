import time
from epics import PV
from py4syn.epics.MotorClass import Motor


class MotorHydra(Motor):
    '''Hydra motor class'''
    def __init__(self, pvName, mnemonic):
        super().__init__(pvName, mnemonic)
        self.dictionary = None
        self.TriggerMode = None
        self.pvHydra = ''.join(pvName.split(':m1')[:-1]) + ':hydraAsynEth1'

        self.pvSendTo = PV(self.pvHydra + '.AOUT')
        self.pvReadFrom = PV(self.pvHydra + '.AINP')

    def getTriggerMode(self):
        """
        Retunrs Trigger Mode
        """
        return self.TriggerMode

    def setTriggerMode(self, value):
        """
        Set Trigger Mode for the controller
        """
        self.TriggerMode = value

    def setTrigger(self, dictionary):
        """
        Method for starting a motor fly scan
        """
        self.dictionary = dictionary
        #print(self.dictionary)
        self.setVelocity(100)
        print("--------POSITIONING----------")
        self.setInitialPosition()

    def setInitialPosition(self, value=None):
        if value is None:
            if self.dictionary['end'] < self.dictionary['start']:
                value = self.dictionary['start'] + self.dictionary['start_offset']
            else:
                value = self.dictionary['start'] - self.dictionary['start_offset']
        self.setAbsolutePosition(value, waitComplete=True)

    def preScanConfig(self):
        """
        Config Command to set Trigger
        """
        aquire_time = self.dictionary['aquire_time']
        expo_time = self.dictionary['time']

        if expo_time > aquire_time:
            aquire_time = expo_time

        if self.dictionary['step_mode']:
            step = self.dictionary['step_or_points']
            n_points = int((self.dictionary['end'] - self.dictionary['start']) / self.dictionary['step_or_points'])
        else:
            step = (self.dictionary['end'] - self.dictionary['start']) / self.dictionary['step_or_points']
            n_points = self.dictionary['step_or_points']
        velocity = min(abs(step / aquire_time), 30)

        print("target: ", self.dictionary['end'])
        print("velocity: ", velocity)
        print("step: ", n_points)
        self.setVelocity(abs(velocity))

        # configString = "Hello world"
        configString = "1 1 settr {0} {1} {2} 1 settrpara".format(int(self.dictionary['start']), int(self.dictionary['end']), int(n_points))

        return configString

    def startFly(self):
        """
        Method for starting a motor fly scan
        """
        print("--------SET TRIGGER PARAMs----------")
        # self.preScanConfig()
        self.sendCommand("100 1 1 settroutpw")
        self.sendCommand("0 1 1 settroutpol")
        self.sendCommand(self.preScanConfig())
        print("--------STARTS-FLY----------")
        # self.setAbsolutePosition(self.dictionary['end'] + self.dictionary['end_offset'])
        print("Running")

        if self.dictionary['end'] < self.dictionary['start']:
            self.setAbsolutePosition(self.dictionary['end'] - self.dictionary['end_offset'], True)
        else:
            self.setAbsolutePosition(self.dictionary['end'] + self.dictionary['end_offset'], True)
        self.sendCommand("0 1 settr 0 1 1 settroutpol")

    def sendCommand(self, command):
        self.pvSendTo.put(command.encode('utf-8'))
        time.sleep(1)

        return command

    def reset(self):
        try:
            print("Initializing. Wait...")
            self.sendCommand("1 nst")
            status = self.pvReadFrom.get()
            self.sendCommand("1 init")
            time.sleep(3)

            if (self.pvReadFrom.get() == "256" or self.pvReadFrom.get() == "260"):
                print("Initializing again...")
                self.sendCommand("1 nst")
                status = self.pvReadFrom.get()
                self.sendCommand("1 init")
                time.sleep(3)
            self.sendCommand("1 nst")
            status = self.pvReadFrom.get()

            if (self.pvReadFrom.get() == "36" or self.pvReadFrom.get() == "256" or self.pvReadFrom.get() == "260" or self.pvReadFrom.get() == ""):
                self.sendCommand("1 nst")
                status = self.pvReadFrom.get()
                print(status)
                self.sendCommand("reset")
                time.sleep(1)
                print("Reseting... This can take some time...")
                while (self.pvReadFrom.get() == ""):
                    self.sendCommand("1 nst")

                if (self.pvReadFrom.get() == "256" or self.pvReadFrom.get() == "260"):
                    print("Initializing again...")
                    self.sendCommand("1 nst")
                    status = self.pvReadFrom.get()
                    self.sendCommand("1 init")
                    time.sleep(3)
                    self.sendCommand("1 nst")
                    status = self.pvReadFrom.get()
                    # return
                else:
                    print('\nSomething went wrong. Try again or do it manually.\n')

            self.sendCommand("1 nst")
            status = self.pvReadFrom.get()

            if (self.pvReadFrom.get() == "32"):
                status = self.calibration()
                print('\n\nHydra reset done!')
            else:
                print('\nSomething went wrong. Try again or do it manually.\n')

        except Exception as e:
            print("Failed. Error: {0}".format(e))

    def calibration(self):
        self.sendCommand("0 0 1 setsw")
        time.sleep(1)
        self.sendCommand("1 ncal")
        time.sleep(1)
        while (self.isMovingPV() is True):
            print('Motor is moving...')
            time.sleep(1)
        self.sendCommand("2 0 1 setsw")
        time.sleep(1)
        self.sendCommand("-4000 200000 1 setnlimit")
        time.sleep(1)

        self.sendCommand("1 nst")
        status = self.pvReadFrom.get()
        self.setAbsolutePosition(0., True)

        return (status)
