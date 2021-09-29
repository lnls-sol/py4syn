from epics import PV, Device, ca
from py4syn.epics.MotorClass import Motor
from time import sleep
from datetime import datetime, timedelta
from scan_utils.CrioTatu import CrioTatuClass


class Saxs(Motor):
    '''Class to control a saxs flyscan with Tatu as master'''

    def onDoingFly(self, value, **kw):
        try:
            self._doingFly = value
        except:
            pass

    def __init__(self, pvName, mnemonic):
        super().__init__(pvName, mnemonic)
        self.dictionary = None
        self.TriggerMode = None
        self.pvPmacControler = pvName[:-2]

        self._doingFly = True
        self.crio = CrioTatuClass('CAT:C:RIO01:9403H')

        self.crio.disable_master_mode()
        self.crio.stop_tatu()
        self.crio.clear_params()
        self.crio.tatu.add_callback('MasterPulsing', callback=self.onDoingFly)

        # TODO: Find a best way the get this PVs
        self.pvAH501DAveragingTime = PV('CAT:T:AH501D:AveragingTime')
        self.pvRIO02AvgTime = PV('CAT:C:RIO02:PvAvgTime')

        self.pvPilatusCapture = PV('CAT:C:P300K:HDF1:Capture')

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
        # print("Dictionary: ", self.dictionary)

        print("--------setInitialPosition----------")
        self.setInitialPosition()

    def setInitialPosition(self, value=None):
        """
        Config Command to set Trigger
        """

        periodUs = int(self.dictionary['acquire_period'] * 1e6)
        timeUs = int(self.dictionary['time'] * 1e6)
        _nimages = self.dictionary['step_or_points']

        # Configure cRIO - TATU
        print("Set cRIO")

        # Configure the Master Mode
        self.crio.reset_master_counter()

        self.crio.set_master_pulse_period(periodUs)
        self.crio.set_master_pulse_length(timeUs)
        self.crio.set_master_pulse_number(_nimages)

        self.crio.start_master_mode()

        # CAENels (OutPut 6) Config
        # (2) = an output will happen whenever a master pulse (virtually) happens
        self.crio.tatu.C6_c0 = 2
        self.crio.tatu.O6_c0 = 5        # Copy an Input (5)
        self.crio.tatu.OCopy6_c0 = 1    # Master Pulse (1)
        self.pvAH501DAveragingTime.put(self.dictionary['time'])
        print("Finished CAENels")

        # Pilatus Config - (Output 5, Input 1)
        self.crio.tatu.C5_c0 = 2
        self.crio.tatu.O5_c0 = 5
        self.crio.tatu.OCopy5_c0 = 1
        print("Finished Pilatus")

        # AnalogRead 9215 CRIO02
        self.pvRIO02AvgTime.put(self.dictionary['time'])
        self.crio.tatu.C7_c0 = 2
        self.crio.tatu.O7_c0 = 5
        self.crio.tatu.OCopy7_c0 = 1
        print("Finished AnalogRead")

        # Pimega 540D - (Output 4, Input 0)
        self.crio.tatu.C4_c0 = 2
        self.crio.tatu.O4_c0 = 'Rising pulse'
        self.crio.tatu.P4_c0 = 1000    # Width pulse 1ms
        print("Finished Pimega")

    def preScanConfig(self):
        """
        Config Command to set Trigger
        """
        self._doingFly = True
        # wait tatu process PV
        sleep(1)
        # Activate Tatu
        self.crio.tatu.activate = 1
        while not self.crio.is_running_tatu():
            self.crio.tatu.activate = 1
            ca.poll(evt=0.01)
        print("Time Start StepFly: ", datetime.now())

    def startFly(self):
        """
        Method for starting a motor fly scan
        """
        self.preScanConfig()

    def wait(self):
        """
        Wait until the motor movement finishes
        """
        while(self._doingFly):
            ca.poll(evt=0.01)
        sleep(self.dictionary['acquire_period'])

        self.crio.tatu.activate = 0
        self.crio.disable_master_mode()
        print("Finished Flyscan")

        sleep(1)
        self.pvPilatusCapture.put(0)

    def stop(self):
        """
        Overwrite the stop motor function
        """
        self.crio.stop_tatu()
        self.crio.disable_master_mode()
