"""Hexapode Bora controller class

Python class for Hexapode Bora controllers

:platform: Unix
:synopsis: Python class for Hexapode Bora from Symetrie controllers


.. moduleauthors::     Douglas Henrique C. de Araújo <douglas.araujo@lnls.br> 
                       Luciano Carneiro Guedes <luciano.guedes@lnls.br>

"""
from epics import PV,Device
from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice

MOVEERROR=1e-4

class Hexapode(IScannable,StandardDevice):
    def __init__(self, mnemonic, pvName, axis):

        super().__init__(mnemonic)
        self.hexapode = Device(pvName + ':',('STATE#PANEL:SET','STATE#PANEL:GET',
                                'STATE#PANEL:BUTTON','MOVE#PARAM:CM',
                                'MOVE:X', 'MOVE:Y',
                                'MOVE:Z', 'MOVE:RX',
                                'MOVE:RY', 'MOVE:RZ' ,
                                ':POSUSERSIRIUS:X',':POSUSERSIRIUS:Y',':POSUSERSIRIUS:Z',
                                ':POSUSERSIRIUS:RX',':POSUSERSIRIUS:RY',':POSUSERSIRIUS:RZ',
                                ':POSMACH:X',':POSMACH:Y',':POSMACH:Z',
                                ':POSMACH:RX',':POSMACH:RY',':POSMACH:RZ',
                                'CFG#CS:1','CFG#CS:2', 'STATE#POSVALID?',
                                'CFG#CS?:1', 'CFG#CS?:2', 'CFG#CS?:3',
                                'CFG#CS?:4','CFG#CS?:5','CFG#CS?:6',
                                'CFG#CS?:7','CFG#CS?:8','CFG#CS?:9','CFG#CS?:10',
                                'CFG#CS?:11','CFG#CS?:12','CFG#CS?:13'))
        self.axis=axis
        self.axis_dic={"X":1,"Y":2,"Z":3,
                       "RX":4,"RY":5,"RZ":6}
        self.axis_number=self.axis_dic[self.axis]
        self.rbv=PV(pvName + ':'+'POSUSERSIRIUS:'+self.axis)
        self.pos=self.hexapode.get('POSUSERSIRIUS:'+self.axis)       
        self.hexapode.add_callback('POSUSERSIRIUS:'+self.axis, self.onStatusChange)

        self.hexapode.put('POSUSERSIRIUS:'+self.axis +".SCAN",9)

    def onStatusChange(self,value,**kw):
        """
        Returns True if the target position was reached
        """
        if ( abs(float(value) - float(self.pos)) >MOVEERROR):
            self.moving=True
        else:
            self.moving=False

    def getValue(self):
        """
        Returns the current position from the axis
        """
        return self.hexapode.get('POSUSERSIRIUS:'+self.axis)

    def setValue(self, v):
        """
        Set the target position
        Parameters
        ---------
        v: `float`
            Target position
        """
        self.setAbsolutePosition(v)

    def setAbsolutePosition(self, pos, waitComplete=True):
        """
        Set the target position 
        """
        
        self.pos=pos
        self.hexapode.put('STATE#PANEL:SET',11)
        self.hexapode.put('MOVE:'+self.axis, self.pos)
        self.moving=True
        self.wait()

    def wait(self):
        while self.moving:
            pass

        self.stop()

    def stop(self):
        self.hexapode.put('STATE#PANEL:SET',0)
        self.moving = False


#------------------------------------------------------------------------------------------
    def canPerformMovement(self, target):
        """
        Check if a movement to a given position is possible using the limit
        values and backlash distance
        Returns
        -------
        `boolean`
        .. note::
        - **True** -- Motor CAN perform the desired movement;
        - **False** -- Motor **CANNOT** perform the desired movement.
        
        """
        if(self.hexapode.get('STATE#POSVALID?') > 0):
            return False, "Out of SYMETRIE workspace."
 

    def getLimits(self, coord, axis=0): #32 and #33
            #Coord: 0- Machine, 1- users
            #Axis: 0-All, 1-X, 2-Y, 3-Z, 4-RX, 5-RY, 6-RZ

            if(coord != 0 and coord != 1):
                raise ValueError("Invalid value for coord argument. It should be 0 or 1")

            elif(axis < 0 or axis > 6):
                raise ValueError("Invalid value for axis argument. It should be between 1 and 6")

            else:
                stateValue = 32
                if(coord == 1):
                    stateValue = 33

                self.hexapode.put('STATE#PANEL:SET',stateValue)
                if(axis > 0):
                    negLim = self.hexapode.get('CFG#CS?:'+str(2*axis - 1))
                    posLim = self.hexapode.get('CFG#CS?:'+str(2*axis))
                    return negLim, posLim
                else:
                    negLimX = self.hexapode.get('CFG#CS?:1')
                    posLimX = self.hexapode.get('CFG#CS?:2')
                    negLimY = self.hexapode.get('CFG#CS?:3')
                    posLimY = self.hexapode.get('CFG#CS?:4')
                    negLimZ = self.hexapode.get('CFG#CS?:5')
                    posLimZ = self.hexapode.get('CFG#CS?:6')
                    negLimRX = self.hexapode.get('CFG#CS?:7')
                    posLimRX = self.hexapode.get('CFG#CS?:8')
                    negLimRY = self.hexapode.get('CFG#CS?:9')
                    posLimRY = self.hexapode.get('CFG#CS?:10')
                    negLimRZ = self.hexapode.get('CFG#CS?:11')
                    posLimRZ = self.hexapode.get('CFG#CS?:12')
                    enabledLimits = self.hexapode.get('CFG#CS?:13')

                    return (negLimX, posLimX, negLimY, posLimY, 
                        negLimZ, posLimZ, negLimRX, posLimRX, 
                        negLimRY, posLimRY, negLimRZ, posLimRZ, 
                        enabledLimits)

    def getLowLimitValue(self):
           if(self.axis_number < 0 or self.axis_number > 6):
                raise ValueError("Invalid value for axis argument. It should be between 1 and 6")

           else:
                stateValue = 33
                self.hexapode.put('STATE#PANEL:SET',stateValue)
                if(self.axis_number > 0):
                    negLim = self.hexapode.get('CFG#CS?:'+str(2*self.axis_number - 1))
                    posLim = self.hexapode.get('CFG#CS?:'+str(2*self.axis_number))
                    return negLim #, posLim
                else:
                    print("Error getLowLimitValue")

    def getHighLimitValue(self):
           if(self.axis_number < 0 or self.axis_number > 6):
                raise ValueError("Invalid value for axis argument. It should be between 1 and 6")

           else:
                stateValue = 33
                self.hexapode.put('STATE#PANEL:SET',stateValue)
                if(self.axis_number > 0):
                    negLim = self.hexapode.get('CFG#CS?:'+str(2*self.axis_number  - 1))
                    posLim = self.hexapode.get('CFG#CS?:'+str(2*self.axis_number ))
                    return posLim
                else:
                    print("Error getHighLimitValue")

    def getDialLowLimitValue(self):
           if(self.axis_number < 0 or self.axis_number > 6):
                raise ValueError("Invalid value for axis argument. It should be between 1 and 6")

           else:
                stateValue = 32
                self.hexapode.put('STATE#PANEL:SET',stateValue)
                if(self.axis_number > 0):
                    negLim = self.hexapode.get('CFG#CS?:'+str(2*self.axis_number - 1))
                    return negLim
                else:
                    print("Error getDialLowLimitValue")

    def getDialHighLimitValue(self):
           if(self.axis_number < 0 or self.axis_number > 6):
                raise ValueError("Invalid value for axis argument. It should be between 1 and 6")

           else:
                stateValue = 32
                self.hexapode.put('STATE#PANEL:SET',stateValue)
                if(self.axis_number > 0):
                    posLim = self.hexapode.get('CFG#CS?:'+str(2*self.axis_number ))
                    return posLim
                else:
                    print("Error getDialHLimit")

#-------------------Motors-----
    def isMoving(self): 
            return self.moving
    def getRealPosition(self): 
            return self.getValue()
    def getDialRealPosition(self):
            return self.hexapode.get('POSMACH:'+self.axis)
    def validateLimits(self): 
            return self.getLimits(0)
    def setRelativePosition(self,pos,waitComplete=False): 
            target = self.getRealPosition()+pos
            self.setAbsolutePosition(target, waitComplete=waitComplete)
