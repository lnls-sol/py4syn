import sys
import time
from epics import ca
import py4syn as py4syn
from py4syn.epics.MotorClass import Motor
from py4syn.epics.PseudoMotorClass import PseudoMotor

polling = 0.1
show_info = True

    
def print_no_newline(s):
    """
    Print information without an new line
    
    Parameters
    ----------
    s : `string`
        Text to be printed
        
    """

    sys.stdout.write('\r'+s)
    sys.stdout.flush()

def createPseudoMotor(name ="", description="", backFormula="", forwardDict={}): 
    """
    Create and add a pseudo-motor to the mtrDB dictionary
    
    Parameters
    ----------
    name : `string`
        Mnemonic of the pseudo-motor
    description : `string`
        Description of the pseudo-motor
    backFormula : `string`
        Formula to define the pseudo-motor position based on other motors

        .. note::
            - **Numpy** and **Math** functions can be used on formulas, specially form numpy users must explicit declare it, e.g. `numpy.linalg.solve(..)`
            - **T** refers to the motor **Target** position
            - **A** refers to the motor **Actual** position
            
    forwardDict : `dictionary`
        A dictionary that contains a formula to be applied for each motor when the pseudo-motor is moved
        
        .. note::
            - **Numpy** and **Math** functions can be used on formulas, specially form numpy users must explicit declare it, e.g. `numpy.linalg.solve(..)`
            - **T** refers to the motor **Target** position
            - **A** refers to the motor **Actual** position
            
    Examples
    ----------
    >>> from py4syn.utils.motor import *
    >>> 
    >>> # Define the formula to calculate the Bragg Value
    >>> braggBackFormula = "asin(1.977/A[energy])"
    >>> 
    >>> # Define the relationship between thetaCrystal and bragg target value
    >>> braggForwardDict = {"thetaCrystal": "T[bragg]"}
    >>> 
    >>> # Define the formula to calculate the Energy Value
    >>> energyBackFormula = "1.977/sin(A[thetaCrystal])"
    >>> 
    >>> # Define the relationship between the needed motors and the energy target value
    >>> energyForwardDict = {"bragg": "asin(1.977/T[energy])",
    >>>                      "gap": "A[beamOffset]*tan(T[bragg])/ (sin(T[bragg])+(cos(T[bragg])*tan(T[bragg])))",
    >>>                      "trans":"A[beamOffset]/(sin(T[bragg])+(cos(T[bragg])*tan(T[bragg])))"}
    >>> 
    >>> # Define the formula to calculate the Beam Offset and the 
    >>> beamOffsetBackFormula = "2*A[trans]*tan(A[bragg])*cos(A[bragg])"
    >>> 
    >>> # Define the relationship between the needed motors and the beam offset 
    >>> beamOffsetForwardDict = {"trans": "T[beamOffset]/(sin(A[bragg])+cos(A[bragg])*tan(A[bragg]))",
    >>>                          "gap": "(T[beamOffset]*tan(A[bragg]))/(sin(A[bragg])+(cos(A[bragg])*tan(A[bragg])))"}
    >>> 
    >>> # Crete a simple motor for the 2nd Crystal Translation
    >>> createMotor("trans", "SOL:DMC1:m1")
    >>> 
    >>> # Crete a simple motor for the 2nd Crystal Gap
    >>> createMotor("gap", "SOL:DMC1:m3")
    >>> 
    >>> # Crete a simple motor for the 1st Crystal Rotation
    >>> createMotor("thetaCrystal", "SOL:DMC1:m4")
    >>> 
    >>> 
    >>> # Create the Pseudo motor Bragg, Energy and BeamOffset with the respective formulas and relationships
    >>> createPseudoMotor("bragg", "Bragg Angle (radians)", backFormula=braggBackFormula, forwardDict=braggForwardDict)
    >>> createPseudoMotor("energy", "Energy (kev)", backFormula=energyBackFormula, forwardDict=energyForwardDict)
    >>> createPseudoMotor("beamOffset", "Beam offset (mm)", backFormula=beamOffsetBackFormula, forwardDict=beamOffsetForwardDict)
    >>> 
    >>> # Print all motor positions
    >>> wa()
    >>> 
    >>> # Move the motor Energy to the value 2.
    >>> mv("energy", 4, wait=True)
    >>> 
    >>> # Print all motor positions
    >>> wa()    
        
    """
    try:
        if name not in py4syn.mtrDB:
            py4syn.mtrDB[name] = PseudoMotor(name, description, backFormula, forwardDict)
            if show_info:
                print("")
                print("\tMotor " + name + " created with success.")
        else:
            print("")
            print("\tName " + name + " already created") 
    except Exception as e:
        print ("\tError: ",e)

def createMotor(name ="",PV=""): 
    """
    Create and add a motor to the mtrDB dictionary
    
    Parameters
    ----------
    name : `string`
        Mnemonic of the motor
    PV : `string`
        The Epics PV for this Motor

    Examples
    ----------
    >>> from py4syn.utils.motor import *
    >>> mtop = 'mtop'
    >>> mbot = 'mbot'
    >>> createMotor(mtop,'SOL:DMC1:m3') # creates a motor using the mnemonic and PV.
    >>> createMotor(mbot,'SOL:DMC1:m4')
    >>> umv(mtop, 10) # move the motor mtop to the position 10.
    >>> wa() # print the position of all motors registered.
    >>> mtopPosition = wmr(mtop) # store the motor mtop position in the variable mtopPosition.

    """ 
    try:
        if name not in py4syn.mtrDB:
            py4syn.mtrDB[name] = Motor(PV, name)
            if show_info:
                print("")
                print("\tMotor " + name + " at " + str(PV) + " created with success")
        else:
            print("")
            print("\tName " + name + " already created") 
    except Exception as e:
        print("\tError: ",e)


def umv(motor,position):
    """
    Move the desired motor to an absolute position, waiting until movement ends,and show the position while it happens.
    
    Parameters
    ----------
    motor : `string`
        Mnemonic of the motor used on the `createMotor` and `createPseudoMotor` functions
    position : `double`
        The desired absolute position

    """ 
    try:
        print("")
        if py4syn.mtrDB[motor].getRealPosition()!= position:
            print("\t" + "Moving ",motor)
            py4syn.mtrDB[motor].setAbsolutePosition(position,False)
            time.sleep(polling)
            while py4syn.mtrDB[motor].isMoving():
                print_no_newline("\t%5.4f"%py4syn.mtrDB[motor].getRealPosition())
                time.sleep(polling) 
            print_no_newline("\t%5.4f"%py4syn.mtrDB[motor].getRealPosition())
            py4syn.mtrDB[motor].validateLimits()         
            print("")
    except(KeyboardInterrupt):
        py4syn.mtrDB[motor].stop()
        print("\tStoped")
    except Exception as e:
        py4syn.mtrDB[motor].stop()
        print("\tError: ",e)

def mv(motor,position,wait=True):
    """
    Move the desired motor to an absolute position, can or not wait until movement ends,**don't** show the position while moving.
    
    Parameters
    ----------
    motor : `string`
        Mnemonic of the motor used on the `createMotor` and `createPseudoMotor` functions
    position : `double`
        The desired absolute position
    wait : `bool`
        Optional parameter that indicates if this function must wait until the movement finishes. Default value is True
        
        .. note::
            - If `wait` is set to **False** the code will follow as the motor moves.        
    """ 
    try:
        py4syn.mtrDB[motor].setAbsolutePosition(position,wait)
        time.sleep(polling)
        if wait:
            py4syn.mtrDB[motor].validateLimits()
    except(KeyboardInterrupt):
        py4syn.mtrDB[motor].stop()
        print("\tStoped")
    except Exception as e:
        py4syn.mtrDB[motor].stop()
        print("\tError: ",e)
        
   
#####################################

def umvr(motor,position):
    """
    Move the desired motor to a **relative** position, waiting until movement ends,and show the position while it happens.
    
    Parameters
    ----------
    motor : `string`
        Mnemonic of the motor used on the `createMotor` and `createPseudoMotor` functions
    position : `double`
        The desired relative position

    """ 
    try:
        print("")
        print("\t" + "Moving",str(position))
        py4syn.mtrDB[motor].setRelativePosition(position,False)
        time.sleep(polling)
        while py4syn.mtrDB[motor].isMoving():
            print_no_newline("\t%5.4f"%py4syn.mtrDB[motor].getRealPosition())
            time.sleep(polling)
        print_no_newline("\t%5.4f"%py4syn.mtrDB[motor].getRealPosition())
        py4syn.mtrDB[motor].validateLimits()

        print("")
    except(KeyboardInterrupt):
        py4syn.mtrDB[motor].stop()
        print("\tStoped")
    except Exception as e:
        py4syn.mtrDB[motor].stop()
        print("\tError: ",e)
        

def mvr(motor,position,wait=True):
    """
    Move the desired motor to a **relative** position, can or not wait until movement ends,**don't** show the position while moving.
    
    Parameters
    ----------
    motor : `string`
        Mnemonic of the motor used on the `createMotor` and `createPseudoMotor` functions
    position : `double`
        The desired relative position
    wait : `bool`
        Optional parameter that indicates if this function must wait until the movement finishes. Default value is True
        
        .. note::
            - If `wait` is set to **False** the code will follow as the motor moves.        
    """ 

    try:
        py4syn.mtrDB[motor].setRelativePosition(position,wait)
        time.sleep(polling)
        if wait:
            py4syn.mtrDB[motor].validateLimits()
    except(KeyboardInterrupt):
        py4syn.mtrDB[motor].stop()
        print("\tStoped")
    except Exception as e:
        py4syn.mtrDB[motor].stop()
        print("\tError: ",e)

############################
def tw(mtr,step):
    """
    Move the desired motor relative, wait the movement end and ask if you need to move again
    
    Parameters
    ----------
    mtr : `string`
        Mnemonic of the motor used on the `createMotor` and `createPseudoMotor` functions
    step : `double`
        Desired relative step size
        
    """ 
    
    def is_numeric(s):
        """ Verify if the string is numeric
        :param s: string to verify
        :type s: string
        :return: boolean
    
        ::
         None -- NAN
         True -- Number
        """
        try:
            float(s)
            return True
        except(ValueError):
            pass    

    try:  
  
        value = "+"
        print("")
        while True:
            target = step
            value = input("\t"+mtr+" = %5.4f, Direction (%s):" %(py4syn.mtrDB[mtr].getRealPosition(),value) ) or value
            
            if value != "-" and  value != "+" and is_numeric(value) == None:
                break
            else:
                if value == "-":
                    target = step * -1
                if is_numeric(value):
                    step = float(value)
                    target = step
                    if step < 0:
                        step *= -1
                    if target > 0:
                        value = "+"
                    else:
                        value = "-"
            mvr(mtr,target)
    except KeyboardInterrupt:
        py4syn.mtrDB[mtr].stop()
    except Exception:
        pass

############################

def mmv(**kargs):
    """
    Perform absolute movement in multiple motors at **almost** the same time
    
    Parameters
    ----------
    kargs : `string`
        The motor name and desired position, e.g. x=10,y=10
    """ 

    flag = ""
    for key,value in kargs.items():
        if key not in py4syn.mtrDB:
            flag = key
    if flag == "":
        
        for key,value in kargs.items():
            mv(key,float(value),False)
    else:
        print("Motor " + flag + " Not Found !!!!")
        

def ummv(**kargs):
    """
    Perform absolute movement in multiple motors at **almost** the same time and wait until movement finishes
    
    Parameters
    ----------
    kargs : `string`
        The motor name and desired position, e.g. x=10,y=10
    """ 
    aux={}
    flag = ""
    for key,value in kargs.items():
        if key not in py4syn.mtrDB:
            flag = key

    if flag == "":

        for key,value in kargs.items():
         
            mv(key,float(value),False)
            aux[key] = "MOV"
        try:
            while "MOV" in aux.values():
                for key,value in kargs.items():            
                    if not py4syn.mtrDB[key].isMoving():
                        aux[key] = "STP"
                ca.poll(evt=0.01)

        except(KeyboardInterrupt):
            for key,value in kargs.items():            
                py4syn.mtrDB[key].stop()
            print("\tStoped")
        except Exception as e:
            for key,value in kargs.items():            
                py4syn.mtrDB[key].stop()
            print("\tError: ",e)
    else:
        print("Motor " + flag + " Not Found !!!!")

    
       
def mmvr(**kargs):
    """
    Perform **relative** movement in multiple motors at **almost** the same time
    
    Parameters
    ----------
    kargs : `string`
        The motor name and desired position, e.g. x=10,y=10
    """ 

    flag=""
    for key,value in kargs.items():
        if key not in py4syn.mtrDB:
            flag = key
    if flag == "":
        for key,value in kargs.items():
            mvr(key,float(value),False)
    else:
        print("Motor " + flag + " Not Found !!!!")




def ummvr(**kargs):
    """
    Perform **relative** movement in multiple motors at **almost** the same time and wait until movement finishes
    
    Parameters
    ----------
    kargs : `string`
        The motor name and desired position, e.g. x=10,y=10
    """ 
    aux={}
    flag = ""
    for key,value in kargs.items():
        if key not in py4syn.mtrDB:
            flag = key

    if flag == "":

        for key,value in kargs.items():

            mvr(key,float(value),False)
            aux[key] = "MOV"

        try:
            while "MOV" in aux.values():
                for key,value in kargs.items():            
                    if not py4syn.mtrDB[key].isMoving():
                        aux[key] = "STP"
                ca.poll(evt=0.01)

        except(KeyboardInterrupt):
            for key,value in kargs.items():            
                py4syn.mtrDB[key].stop()
            print("\tStoped")
        except Exception as e:
            for key,value in kargs.items():            
                py4syn.mtrDB[key].stop()
            print("\tError: ",e)
    else:
        print("Motor " + flag + " Not Found !!!!")

def wa():
    """
    Show the motor positions in dial and user coordinates
    
    """ 
    print("")
 
    data = [[] for i in range(len(py4syn.mtrDB)+1)]
    data[0].append("Motor:")
    data[0].append("User:")
    data[0].append("Dial:")
    i = 1
    for mtr in py4syn.mtrDB:
        data[i].append(mtr)
        data[i].append(str ("%5.4f"%py4syn.mtrDB[mtr].getRealPosition()))
        data[i].append(str ("%5.4f"%py4syn.mtrDB[mtr].getDialRealPosition()))
        i+=1


    for row in data:
        print("{0:>20} {1:>20} {2:>20}".format(*row))

def wm(mtr):
    """
    Show the position of one specific motor in dial and user coordinates
    
    Parameters
    ----------
    mtr : `string`
        Mnemonic of the motor used on the `createMotor` and `createPseudoMotor` functions    
    """ 

    print("")
    data = [[]for i in range(2)]
    data[0].append("Motor:")
    data[0].append("User:")
    data[0].append("Dial:")

    data[1].append(mtr)
    data[1].append(str ("%5.4f"%py4syn.mtrDB[mtr].getRealPosition()))
    data[1].append(str ("%5.4f"%py4syn.mtrDB[mtr].getDialRealPosition()))

    for row in data:
        print("{0:>20} {1:>20} {2:>20}".format(*row))

def wmr(mtr):
    """
    Return the motor position in user coordinates
    
    Parameters
    ----------
    mtr : `string`
        Mnemonic of the motor used on the `createMotor` and `createPseudoMotor` functions
        
    Returns
    ----------
    `double`
        Motor position in user coordinates
    """ 
    return py4syn.mtrDB[mtr].getRealPosition()


def lm():
    """
    Show the motors limits in dial and user coordinates
    
    """ 

    data=[[]for i in range(len(py4syn.mtrDB)+1)]
    data[0].append("Motor:")
    data[0].append("User Low Limit:")
    data[0].append("User High Limit:")
    data[0].append("Dial Low Limit:")
    data[0].append("Dial High Limit:")
    i = 1
    print("")
    for mtr in py4syn.mtrDB:
        data[i].append(mtr)
        data[i].append(str (py4syn.mtrDB[mtr].getLowLimitValue()))
        data[i].append(str (py4syn.mtrDB[mtr].getHighLimitValue()))
        data[i].append(str (py4syn.mtrDB[mtr].getDialLowLimitValue()))
        data[i].append(str (py4syn.mtrDB[mtr].getDialHighLimitValue()))
        i+=1

    for row in data:
        print("{0:>20} {1:>20} {2:>20} {3:>20} {4:>20}".format(*row))

def lms():
    """
    Show the motors limits switch state
    
    """ 

    data=[[]for i in range(len(py4syn.mtrDB)+1)]
    data[0].append("Motor:")
    data[0].append("Low Limit Switch:")
    data[0].append("High Limit Switch:")
 
    i = 1
    print("")
    for mtr in py4syn.mtrDB:
        data[i].append(mtr)
        data[i].append(str (py4syn.mtrDB[mtr].isAtLowLimitSwitch()))
        data[i].append(str (py4syn.mtrDB[mtr].isAtHighLimitSwitch()))
        i+=1

    for row in data:
        print("{0:>20} {1:>20} {2:>20}".format(*row))




def set_lm(mtr,ll,hl):
    """
    Set the motor soft limits in user coordinates, will change **DHLM** and **DLLM**
    
    Parameters
    ----------
    mtr : `string`
        Mnemonic of the motor used on the `createMotor` and `createPseudoMotor` functions
    ll : `double`
        Low Soft Limit value
    hl : `double`
        High Soft Limit value        
        
    """

    try:
        h_old = py4syn.mtrDB[mtr].getDialHighLimitValue()
        l_old = py4syn.mtrDB[mtr].getDialLowLimitValue()
        _dpos = py4syn.mtrDB[mtr].getDialPosition()
        _pos = py4syn.mtrDB[mtr].getPosition()
        h_new = (hl + (_dpos- _pos))
        l_new = (ll + (_dpos - _pos))
        py4syn.mtrDB[mtr].setDialHighLimitValue(h_new)
        py4syn.mtrDB[mtr].setDialLowLimitValue(l_new)
        print("")
        print("\tMotor High Limit Reseted from: " + str(h_old) + " to: " + str(h_new))
        print("\tMotor Low Limit Reseted from: " + str(l_old) + " to: " + str(l_new))

    except:
        print("")
        print("\tError!")
        print("")


###################################################

def set_dial(mtr,position):
    """
    Change the motor dial coordinates
    
    Parameters
    ----------
    mtr : `string`
        Mnemonic of the motor used on the `createMotor` and `createPseudoMotor` functions
    position : `double`
        Desired position for dial coordinates
        
    """
    if(isinstance(py4syn.mtrDB[mtr],PseudoMotor)):
        print("")
        print("\tError, set_dial not implemented for Pseudomotors.")
        print("")
        return
    try:
        _old = py4syn.mtrDB[mtr].getDialPosition()
        _off = py4syn.mtrDB[mtr].getOffset()
        _pos = py4syn.mtrDB[mtr].getRealPosition()

        py4syn.mtrDB[mtr].setSETMode()
        py4syn.mtrDB[mtr].setFreezeOffset(1)
        py4syn.mtrDB[mtr].setDialPosition(position)
        time.sleep(0.1)
        py4syn.mtrDB[mtr].setVariableOffset(1)
        py4syn.mtrDB[mtr].setUSEMode()
        time.sleep(0.1)

        if py4syn.mtrDB[mtr].getDirection() == 0:
            value =  _off + (_old - position)
        else:
            value =  _off - (_old-position)


        if py4syn.mtrDB[mtr].getLVIO()==0 :
            py4syn.mtrDB[mtr].setOffset(value)
            print("")
            print("\tMotor " + mtr + " Reseted from: " + str(_old) + " to: " + str(position))
            print("")
        else:
            print("")
            print("\tCheck the dial limits!")
            print("")
    except:
        print("")
        print("\tError!")
        print("")


def set(mtr,position):
    """
    Change the motor user coordinates
    
    Parameters
    ----------
    mtr : `string`
        Mnemonic of the motor used on the `createMotor` and `createPseudoMotor` functions
    position : `double`
        Desired position for user coordinates
        
    """
    try:
        if(isinstance(py4syn.mtrDB[mtr],Motor)):
            _dpos= py4syn.mtrDB[mtr].getDialPosition()
            _pos = py4syn.mtrDB[mtr].getPosition()
            
            if py4syn.mtrDB[mtr].getDirection() == 0:
                value = (position-_dpos)
            else:
                value = (position+_dpos)
      
            py4syn.mtrDB[mtr].setOffset(value)
            print("")
            print("\tMotor " + mtr + " Reseted from: " + str(_pos) + " to: " + str(position))
            print("")
        else:
            py4syn.mtrDB[mtr].setOffset(position)
    except:
        print("")
        print("\tError!")
        print("")

def stop():
    """
    Stops all motors in py4syn.mtrDB dictionary
    
    """

    try:
        for mtr in py4syn.mtrDB:
            py4syn.mtrDB[mtr].stop()
            print("\tMotor " + mtr + " Stopped")
    except:
        print("\tError")
