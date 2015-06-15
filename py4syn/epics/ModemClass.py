"""
FILENAME... ModemClass.py
USAGE...    Python Class for EPICS Modem control
 
/*
 *      Original Author: Hugo Henrique Slepicka
 *      Date: 22/01/2014
 *
 * Modification Log:
 * -----------------
 * .01 22/01/2014 first version released
 */
"""

from epics import Device
from time import sleep
from py4syn.epics.StandardDevice import StandardDevice

class Modem(StandardDevice):

    def onStatusChange(self, value, **kw):
        #print "Modem Status Now is: ", value
        self._status = value

    #CONSTRUCTOR OF MODEM CLASS
    def __init__(self, pvName, mnemonic):
        StandardDevice.__init__(self, mnemonic)
        self.pvName = pvName
        self.modem = Device(pvName+':FONE:', ('discar.PROC','audio','numero','discar.VALA'))
        self._status = self.getStatus()
        self.modem.add_callback('discar.VALA',self.onStatusChange)


    def getStatus(self):
        return self.modem.get('discar.VALA')

    def getDiscar(self):
        return self.modem.get('discar.PROC')

    def setDiscar(self, discar):
        self.setStatus("1 - Aguardando Instrucoes")
        sleep(0.5)
        self.modem.put('discar.PROC', discar)

    def setAudio(self, audio):
        self.modem.put('audio',audio)

    def setNumero(self, numero):
        self.modem.put('numero',numero)

    def setStatus(self, status):
        self.modem.put('discar.VALA',status)
    
    def getStatusCode(self):
        return int(self._status[:2])

    def waitCall(self):
        while self.getStatusCode() < 11:
            sleep(1)
