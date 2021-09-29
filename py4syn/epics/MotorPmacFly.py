from py4syn.epics.MotorClass import Motor
import numpy as np
from epics import PV
from time import sleep
from scan_utils.CrioTatu import CrioTatuClass


class PmacFlyClass(Motor):
    def __init__(self, pvName, mnemonic):
        super().__init__(pvName, mnemonic)
        self.dictionary = None
        self.TriggerMode = None
        self.controller = pvName[:-3]

        self.start_offset = 0
        self.end_offset = 0
        self.motor.add_pv(pvName+".MRES",
                          attr='MRES')

        self.crio = CrioTatuClass('CAT:C:RIO01:9403H')
        self.crio.stop_tatu()
        self.crio.clear_params()

        self.pvPLC = PV(self.controller + ':SendCmd')
        self.Ts = PV(self.controller + ":flyM7JogTs:RBV")
        self.pos_start = PV(self.controller + ":flyPosStart")
        self.pos_end = PV(self.controller + ":flyPosEnd")
        self.pos_width = PV(self.controller + ":flyPosWidth")
        self.pos_period = PV(self.controller + ":flyPosPeriod")
        self.enable_trigger_output = PV(self.controller + ":flyEnableTrigger")
        self.set_trigger_set = PV(self.controller + ":flySetTrigger")
        self.set_trigger_set_rbv = PV(
            self.controller + ":flySetTriggerRBV:RBV")
        self.flyscan_monitor = PV(self.controller + ":flyStartFlyMonitor")
        self.pvRyOffset = PV(self.pvName + '.OFF')

        # TODO: Find a best way the get this PVs
        self.pvAH501DAveragingTime = PV('CAT:T:AH501D:AveragingTime')

    def disable_plc(self):
        self.pvPLC.put('disable PLC PLC_SET_TRIGGER')
        sleep(2)
        self.pvPLC.put('disable PLC PLC_START_FLY')
        self.setVelocity(30)

    def getResolution(self):
        """
        Read the motor Resolution field `MRES` field of Motor Record

        Returns
        -------
        `float`
        """

        return self.motor.get('MRES')

    def stop(self):
        """
        Stop the motor and stop plcs 
        Overloading of the stop method from MotorClass
        """
        print("Stop pmac fly class")
        self.disable_plc()
        self.motor.put('STOP', 1)

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
        print("--------SET VELO----------")
        self.preScanConfig()
        print("--------POSITIONING----------")
        self.setInitialPosition()
        print("--------Set Trigger----------")
        self.set_trigger_set.put(1)

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
            #Ts = self.Ts.get()/1000
            Ts = 1e-5/1000

            # Calculate the acceleration displacement
            offset = -(k/(6*Ts))*pow(Ta+Ts, 3) \
                + (k/2)*(Ta/Ts + 1)*pow(Ta+Ts, 2)\
                - (k/2)*Ts*(pow(Ta/Ts, 2) + 1)*(Ta+Ts)\
                + (k*pow(Ts, 2))/6 + (k*pow(Ta, 3))/(6*Ts)

            print("Offset: \t", offset)

            if self.dictionary['end'] < self.dictionary['start']:
                value = self.dictionary['start'] + offset
                self.end_offset = self.dictionary['end'] - offset

            else:
                value = self.dictionary['start'] - offset
                self.end_offset = self.dictionary['end'] + offset

            self.start_offset = value

            print("Positions log")
            print("Start movement: \t", self.start_offset)
            print("Start triggering:\t", self.dictionary['start'])
            print("End triggering: \t", self.end_offset)
            print("End movement: \t", self.end_offset)

            # Write on delta tau registers
            sf = self.getResolution()

            # add ry user offset
            ry_offset = self.pvRyOffset.get()
            self.end_offset -= ry_offset

            self.pos_start.put(self.dictionary['start']/sf)
            self.pos_end.put(int(self.end_offset/sf))

            self.pos_width.put(50)
            self.pos_period.put(
                np.round((self.veloc*self.dictionary['acquire_period'])/sf, 0))

            # Pq está 10e6? Não seria 1e6?
            # Não seria Ts+Ta em vez de self.veloc?
            offset_time = (offset/self.veloc)*10e6
            print("Set cRIO")

            '''
            # Pilatus Config - (Output 5, Input 1)
            # P11 (10) = if P11 is TRUE, the condition is met.​
            self.crio.tatu.C5_c0 = 10
            # Rising pulse (4) = a pulse, from 0 to 1 and back to 0.
            self.crio.tatu.O5_c0 = 'Rising pulse'
            self.crio.tatu.P5_c0 = timeUs    # Width pulse 100ms
            print("Finished Pilatus")

            # AnalogRead 9215 CRIO02
            self.pvRIO02AvgTime.put(self.dictionary['time'])
            # P11 (10) = if P11 is TRUE, the condition is met.
            self.crio.tatu.C7_c0 = 10
            self.crio.tatu.O7_c0 = 'Rising pulse'
            self.crio.tatu.P7_c0 = timeUs
            print("Finished AnalogRead")
            '''

            # Pimega 540D - (Output 4, Input 0)
            self.crio.tatu.C4_c0 = 1
            self.crio.tatu.O4_c0 = 'On'
            self.crio.tatu.D4_c0 = offset_time  # Time to accel
            # self.crio.tatu.P4_c0 = 1000    # Width pulse 1ms
            print("Finished Pimega")

            # CAENels (OutPut 6) Config
            self.crio.tatu.C6_c0 = 1
            self.crio.tatu.O6_c0 = 'On'  # Rising pulse (4)
            self.crio.tatu.D6_c0 = offset_time  # Time to accel
            self.pvAH501DAveragingTime.put(self.dictionary['time'])
            print("Finished CAENels")

            # Motor ry (Output 15)
            self.crio.tatu.C15_c0 = 1
            self.crio.tatu.D15_c0 = 0
            self.crio.tatu.O15_c0 = 'Rising pulse'
            self.crio.tatu.P15_c0 = 1000    # Width pulse 1ms
            print("Finished Ry")

            print('Ta: ', Ta)
            print('Ts: ', Ts)
            print('offset: ', offset/sf)
            print('offset time: ', offset_time)
            print('pos_start: ', self.pos_start.get())
            print('pos_end: ', self.pos_end.get())
            print('pos_width: ', self.pos_width.get())
            print('pos_period: ', self.pos_period.get())
            print('velo: ', self.veloc)

        self.setAbsolutePosition(value, waitComplete=True)

    def preScanConfig(self):
        """
        Config Command to set Trigger
        """
        self.setVelocity(30)
        sleep(2)
        self.setAbsolutePosition(self.dictionary['start'], waitComplete=True)
        acquire_period = self.dictionary['acquire_period']
        expo_time = self.dictionary['time']

        if expo_time > acquire_period:
            acquire_period = expo_time

        if self.dictionary['step_mode']:
            self.step = self.dictionary['step_or_points']
            n_points = int(
                (self.dictionary['end'] - self.dictionary['start']) / self.dictionary['step_or_points'])
        else:
            self.step = (
                self.dictionary['end'] - self.dictionary['start']) / self.dictionary['step_or_points']
            n_points = self.dictionary['step_or_points']

        velocity = min(abs((self.step) / acquire_period), 360)
        print('velocity:', velocity)
        self.veloc = velocity
        self.setVelocity(velocity)

        self.pvPLC.put('enable PLC PLC_SET_TRIGGER')
        self.pvPLC.put('enable PLC PLC_START_FLY')

    def startFly(self):
        # Start flyscan monitor
        print("--------Enable Trigger----------")
        self.flyscan_monitor.put(1)
        # Enable trigger output
        # Command motor to final position
        print("--------Star Fly :)----------")
        print(self.crio.tatu.bo15)
        self.enable_trigger_output.put(1)

        self.crio.start_tatu()
        while self.crio.is_running_tatu() != 1:
            print('Trying to activate tatu!')
            self.crio.start_tatu()
            sleep(0.1)
        print('Tatu is active! Active = ' +
              str(self.crio.is_running_tatu()))

        self.wait()
        self.crio.stop_tatu()

        self.disable_plc()
