"""GAs Selection System (GASS) class

Python class for GAs Selection System (GASS) device

:platform: Unix
:synopsis: Python class for GAs Selection System (GASS) device

.. moduleauthor:: Carlos Doro <carlos.doro@lnls.br>
.. moduleauthor:: Douglas Bezerra Beniz <douglas.beniz@lnls.br>

"""
import socket
import numpy

from threading import Thread
from queue import Queue
from time import sleep
from enum import Enum

from py4syn.epics.DigitalIOClass        import DigitalIO
from py4syn.epics.BlueRibbonBD306Class  import BlueRibbonBD306

# -----------------------------------------------------------
# Global constants
# -----------------------------------------------------------
MAXIMUM_TIMEOUT = 30        # seconds

# -----------------------------------------------------------
# Valves
# -----------------------------------------------------------
# XAFS2:DIO:bo9       # v1  -   Vacuum
# XAFS2:DIO:bo10      # v2  -   N2
# XAFS2:DIO:bo11      # v3  -   He
# XAFS2:DIO:bo12      # v4  -   Ar
# XAFS2:DIO:bo13      # v5  -   I0
# XAFS2:DIO:bo14      # v6  -   I1
# XAFS2:DIO:bo15      # v7  -   I2
class Valves(Enum):
    Vacuum = 0
    N2 = 1
    He = 2
    Ar = 3
    I0 = 4
    I1 = 5
    I2 = 6

# -----------------------------------------------------------
# Pressures
# -----------------------------------------------------------
# XAFS2:BD306A:P1     # I0
# XAFS2:BD306B:P1     # I1
# XAFS2:BD306B:P2     # I2

# -----------------------------------------------------------
# Table of gas proportions...
# -----------------------------------------------------------
# { <ELEMENT> : { <EDGE> : [ <I0> [N2, He, Ar], <I1> [N2, He, Ar], <I2> [N2, He, Ar] ] } ... }
# -----------------------------------------------------------
GAS_PROPORTIONS  = {'Ac':{  'L1':[[0,0,100],[0,0,100],[0,0,100]],
                            'L2':[[6,0,94],[0,0,100],[0,0,100]],
                            'L3':[[47,0,53],[0,0,100],[0,0,100]]},
                    'As':{  'K': [[80,0,20],[8,0,92],[8,0,92]]},
                    'At':{  'L2':[[37,0,63],[0,0,100],[0,0,100]]},
                    'Au':{  'L1':[[61,0,39],[0,0,100],[0,0,100]],
                            'L2':[[67,0,33],[0,0,100],[0,0,100]],
                            'L3':[[79,0,21],[7,0,93],[7,0,93]]},
                    'Ba':{  'L1':[[74,26,0],[91,0,9],[91,0,9]],
                            'L2':[[60,40,0],[93,0,7],[93,0,7]],
                            'L3':[[52,48,0],[95,0,5],[95,0,5]]},
                    'Bi':{  'L1':[[41,0,58],[0,0,100],[0,0,100]],
                            'L2':[[49,0,51],[0,0,100],[0,0,100]],
                            'L3':[[69,0,31],[0,0,100],[0,0,100]]},
                    'Br':{  'K': [[69,0,31],[0,0,100],[0,0,100]]},
                    'Ca':{  'K': [[15,85,0],[45,55,0],[45,55,0]]},
                    'Ce':{  'L1':[[100,0,0],[85,0,15],[85,0,15]],
                            'L2':[[83,17,0],[89,0,11],[89,0,11]],
                            'L3':[[66,34,0],[92,0,8],[92,0,8]]},
                    'Co':{  'K': [[97,0,3],[76,0,24],[76,0,24]]},
                    'Cr':{  'K': [[74,26,0],[91,0,9],[91,0,9]]},
                    'Cs':{  'L1':[[60,40,0],[93,0,7],[93,0,7]],
                            'L2':[[52,48,0],[95,0,5],[95,0,5]],
                            'L3':[[52,48,0],[96,0,4],[96,0,4]]},
                    'Cu':{  'K': [[93,0,7],[61,0,39],[61,0,39]]},
                    'Dy':{  'L1':[[93,0,7],[60,0,40],[60,0,40]],
                            'L2':[[95,0,5],[66,0,34],[66,0,34]],
                            'L3':[[97,0,3],[75,0,25],[75,0,25]]},
                    'Er':{  'L1':[[90,0,10],[49,0,51],[49,0,51]],
                            'L2':[[92,0,8],[57,0,43],[57,0,43]],
                            'L3':[[95,0,5],[69,0,31],[69,0,31]]},
                    'Eu':{  'L1':[[96,0,4],[72,0,28],[72,0,28]],
                            'L2':[[98,0,2],[77,0,23],[77,0,23]],
                            'L3':[[99,0,1],[83,0,17],[83,0,17]]},
                    'Fe':{  'K': [[100,0,0],[80,0,20],[80,0,20]]},
                    'Fr':{  'L1':[[12,0,88],[0,0,100],[0,0,100]],
                            'L2':[[23,0,77],[0,0,100],[0,0,100]],
                            'L3':[[55,0,45],[0,0,100],[0,0,100]]},
                    'Ga':{  'K': [[87,0,13],[39,0,61],[39,0,61]]},
                    'Gd':{  'L1':[[95,0,5],[69,0,31],[69,0,31]],
                            'L2':[[97,0,3],[74,0,26],[74,0,26]],
                            'L3':[[99,0,1],[81,0,19],[81,0,19]]},
                    'Ge':{  'K': [[84,0,16],[25,0,75],[25,0,75]]},
                    'Hf':{  'L1':[[83,0,17],[21,0,79],[21,0,79]],
                            'L2':[[86,0,14],[32,0,68],[32,0,68]],
                            'L3':[[91,0,9],[52,0,48],[52,0,48]]},
                    'Ho':{  'L1':[[92,0,8],[55,0,45],[55,0,45]],
                            'L2':[[94,0,6],[62,0,38],[62,0,38]],
                            'L3':[[96,0,4],[72,0,28],[72,0,28]]},
                    'I' :{  'L1':[[52,48,0],[96,0,4],[96,0,4]],
                            'L2':[[45,55,0],[95,0,5],[95,0,5]],
                            'L3':[[40,60,0],[100,0,0],[100,0,0]]},
                    'In':{  'L1':[[16,84,0],[53,47,0],[53,47,0]]},
                    'Ir':{  'L1':[[69,0,31],[0,0,100],[0,0,100]],
                            'L2':[[73,0,27],[0,0,100],[0,0,100]],
                            'L3':[[83,0,17],[22,0,78],[22,0,78]]},
                    'La':{  'L1':[[85,15,0],[89,0,11],[89,0,11]],
                            'L2':[[71,29,0],[91,0,9],[91,0,9]],
                            'L3':[[60,40,0],[93,0,7],[93,0,7]]},
                    'Lu':{  'L1':[[85,0,15],[29,0,71],[29,0,71]],
                            'L2':[[88,0,12],[39,0,61],[39,0,61]],
                            'L3':[[92,0,8],[57,0,43],[57,0,43]]},
                    'Mn':{  'K': [[100,0,0],[85,0,15],[85,0,15]]},
                    'Mo':{  'K': [[0,0,100],[0,0,100],[0,0,100]]},
                    'Nb':{  'K': [[7,0,93],[0,0,100],[0,0,100]]},
                    'Nd':{  'L1':[[99,0,1],[82,0,18],[82,0,18]],
                            'L2':[[100,0,0],[85,0,15],[85,0,15]],
                            'L3':[[82,18,0],[89,0,11],[89,0,11]]},
                    'Ni':{  'K': [[95,0,5],[69,0,31],[69,0,31]]},
                    'Os':{  'L1':[[72,0,28],[0,0,100],[0,0,100]],
                            'L2':[[76,0,24],[0,0,100],[0,0,100]],
                            'L3':[[85,0,15],[29,0,71],[29,0,71]]},
                    'Pb':{  'L1':[[47,0,53],[0,0,100],[0,0,100]],
                            'L2':[[54,0,46],[0,0,100],[0,0,100]],
                            'L3':[[72,0,28],[0,0,100],[0,0,100]]},
                    'Pm':{  'L1':[[98,0,2],[79,0,21],[79,0,21]],
                            'L2':[[99,0,1],[83,0,17],[83,0,17]],
                            'L3':[[92,8,0],[87,0,13],[87,0,13]]},
                    'Po':{  'L3':[[66,0,34],[0,0,100],[0,0,100]]},
                    'Pr':{  'L1':[[100,0,0],[84,0,16],[84,0,16]],
                            'L2':[[91,9,0],[87,0,13],[87,0,13]],
                            'L3':[[73,27,0],[91,0,9],[91,0,9]]},
                    'Pt':{  'L1':[[65,0,35],[0,0,100],[0,0,100]],
                            'L2':[[70,0,30],[0,0,100],[0,0,100]],
                            'L3':[[80,0,20],[15,0,85],[15,0,85]]},
                    'Rb':{  'K': [[54,0,46],[0,0,100],[0,0,100]]},
                    'Re':{  'L1':[[75,0,25],[0,0,100],[0,0,100]],
                            'L2':[[79,0,21],[6,0,94],[6,0,94]],
                            'L3':[[87,0,13],[36,0,64],[36,0,64]]},
                    'Sb':{  'L1':[[40,60,0],[100,0,0],[100,0,0]],
                            'L2':[[16,84,0],[53,48,0],[53,48,0]],
                            'L3':[[15,85,0],[45,55,0],[45,55,0]]},
                    'Sc':{  'K': [[35,65,0],[100,0,0],[100,0,0]]},
                    'Se':{  'K': [[74,0,26],[0,0,100],[0,0,100]]},
                    'Sm':{  'L1':[[97,0,3],[76,0,24],[76,0,24]],
                            'L2':[[98,0,2],[80,0,20],[80,0,20]],
                            'L3':[[100,0,0],[85,0,15],[85,0,15]]},
                    'Sn':{  'L1':[[19,81,0],[61,39,0],[61,39,0]],
                            'L2':[[15,85,0],[45,55,0],[45,55,0]]},
                    'Sr':{  'K': [[44,0,56],[0,0,100],[0,0,100]]},
                    'Ta':{  'L1':[[81,0,19],[12,0,88],[12,0,88]],
                            'L2':[[84,0,16],[24,0,76],[24,0,76]],
                            'L3':[[90,0,10],[47,0,53],[47,0,53]]},
                    'Tb':{  'L1':[[94,0,6],[64,0,36],[64,0,36]],
                            'L2':[[96,0,4],[70,0,30],[70,0,30]],
                            'L3':[[98,0,2],[78,0,22],[78,0,22]]},
                    'Te':{  'L1':[[45,55,0],[95,0,5],[95,0,5]],
                            'L3':[[16,84,0],[53,48,0],[53,48,0]],
                            'L3':[[40,60,0],[100,0,0],[100,0,0]]},
                    'Th':{  'L3':[[42,0,58],[0,0,100],[0,0,100]]},
                    'Ti':{  'K': [[45,55,0],[95,0,5],[95,0,5]]},
                    'Tl':{  'L1':[[58,0,42],[0,0,100],[0,0,100]],              # douglas.beniz - to be confirmed!
                            'L2':[[52,0,48],[0,0,100],[0,0,100]],
                            'L3':[[74,0,26],[0,0,100],[0,0,100]]},
                    'Tm':{  'L1':[[89,0,11],[43,0,57],[43,0,57]],
                            'L2':[[91,0,9],[52,0,48],[52,0,48]],
                            'L3':[[94,0,6],[65,0,35],[65,0,35]]},
                    'U' :{  'L1':[[0,0,100],[0,0,100],[0,0,100]],
                            'L2':[[0,0,100],[0,0,100],[0,0,100]],
                            'L3':[[32,0,68],[0,0,100],[0,0,100]]},
                    'V' :{  'K': [[60,40,0],[93,0,7],[93,0,7]]},
                    'W' :{  'L1':[[78,0,22],[2,0,98],[2,0,98]],
                            'L2':[[81,0,19],[15,0,85],[15,0,85]],
                            'L3':[[89,0,11],[42,0,58],[42,0,58]]},
                    'Y' :{  'K': [[34,0,66],[0,0,100],[0,0,100]]},
                    'Yb':{  'L1':[[87,0,13],[37,0,63],[37,0,63]],
                            'L2':[[89,0,11],[46,0,54],[46,0,54]],
                            'L3':[[93,0,7],[61,0,39],[61,0,39]]},
                    'Zn':{  'K': [[90,0,10],[50,0,50],[50,0,50]]},
                    'Zr':{  'K': [[21,0,79],[0,0,100],[0,0,100]]}}

# -----------------------------------------------------------------------------
# Main class
# -----------------------------------------------------------------------------
class GASS():
    """
    Python class to help configuration and control of GAs Selection System devices over EPICS.

    Examples
    --------
        >>> from py4syn.epics.GASSClass import GASS
        >>> gass = GASS("BL:BD306A", 'bd306a')
    """
    def __init__ (self,
                  element,
                  edge,
                  pvValvesDigitalPrefix     =   "XAFS2:DIO:bo",
                  pvValvesDigitalPorts      =   "9-15",
                  pvPressureI0Prefix        =   "XAFS2:BD306A",
                  pvPressureI0Mnemonic      =   "bd306a",
                  pvPressureI1_I2Prefix     =   "XAFS2:BD306B",
                  pvPressureI1_I2Mnemonic   =   "bd306b",
                  pressureVacuum            =   -6.26,
                  pressureWork              =   8.0,
                  extraTimeManifold         =   2.0,
                  extraTimeManifoldVacuum   =   5.0,
                  argonOrder                =   0,
                  heliumOrder               =   1,
                  nitrogenOrder             =   2):
        """
        Constructor

        Parameters
        ----------
        pvValvesDigitalPorts : `string`
            Sequence to IO ports that that open/close valves of Vacuum, N2, He, Ar, I0, I1 and I2 in this ordering; You can use this syntax: "2-6;8"
        """

        # ----------------------------------------------------------------
        # Digital outputs to control valves of gases
        # ----------------------------------------------------------------
        self.valvesDigitalIO = DigitalIO(pvValvesDigitalPrefix, "OUTPUT", pvValvesDigitalPorts)
        self.valvesArray = self.__getPortNumbers(pvValvesDigitalPorts)

        if (len(self.valvesArray) != len(Valves)):
            raise Exception("Inconsistent number of valves!")

        # ----------------------------------------------------------------
        # Bulldog controllers to monitor pressure on ionization chambers
        # ----------------------------------------------------------------
        self.pressureI0 = BlueRibbonBD306(pvPressureI0Prefix, pvPressureI0Mnemonic)
        self.pressureI1_I2 = BlueRibbonBD306(pvPressureI1_I2Prefix, pvPressureI1_I2Mnemonic)

        # Attributes to store element and edge
        self.element = element.title()
        self.edge = edge.title()

        # Pressure parameters
        self.pressureVacuum = pressureVacuum
        self.pressureWork = pressureWork

        # Extra-time to wait after reach target pressure
        self.extraTimeManifold = extraTimeManifold
        self.extraTimeManifoldVacuum = extraTimeManifoldVacuum

        # Attribute to store if all target (chamber) pressures were reached
        self.reachedPressure = numpy.array([False] *3)
        self.enclosureQueue = Queue()

        # Check if informed sequence is consistent
        gasesOrder = [argonOrder, heliumOrder, nitrogenOrder]
        gasesOrderConsistent = True

        try:
            for i in range(len(gasesOrder)):
                gasesOrderConsistent &= (gasesOrder.index(i) > -1)
        except ValueError:
            gasesOrderConsistent = False

        if (gasesOrderConsistent):
            # Just to initiate the array...
            self.gases = [0, 0, 0]

            # Order of gases to fill up the chambers           
            self.gases[argonOrder]    = Valves.Ar
            self.gases[heliumOrder]   = Valves.He
            self.gases[nitrogenOrder] = Valves.N2
        else:
            # --------------------------------------------------
            # 'Ar', 'He' and 'N2' in sequence (default)...
            # --------------------------------------------------
            self.gases = [Valves.Ar, Valves.He, Valves.N2]

    # -------------------------------------------------------------------------
    # Get/Set attributes
    # -------------------------------------------------------------------------
    def set_element(self, element):
        self.element = element.title()

    def get_element(self):
        return self.element.title()

    def set_edge(self, edge):
        self.edge = edge

    def get_edge(self):
        return self.edge

    def set_pressure_vacuum(self, pressVacuum):
        self.pressureVacuum = pressVacuum

    def get_pressure_vacuum(self):
        return self.pressureVacuum

    def set_pressure_work(self, pressWork):
        self.pressureWork = pressWork

    def get_pressure_work(self):
        return self.pressureWork

    def set_extratime_manifold(self, extraTime):
        self.extraTimeManifold = extraTime

    def get_extratime_manifold(self):
        return self.extraTimeManifold

    def set_extratime_manifold_vacuum(self, extraTime):
        self.extraTimeManifoldVacuum = extraTime

    def get_extratime_manifold_vacuum(self):
        return self.extraTimeManifoldVacuum

    # -------------------------------------------------------------------------
    # Valves control
    # -------------------------------------------------------------------------
    def open_valve(self, io_port):
        try:
            self.valvesDigitalIO.putValue(io_port, 1)
        except:
            raise Exception("Error to open valve at I/O: %d" % str(io_port))


    def open_all_valves(self):
        io_port = -1

        try:
            for valve in Valves:
                io_port = self.valvesArray[valve.value]
                # Open
                self.open_valve(io_port)
        except:
            raise Exception("Error to open valve at I/O: %d" % str(io_port))


    def open_all_chambers(self):
        io_port = -1

        try:
            for i in range(Valves.I0.value, Valves.I2.value +1):
                io_port = self.valvesArray[i]
                # Open
                self.open_valve(io_port)
        except:
            raise Exception("Error to open chamber's valve, I/O: %d" % str(io_port))


    def close_valve(self, io_port):
        try:
            self.valvesDigitalIO.putValue(io_port, 0)
        except:
            raise Exception("Error to close valve at I/O: %d" % str(io_port))


    def close_all_valves(self):
        io_port = -1

        try:
            for valve in Valves:
                io_port = self.valvesArray[valve.value]
                # Close
                self.close_valve(io_port)
        except:
            raise Exception("Error to close valve at I/O: %d" % str(io_port))


    def close_all_chambers(self):
        io_port = -1

        try:
            for i in range(Valves.I0.value, Valves.I2.value +1):
                io_port = self.valvesArray[i]
                # Open
                self.close_valve(io_port)
        except:
            raise Exception("Error to close chamber's valve, I/O: %d" % str(io_port))


    # -------------------------------------------------------------------------
    # Procedures to apply vacuum on chambers and manifold
    # -------------------------------------------------------------------------
    def do_vacuum_all_chambers(self):
        try:
            # Close all valves
            self.close_all_valves()

            # Open valves of all chambers
            self.open_all_chambers()

            # Open vacuum valve
            self.open_valve(self.valvesArray[Valves.Vacuum.value])

            # Wait until reach target vacuum pressure on all chambers
            if (self.__waitAllChambersReachPressure(self.pressureVacuum)):
                # Wait an extra-time, just for guarantee
                sleep(self.extraTimeManifold)

            # Close all valves
            self.close_all_valves()
        except Exception as e:
            # Close all valves
            self.close_all_valves()
            # Return false
            return False, e

        return True, "OK"


    def do_vacuum_manifold(self):
        try:
            # Close all valves
            self.close_all_valves()

            # Open vacuum valve
            self.open_valve(self.valvesArray[Valves.Vacuum.value])

            # Wait a while
            sleep(self.extraTimeManifoldVacuum)

            # Close all valves
            self.close_all_valves()
        except:
            # Close all valves
            self.close_all_valves()
            # Return false
            return False

        return True


    # -------------------------------------------------------------------------
    # Procedures to fill chambers with gas(es)
    # -------------------------------------------------------------------------
    def fill_all_chambers(self, purge=False):
        # Close all valves
        self.close_all_valves()

        if (purge):
            # In purge process, use 'N2' to clean all chambers...
            # -----------------------------------------------------------
            # Open 'N2' valve
            self.open_valve(self.valvesArray[Valves.N2.value])

            # Wait an extra-time to guarantee the manifold will be filled before to open chamber valves
            sleep(self.extraTimeManifold)

            # Open all chambers valves
            self.open_all_chambers()

            # Wait until reach target work pressure on all chambers
            if (not self.__waitAllChambersReachPressure(self.pressureWork, greaterThan=True)):
                # Close all valves
                self.close_all_valves()
                # Raise an exception
                raise Exception("Error when purging chambers, aborting...")

            # Close all valves
            self.close_all_valves()
        else:
            """
            # --------------------------------------------------
            # Fill up gas in chambers on this ordering (default)
            # or that one informed by parameter (for all chambers):
            # --------------------------------------------------
            # 1st: 'Ar'   -   heaviest
            # 2nd: 'He'   -   lightest
            # 3rd: 'N2'
            # --------------------------------------------------
            """

            # --------------------------------------------------
            # Generic preparation
            # --------------------------------------------------
            updatedPressures = self.__getChambersPressures()
            deltaPressures = []

            # Check pressures
            # delta = self.pressureWork - P1
            for chamberNumber in range(3):
                deltaPressures.append(self.pressureWork - updatedPressures[chamberNumber])

            for gas in self.gases:
                # Fill with current gas
                self.fill_all_chambers_with_a_gas(enumGas=gas, deltaPressures=deltaPressures)
                # Clean manifold
                self.do_vacuum_manifold()


    def fill_all_chambers_with_a_gas(self, enumGas, deltaPressures):
        # Obtain the target pressures
        targetPressures, updatedPressures  = self.__getTargetPressures(deltaPressures=deltaPressures, indexGas=(enumGas.value - 1))
    
        try:
            print("---------------------------")
            print("enumGas", enumGas.name)
            print("targetPressures", targetPressures)
            print("updatedPressures", updatedPressures)

            # Open 'Gas' valve
            self.open_valve(self.valvesArray[enumGas.value])

            # Wait an extra-time to guarantee the manifold will be filled before to open chamber valves
            sleep(self.extraTimeManifold)

            # -------------------------------------------------------
            # Check if should fill each chamber with that gas...
            for chamberNumber in range(3):
                # Get values
                curPress        = updatedPressures[chamberNumber]
                targetPress     = targetPressures[chamberNumber]

                if (curPress < targetPress):
                    # Open valve of current chamber (I0, I1 or I2)
                    self.open_valve(self.valvesArray[Valves.I0.value + chamberNumber])
        except:
            # Close all valves
            self.close_all_valves()
            # Raise exception
            raise Exception("Error to fill IC with gas %s, aborted!" % (enumGas.name))

        # Wait until reach target work pressure on each chamber, closing each one individually
        if (not self.__waitEachChamberReachPressure(targetPressures, greaterThan=True)):
            # Close all valves
            self.close_all_valves()
            raise Exception()

        # Close all valves
        self.close_all_valves()

        return True


    # -------------------------------------------------------------------------
    # Main procedure to control the purge chambers operation
    # -------------------------------------------------------------------------
    def purge_all_chambers(self):
        # Start doing vacuum on all chambers...
        statusVacuum, statusExecution = self.do_vacuum_all_chambers()
        if (statusVacuum):

            # Fill all chambers with 'N2' (cheaper than 'He')
            self.fill_all_chambers(purge=True)

            # Finally, do vacuum on all chambers again...
            self.do_vacuum_all_chambers()
        else:
            # Close all valves
            self.close_all_valves()
            #raise Exception("Impossible to purge chambers, problem when doing vacuum... %s" % str(statusExecution))
            raise Exception(str(statusExecution))


    # -------------------------------------------------------------------------
    # Main procedure to control an entire procedure to purge and fill up all chambers
    # accordingly with chosen Element and Edge
    # -------------------------------------------------------------------------
    def start(self):
        """
        Main function to proceed with GASS operation...
        """
        # Close all valves...
        self.close_all_valves()

        # Purge chambers...
        self.purge_all_chambers()

        # Fill all chambers with gases depending on element and edge to work with...
        self.fill_all_chambers()

        # Close all valves, just to be sure...
        self.close_all_valves()


    # -------------------------------------------------------------------------
    # Internal use methods
    # -------------------------------------------------------------------------
    def __getChambersPressures(self):
        #
        pressures = []

        try:
            #
            i0_pressure = self.pressureI0.getPressure1()
            pressures.append(i0_pressure)

            i1_pressure = self.pressureI1_I2.getPressure1()
            pressures.append(i1_pressure)

            i2_pressure = self.pressureI1_I2.getPressure2()
            pressures.append(i2_pressure)
        except:
            raise Exception("Error when getting pressures...")

        return pressures


    def __getChamberPressure(self, chamberNumber):
        pressure = None

        # 
        try:
            #
            if (chamberNumber == 0):
                pressure = self.pressureI0.getPressure1()
            elif (chamberNumber == 1):
                pressure = self.pressureI1_I2.getPressure1()
            elif (chamberNumber == 2):
                pressure = self.pressureI1_I2.getPressure2()
        except:
            raise Exception("Error when getting pressure: <%d>" % (chamberNumber))

        return pressure


    def __getTargetPressures(self, deltaPressures, indexGas):
        #
        targetPressures = []
        updatedPressures = self.__getChambersPressures()

        if (GAS_PROPORTIONS.get(self.element).get(self.edge)):
            for chamberNumber in range(3):
                # Get values
                curPress        = updatedPressures[chamberNumber]
                deltaPress      = deltaPressures[chamberNumber]
                gasProportion   = 0.01 * GAS_PROPORTIONS.get(self.element).get(self.edge)[chamberNumber][indexGas]
                # --------------------------------------------------------------
                # targetPressure = P1 + (Proportion * DeltaPressure)
                # --------------------------------------------------------------
                targetPressures.append(curPress + (gasProportion * deltaPress))
        else:
            raise Exception("Element and/or edge is not in table!")

        return targetPressures, updatedPressures


    def __waitAllChambersReachPressure(self, targetPressure, greaterThan=False):
        print("---------------------------")
        print("targetPressure for all chambers", targetPressure)

        return self.__waitEachChamberReachPressure([targetPressure] *3, greaterThan)


    def __waitEachChamberReachPressure(self, targetPressures, greaterThan=False):
        # Wait until reach target vacuum pressure on all chambers
        for chamberNumber in range(3):
            self.reachedPressure[chamberNumber] = False

            targetPress = targetPressures[chamberNumber]

            #if (chamberNumber == 0):
            self.enclosureQueue.put(chamberPressTask(chamberNumber))

            # Start a new Thread to wait desired pressure...
            waitPressure = Thread(target=self.__waitChamberReachPressure, args=(chamberNumber, targetPress, greaterThan))
            waitPressure.setDaemon(True)
            waitPressure.start()

        # Wait all threads finish
        self.enclosureQueue.join()

        if (numpy.all(self.reachedPressure)):
            # Check all pressures...
            updatedPressures = self.__getChambersPressures()
            print("updatedPressures at the end: ", updatedPressures)
            # OK
            return True
        else:
            # Close all valves
            self.close_all_valves()
            # Raise an exception
            raise Exception("Error! Doesn't reach desired pressures!")


    def __waitChamberReachPressure(self, chamberNumber, targetPressure, greaterThan=False):
        # Obtain a task from queue
        chamberPressTask = self.enclosureQueue.get()

        # ----------------------------------------------------------------
        # FIRST APPROACH...
        # ----------------------------------------------------------------
        # Wait until reach target vacuum pressure on all chambers
        waitTime = 0.05      # seconds
        maximumLoops = MAXIMUM_TIMEOUT / waitTime

        stopWaiting = False
        tryNumber   = 0

        while ((not stopWaiting) and (tryNumber < maximumLoops)):
            # Wait a while...
            sleep(waitTime)

            # Check pressure
            updatedPressure = self.__getChamberPressure(chamberNumber)

            if (updatedPressure is not None):
                partialResult = (updatedPressure >= targetPressure) if greaterThan else (updatedPressure <= targetPressure)
                # -------------------------------------------------------------------
                # If this chamber has been reached the target, close its valve
                if (partialResult):
                    self.close_valve(self.valvesArray[Valves.I0.value + chamberNumber])
                    stopWaiting = True

            tryNumber += 1

        # ----------------------------------------------------------------
        # FINE TUNING...
        # ----------------------------------------------------------------
        # Wait until reach target vacuum pressure on all chambers
        waitFineTuning = 1      # seconds
        maximumLoops = MAXIMUM_TIMEOUT / waitFineTuning

        stopWaiting = False
        tryNumber   = 0

        # Just for guarantee, wait a while and double check...
        sleep(waitFineTuning)

        while ((not stopWaiting) and (tryNumber < maximumLoops)):
            # Check pressure
            updatedPressure = self.__getChamberPressure(chamberNumber)

            if (updatedPressure is not None):
                doubleCheckResult = (updatedPressure >= targetPressure) if greaterThan else (updatedPressure <= targetPressure)

                if (doubleCheckResult):
                    # Stop verification
                    self.reachedPressure[chamberNumber] = doubleCheckResult
                    stopWaiting = True
                else:
                    # -------------------------------------------------------------------
                    # If this chamber has not reached the target, re-open chamber just a little moment...
                    self.__toggleValve(self.valvesArray[Valves.I0.value + chamberNumber])

            tryNumber += 1
            # Wait a while...
            sleep(waitFineTuning)

        # End of this thread...
        self.enclosureQueue.task_done()


    def __toggleValve(self, valve, waitTime = 0.02):
        self.open_valve(valve)
        sleep(waitTime)
        self.close_valve(valve)


    def __getPortNumbers(self, port_sequences):
        """
        Receive a sequece of ports and return an integer array with all port numbers.

        Parameters
        ----------
        port_sequences : `string`
            Sequences of port indexes.

        Returns
        ----------
        port_sequence_array : `int`
            Array of all port numbers.
        """

        try:
            port_sequences = str(port_sequences)
            port_sequence = port_sequences.split(';')
            port_sequence_array = []

            for p in port_sequence:
                if len(p.split('-')) >= 1:
                    port_init = p.split('-')[0]
                    port_final = port_init
                if len(p.split('-')) == 2:
                    port_final = p.split('-')[1]

                for x in range(int(port_init),int(port_final)+1):
                    port_sequence_array.append(x)

            return port_sequence_array

        except:
            raise Exception("Error when parsing digital I/O ports")



"""
Auxiliary chamberNumber class for tasks queue
"""
class chamberPressTask():
    def __init__(self, number):
        self.number = number

