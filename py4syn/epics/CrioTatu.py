from epics import PV, Device
from time import sleep


class CrioTatuClass(object):

    """ Crio's control class """

    def __init__(self, pv):
        super().__init__()

        self.prefix = pv
        prefix = pv
        sufix = [':InputTriggerIO',
                 ':ConditionIO',
                 ':OutputIO',
                 ':DelayIO',
                 ':PulseIO',
                 ':OutputCOPYIO']

        attributes = []
        self.tatu = Device()

        self.inputList = [0, 1, 2, 3, 8, 9, 10, 11, 16, 17, 18, 19]
        self.outputList = [4, 5, 6, 7, 12, 13, 14, 15, 20, 21, 22, 23]

        for k in self.inputList:
            s = ':InputTriggerIO'+str(k)
            p = ':P'+str(k)
            at = 'InTIO'+str(k)
            nTriggers = ':EdgestoTrigIO'+str(k)
            self.tatu.add_pv(prefix+s, attr=at)
            self.tatu.add_pv(prefix+p, attr=p)
            self.tatu.add_pv(prefix+nTriggers, attr=nTriggers[1:])
            attributes.append(at)

        for ele in sufix[1:]:
            for i in self.outputList:
                self.tatu.add_pv(prefix+':bo'+str(i), attr='bo'+str(i))
                for j in range(3):

                    s = ele + str(i) + ':c' + str(j)
                    if ele == ':OutputCOPYIO':
                        at = 'OCopy' + str(i) + '_c' + str(j)
                    else:
                        at = ele[1] + str(i) + '_c' + str(j)

                    self.tatu.add_pv(prefix+s, attr=at)
                    attributes.append(at)
                    # print(prefix+s, '  '+at)
        self.tatu.add_pv(prefix+':Activate', attr='activate')
        self.tatu.add_pv(prefix+':TatuActive', attr='active')

        self.create_master_mode_pvs()
        # print(self.tatu._pvs)
        # print(dir(self.tatu))

    def start_tatu(self):
        self.tatu.activate = 1

    def stop_tatu(self):
        self.tatu.activate = 0

    def is_running_tatu(self):
        return self.tatu.active

    def create_master_mode_pvs(self):
        self.tatu.add_pv(self.prefix+':MasterMode', attr='MasterMode')
        self.tatu.add_pv(self.prefix+':MasterPulseNumber',
                         attr='MasterPulseNumber')
        self.tatu.add_pv(self.prefix+':MasterPulsePeriod',
                         attr='MasterPulsePeriod')
        self.tatu.add_pv(self.prefix+':MasterPulseLength',
                         attr='MasterPulseLength')
        self.tatu.add_pv(self.prefix+':Zeropulses', attr='Zeropulses')
        self.tatu.add_pv(self.prefix+':IssuedMasterPulses',
                         attr='IssuedMasterPulses')
        self.tatu.add_pv(self.prefix+':MasterPulsing', attr='MasterPulsing')

    def start_master_mode(self):
        self.tatu.MasterMode = 1

    def disable_master_mode(self):
        self.tatu.MasterMode = 0

    def reset_master_counter(self):
        self.tatu.Zeropulses = 1
        sleep(0.5)
        self.tatu.Zeropulses = 0

    def set_master_pulse_period(self, value):
        self.tatu.MasterPulsePeriod = value

    def set_master_pulse_length(self, value):
        self.tatu.MasterPulseLength = value

    def set_master_pulse_number(self, value):
        self.tatu.MasterPulseNumber = value

    def is_running_master(self):
        return self.tatu.MasterPulsing

    def get_output_attribute_list(self, param):
        list_parms = []
        for _param in self.outputList:
            for c in range(3):
                param_str = param + str(_param) + "_c" + str(c)
                list_parms.append(param_str)
        return list_parms

    def clear_output_params(self, param):
        for attr in self.get_output_attribute_list(param):
            setattr(self.tatu, attr, 0)

    def get_input_attribute_list(self, param):
        list_parms = []
        for _param in self.inputList:
            param_str = param + str(_param)
            list_parms.append(param_str)
        return list_parms

    def clear_input_params(self, param):
        for attr in self.get_input_attribute_list(param):
            setattr(self.tatu, attr, 0)

    def clear_params(self):
        # clear output params
        self.clear_output_params('C')
        self.clear_output_params('D')
        self.clear_output_params('O')
        self.clear_output_params('P')
        self.clear_output_params('OCopy')

        # clear input params
        self.clear_input_params('InTIO')
        self.clear_input_params('EdgestoTrigIO')

    def flyscan_mode(self):
        self.tatu.add_pv(self.prefix+':FlyScan', attr='FlyScan')
        self.tatu.add_pv(self.prefix+':FlyScanFilePath',
                         attr='FlyScanFilePath')
        self.tatu.add_pv(self.prefix+':FlyScanFilePath2',
                         attr='FlyScanFilePath2')
        self.tatu.add_pv(self.prefix+':FlyScanFileName',
                         attr='FlyScanFileName')
        self.tatu.add_pv(self.prefix+':FlyScanFileOpen',
                         attr='FlyScanFileOpen')
        self.tatu.add_pv(self.prefix+':FlyScanFileValidPath',
                         attr='FlyScanFileValidPath')
        self.tatu.add_pv(self.prefix+':FlyScanFileErrorCode',
                         attr='FlyScanFileErrorCode')
        self.tatu.add_pv(self.prefix+':FlyScanFileErrorMsg',
                         attr='FlyScanFileErrorMsg')
        self.tatu.add_pv(self.prefix+':TriggerCounter',
                         attr='TriggerCounter')
