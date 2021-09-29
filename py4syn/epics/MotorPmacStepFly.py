from time import sleep
from epics import PV, ca
from py4syn.epics.MotorClass import Motor
from datetime import datetime
from py4syn.epics.HexapodeClass import Hexapode
from scan_utils.CrioTatu import CrioTatuClass


class motorPmacStepFly(Motor):
    '''Class to control a step-fly with Pmac PLC routine'''

    def onDoingFly(self, value, **kw):
        try:
            self._doingFly = (value < self.dictionary['end'])
        except:
            pass

    def onHexaTrigger(self, value, **kw):
        print("onHexaTrigger: ", self._forward)
        print("Value: ", value)
        try:
            if value:
                if self._forward:
                    print("Forward")
                    self.pvHexaYPos.put(self.dictionary['end_offset'])
                    sleep(0.2)
                    self.startHexaMove()
                    print("Finished the Move Forward")
                    self._forward = False
                else:
                    print("Reverse")
                    self.pvHexaYPos.put(self.dictionary['start_offset'])
                    sleep(0.2)
                    self.startHexaMove()
                    print("Finished the Move Reverse")
                    self._forward = True
        except:
            pass

    def __init__(self, pvName, mnemonic):
        super().__init__(pvName, mnemonic)
        self.dictionary = None
        self.TriggerMode = None
        self.pvPmacControler = pvName[:-2]

        self._doingFly = True
        self._forward = True

        self.pvInitialPos = PV(self.pvPmacControler + 'trigInitPos')
        self.pvFinalPos = PV(self.pvPmacControler + 'trigFinalPos')
        self.pvStepSize = PV(self.pvPmacControler + 'trigStepSize')
        self.pvFeedBackSize = PV(self.pvPmacControler + 'trigFbkSize')
        self.pvPLC = PV(self.pvPmacControler + 'SendCmd')
        self.pvAbortPLC = PV(self.pvPmacControler + 'trigAbort')
        self.pvStatusPLC = PV(self.pvPmacControler + 'READ_PLCBITS00')
        self.pvRyOffset = PV(self.pvName + '.OFF')
        self.pvRyPos = PV(self.pvName + '.RBV', callback=self.onDoingFly)

        # set velocity to default value
        print("setVelocity")
        self.setVelocity(60)
        self.setAbsolutePosition(self.getRealPosition() + 0.1)

        self.crio = CrioTatuClass('CAT:C:RIO01:9403H')
        self.crio.clear_params()

        # TODO: Find a best way the get this PVs
        self.pvAH501DAveragingTime = PV('CAT:T:AH501D:AveragingTime')
        self.pvRIO02AvgTime = PV('CAT:C:RIO02:PvAvgTime')

        self.pvPilatusCapture = PV('CAT:C:P300K:HDF1:Capture')
        self.pvNumExposuresPimega = PV('CAT:T:PIMEGA540D:cam1:NumExposures')

    def startHexaMove(self, pos):
        _offset = 0.001
        print("startHexaMove")
        self.pvHexaYPos.put(pos, wait=True)
        sleep(0.5)
        self.pvHexaCmd.put(value=11)  # Send move cmd
        print(pos)
        while abs(self.pvHexaYPosRBV.get()) < abs(pos - _offset):
            print(abs(self.pvHexaYPosRBV.get()))
            ca.poll(evt=0.01)
        self.pvHexaCmd.put(value=0)  # reset cmd pv

    def useHexaMove(self):
        self.pvHexaYPosRBV = PV('CAT:C:BORA01:POSUSERSIRIUS:Y')
        self.pvHexaYPos = PV('CAT:C:BORA01:MOVE:Y')
        self.pvHexaCmd = PV('CAT:C:BORA01:STATE#PANEL:SET.VAL')
        self.pvPilatusNumImages = PV('CAT:C:P300K:cam1:NumImages')
        self.pvPilatusNumCaptures = PV('CAT:C:P300K:HDF1:NumCapture')

        print("After all PVs")

        numPoints = len(self.dictionary['points']) * 2
        self.pvPilatusNumImages.put(numPoints)
        self.pvPilatusNumCaptures.put(numPoints)

        print("Before import Hexapode Class")

        self.hexaY = Hexapode('hexa_y', 'CAT:C:BORA01', "Y")
        print("Initial Pos Hexa: ", self.pvHexaYPosRBV.get())

        print(self.dictionary['start_offset'])

        self.startHexaMove(self.dictionary['start_offset'])

        self.pvNumImagesRBV = PV(
            'CAT:T:AH501D:NumAcquired', callback=self.onHexaTrigger)

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

    def sendAbort(self):
        self.pvAbortPLC.put(1)
        sleep(0.5)
        self.pvAbortPLC.put(0)

    def setTrigger(self, dictionary):
        """
        Method for starting a motor fly scan
        """
        self.dictionary = dictionary
        # print("Dictionary: ", self.dictionary)

        print("--------Set Triggers----------")
        self.setInitialPosition()

        # Abort any Ry Pmac PLC running
        self.sendAbort()

    def setInitialPosition(self, value=None):
        """
        Config Command to set Trigger
        """

        self.pvNumExposuresPimega.put(1, wait=True)
        # Configure Ry Pmac PLC
        offset = self.pvRyOffset.get()
        self.pvInitialPos.put(self.dictionary['start'] - offset)
        self.pvFinalPos.put(self.dictionary['end'] - offset)
        step = 0.0
        if self.dictionary['step_mode']:
            step = (self.dictionary['end'] - self.dictionary['start']
                    ) / self.dictionary['step_or_points']
        else:
            step = self.dictionary['step_or_points']
        self.pvStepSize.put(step)

        periodUs = int(self.dictionary['acquire_period'] * 1e6)
        timeUs = int(self.dictionary['time'] * 1e6)

        # define pulse width from pmac - unit: units of PLC clock
        self.pvFeedBackSize.put(100)

        # Configure cRIO - TATU
        print("Set cRIO")

        self.crio.stop_tatu()
        sleep(1)

        # Pmac PLC starting send a edge when reach the first position
        self.crio.tatu.InTIO11 = 2  # Rising (2) = a rising edge detected

        # CAENels (OutPut 6) Config
        # P11 (10) = if P11 is TRUE, the condition is met.​
        self.crio.tatu.C6_c0 = 10
        self.crio.tatu.C6_c1 = 10
        self.crio.tatu.O6_c0 = 'On'  # Rising pulse (4)
        self.crio.tatu.O6_c1 = 'Off'  # Off (1)
        self.crio.tatu.D6_c1 = timeUs  # Time (given in μs)
        # self.crio.tatu.P6_c0 = timeUs
        self.pvAH501DAveragingTime.put(self.dictionary['time'])
        print("Finished CAENels")

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

        # Pimega 540D - (Output 4, Input 0)
        # P11 (10) = if P11 is TRUE, the condition is met.​
        self.crio.tatu.C4_c0 = 10
        # Rising pulse (4) = a pulse, from 0 to 1 and back to 0.
        self.crio.tatu.O4_c0 = 'Rising pulse'
        self.crio.tatu.P4_c0 = 1000    # Width pulse 1ms
        print("Finished Pimega")

        if (self.dictionary['start_offset'] != 0
                or self.dictionary['end_offset'] != 0):
            print("Has offset")

            self.useHexaMove()

            # Configure Hexapod Input
            self.crio.tatu.InTIO8 = 'Rising'  # Rising (1)

            # P8 (7) = if P11 is TRUE, the condition is met.​
            self.crio.tatu.C6_c1 = 7
            self.crio.tatu.O6_c1 = 'Rising pulse'  # Rising pulse (4)
            self.crio.tatu.P6_c1 = timeUs    # Width pulse 100ms
            # P8 (7) = if P11 is TRUE, the condition is met.​
            self.crio.tatu.C5_c1 = 7
            self.crio.tatu.O5_c1 = 'Rising pulse'  # Rising pulse (4)
            self.crio.tatu.P5_c1 = timeUs    # Width pulse 100ms
            # P8 (7) = if P11 is TRUE, the condition is met.​
            self.crio.tatu.C7_c1 = 7
            self.crio.tatu.O7_c1 = 'Rising pulse'  # Rising pulse (4)
            self.crio.tatu.P7_c1 = timeUs    # Width pulse 100ms

            # Ry waiting hexapode condition P19 send ACK for go to next point

            # Configure P19 condition
            # print(self.crio.tatu.EdgestoTrigIO19)
            self.crio.tatu.InTIO19 = 'Rising'
            self.crio.tatu.EdgestoTrigIO19 = 2
            self.crio.tatu.D15_c0 = 0
            self.crio.tatu.C15_c0 = 14  # P19 (14)
            self.crio.tatu.O15_c0 = 'Rising pulse'
            self.crio.tatu.P15_c0 = 1000
            print("Finished Ry")

        else:
            # Ry waiting Pilatus send a ACK for go to next point
            self.crio.tatu.D15_c0 = periodUs
            # self.crio.tatu.InTIO1 = 1     #Fallin​g (1)
            # self.crio.tatu.C15_c0 = 4     #P1
            self.crio.tatu.C15_c0 = 10
            self.crio.tatu.O15_c0 = 'Rising pulse'
            self.crio.tatu.P15_c0 = 1000
            print("Finished Ry")

        sleep(2)

        # Activate Tatu
        self.crio.start_tatu()
        # wait tatu process PV
        sleep(1)

    def preScanConfig(self):
        """
        Config Command to set Trigger
        """
        sleep(2)

        print('preScanConfig')
        # Enable Ry Pmac PLC
        self.pvPLC.put('enable PLC 1')

        # Wait motor reach the initial position
        while(self.pvStatusPLC.get() != 2):
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

        self.crio.stop_tatu()
        print("Finished Flyscan")

        sleep(2)
        self.pvPilatusCapture.put(0)
