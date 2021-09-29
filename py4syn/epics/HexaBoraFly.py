from time import sleep
from epics import PV, Device, ca
from py4syn.epics.MotorClass import Motor


class CrioClass(object):

    """ Crio's control class """

    def __init__(self,pv):
        super().__init__()

        self.prefix = pv
        prefix = pv
        sufix = [':InputTriggerIO',
                 ':ConditionIO',
                 ':OutputIO',
                 ':DelayIO',
                 ':PulseIO']

        attributes = []
        self.tatu = Device()

        inputList = [0, 1, 2, 3, 8, 9, 10, 11, 16, 17, 18, 19]
        outputList = [4, 5, 6, 7, 12, 13, 14, 15, 20, 21, 22, 23]
        
        for k in inputList:
            s = ':InputTriggerIO'+str(k)
            p = ':P'+str(k)
            at = 'InTIO'+str(k)
            self.tatu.add_pv(prefix+s, attr=at)
            self.tatu.add_pv(prefix+p, attr=p)
            attributes.append(at)
            #print(prefix+s, '  '+at)
            #print(prefix+p, '  '+p)

        for ele in sufix[1:]:
            for i in outputList:
                self.tatu.add_pv(prefix+':bo'+str(i), attr='bo'+str(i))
                for j in range(3):

                    s = ele + str(i) + ':c' + str(j)
                    at = ele[1]+ str(i) + '_c' + str(j)

                    self.tatu.add_pv(prefix+s, attr=at)
                    attributes.append(at)
                    #print(prefix+s, '  '+at)
        self.tatu.add_pv(prefix+':Activate', attr='activate')
        #self.set_master_mode()
        
    def set_master_mode(self):
        self.tatu.add_pv(self.prefix+':MasterMode', attr='MasterMode')
        self.tatu.add_pv(self.prefix+':MasterPulseNumber', attr='MasterPulseNumber')
        self.tatu.add_pv(self.prefix+':MasterPulsePeriod', attr='MasterPulsePeriod')
        self.tatu.add_pv(self.prefix+':MasterPulseLength', attr='MasterPulseLength')
        self.tatu.add_pv(self.prefix+':Zeropulses', attr='Zeropulses')
        self.tatu.add_pv(self.prefix+':IssuedMasterPulses', attr='IssuedMasterPulses')
        self.tatu.add_pv(self.prefix+':MasterPulsing', attr='MasterPulsing')

    def flyscan_mode(self):
        self.tatu.add_pv(self.prefix+':FlyScan', attr='FlyScan')
        self.tatu.add_pv(self.prefix+':FlyScanFilePath', attr='FlyScanFilePath')
        self.tatu.add_pv(self.prefix+':FlyScanFilePath2', attr='FlyScanFilePath2')
        self.tatu.add_pv(self.prefix+':FlyScanFileName', attr='FlyScanFileName')
        self.tatu.add_pv(self.prefix+':FlyScanFileOpen', attr='FlyScanFileOpen')
        self.tatu.add_pv(self.prefix+':FlyScanFileValidPath', attr='FlyScanFileValidPath')
        self.tatu.add_pv(self.prefix+':FlyScanFileErrorCode', attr='FlyScanFileErrorCode')
        self.tatu.add_pv(self.prefix+':FlyScanFileErrorMsg', attr='FlyScanFileErrorMsg')
        self.tatu.add_pv(self.prefix+':TriggerCounter', attr='TriggerCounter')

class hexaBoraFly(Motor):
    '''Class to control a fly-scan with Symetrie Bora Hexapod'''

    def onStatusChange(self, value, **kw):
        try:
            self._doingFly = (value < self.dictionary['end'])
        except:
            pass

    def __init__(self, pvName, mnemonic):
        super().__init__(pvName, mnemonic)
        self.dictionary = None
        self.TriggerMode = None
        self.pvPmacControler = pvName[:-2]
        print(self.pvPmacControler)
        print(pvName)

        self._doingFly = True

        self.pvInitialPos = PV(self.pvPmacControler + 'trigInitPos')
        self.pvFinalPos = PV(self.pvPmacControler + 'trigFinalPos')
        self.pvStepSize = PV(self.pvPmacControler + 'trigStepSize')
        self.pvFeedBackSize = PV(self.pvPmacControler + 'trigFbkSize')
        self.pvPLC = PV(self.pvPmacControler + 'SendCmd')
        self.pvAbortPLC = PV(self.pvPmacControler + 'trigAbort')
        self.pvStatusPLC = PV(self.pvPmacControler + 'READ_PLCBITS00')
        self.pvRyPos = PV(self.pvName + '.RBV', callback=self.onStatusChange)

        self.crio = CrioClass('CAT:C:RIO01:9403H')

        #TODO: Find a best way the get this PVs
        self.pvAH501DAveragingTime = PV('CAT:T:AH501D:AveragingTime')
        self.pvRIO02AvgTime = PV('CAT:C:RIO02:PvAvgTime')

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
        print("Dictionary: ",self.dictionary)

        """
        self.setInitialPosition()

        print("--------Set Trigger----------")
        #Activate Ry Pmac PLC
        self.sendAbort()
        self.pvPLC.put('enable PLC 1')

        while(self.pvStatusPLC.get()!=2):
            ca.poll(evt=0.01)

        """

    def setInitialPosition(self, value=None):
        """
        Config Command to set Trigger
        

        # Configure Ry Pmac PLC
        self.pvInitialPos.put(self.dictionary['start'])
        self.pvFinalPos.put(self.dictionary['end'])
        step = 0.0
        if self.dictionary['step_mode']:
            step = (self.dictionary['end'] - self.dictionary['start']) / self.dictionary['step_or_points']
        else:
            step = self.dictionary['step_or_points']
        self.pvStepSize.put(step)

        periodUs = int(self.dictionary['aquire_time'] * 1e6)
        timeUs = int(self.dictionary['time'] * 1e6)

        # define pulse width from pmac - unit: units of PLC clock
        self.pvFeedBackSize.put(100)

        #Configure cRIO - TATU
        print("Set cRIO")

        self.crio.tatu.activate = 0
        sleep(0.5)

        # Pmac PLC starting send a edge when reach the first position
        self.crio.tatu.InTIO11 = 2 # Rising (2) = a rising edge detected

        # CAENels (OutPut 6) Config
        self.crio.tatu.C6_c0 = 10       #P11 (10) = if P11 is TRUE, the condition is met.​
        self.crio.tatu.C6_c1 = 10       #P11 (10) = if P11 is TRUE, the condition is met.
        self.crio.tatu.O6_c0 = 'On'        #On (2) = set the output port to 1
        self.crio.tatu.O6_c1 = 'Off'        #Off (1) = set the output port to 0
        self.crio.tatu.D6_c1 = timeUs   #Time (given in μs) to wait before producing the output
        print("Finished CAENels")

        #Pilatus Config - (Output 5, Input 1)
        self.pvAH501DAveragingTime.put(self.dictionary['time'])
        self.crio.tatu.C5_c0 = 10       #P11 (10) = if P11 is TRUE, the condition is met.​
        self.crio.tatu.O5_c0 = 'Rising pulse'        # Rising pulse (4) = a pulse, from 0 to 1 and back to 0.
        self.crio.tatu.P5_c0 = timeUs    # Width pulse 100ms
        print("Finished Pilatus")

        #AnalogRead 9215 CRIO02
        self.pvRIO02AvgTime.put(self.dictionary['time'])
        self.crio.tatu.C7_c0 = 10       #P11 (10) = if P11 is TRUE, the condition is met.
        self.crio.tatu.O7_c0 = 'Rising pulse'
        self.crio.tatu.P7_c0 = timeUs
        print("Finished AnalogRead")

        #Ry waiting Pilatus send a ACK for go to next point
        self.crio.tatu.D15_c0 = periodUs
        #self.crio.tatu.InTIO1 = 1               #Fallin​g (1) = a falling edge detected
        self.crio.tatu.C15_c0 = 10
        self.crio.tatu.O15_c0 = 'Rising pulse'
        self.crio.tatu.P15_c0 = 10000
        print("Finished Ry")

        # Activate Tatu
        self.crio.tatu.activate = 1

        """


    def preScanConfig(self):
        """
        Config Command to set Trigger
        """
        pass


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
        print("Finished Flyscan")
