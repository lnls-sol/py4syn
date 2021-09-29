from time import sleep
from epics import PV
from py4syn.epics.MotorClass import Motor
import sys


class MotorSimFly(Motor):
    '''Motor simulation flyscan class'''

    def __init__(self, pvName, mnemonic):
        super().__init__(pvName, mnemonic)
        self.dictionary = None
        self.TriggerMode = None

        self.motor.add_pv(pvName+".MRES",
                          attr='MRES')

    def getResolution(self):
        """
        Read the motor Resolution field `MRES` field of Motor Record

        Returns
        -------
        `float`
        """
        return self.motor.get('MRES')

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
        self.preScanConfig()
        self.setInitialPosition()

    def preScanConfig(self):
        """
        Config Command to set Trigger
        """
        self.setVelocity(50)
        sleep(2)
        self.setAbsolutePosition(self.dictionary['start'], waitComplete=True)
        acquire_period = self.dictionary['acquire_period']
        expo_time = self.dictionary['time']
        step_or_points = self.dictionary['step_or_points']
        start = self.dictionary['start']
        end = self.dictionary['end']

        if expo_time > acquire_period:
            acquire_period = expo_time

        if self.dictionary['step_mode']:
            self.step = step_or_points
            n_points = int((end - start) / step_or_points)
        else:
            self.step = (end - start) / step_or_points
            n_points = step_or_points

        velocity = min(abs((self.step) / acquire_period), 360)
        self.veloc = velocity
        self.setVelocity(velocity)

    def setInitialPosition(self, autoset=True, value=None):
        if not autoset:
            if value is None:
                if self.dictionary['end'] < self.dictionary['start']:
                    value = self.dictionary['start'] + \
                        self.dictionary['start_offset']
                else:
                    value = self.dictionary['start'] - \
                        self.dictionary['start_offset']
        else:
            Ta = self.getAcceleration()
            k = self.veloc/Ta

            # Jerk time is read in milliseconds, directly from hardware
            Ts = 1e-5/1000

            # Calculate the acceleration displacement
            offset = -(k/(6*Ts))*pow(Ta+Ts, 3) \
                + (k/2)*(Ta/Ts + 1)*pow(Ta+Ts, 2)\
                - (k/2)*Ts*(pow(Ta/Ts, 2) + 1)*(Ta+Ts)\
                + (k*pow(Ts, 2))/6 + (k*pow(Ta, 3))/(6*Ts)

            if self.dictionary['end'] < self.dictionary['start']:
                value = self.dictionary['start'] + offset
                self.end_offset = self.dictionary['end'] - offset

            else:
                value = self.dictionary['start'] - offset
                self.end_offset = self.dictionary['end'] + offset

            self.start_offset = value

        self.setAbsolutePosition(value, waitComplete=True)

    def startFly(self):
        """
        Method for starting a motor fly scan
        """
        # Start flyscan monitor
        print("--------Star Fly :)----------")
        self.setAbsolutePosition(self.dictionary['end'], waitComplete=True)
        self.wait()
