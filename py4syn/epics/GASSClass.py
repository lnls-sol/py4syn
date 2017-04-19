"""GAs Selection System (GASS) class

Python class for GAs Selection System (GASS) device

:platform: Unix
:synopsis: Python class for GAs Selection System (GASS) device

.. moduleauthor:: Carlos Doro <carlos.doro@lnls.br>
.. moduleauthor:: Douglas Bezerra Beniz <douglas.beniz@lnls.br>

"""
import socket

from threading import Thread
from time import sleep
from enum import Enum

from py4syn.epics.DigitalIOClass        import DigitalIO
from py4syn.epics.BlueRibbonBD306Class  import BlueRibbonBD306

# -----------------------------------------------------------
# Global constants
# -----------------------------------------------------------
MAXIMUM_TIMEOUT = 60        # seconds

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
                    'As':{  'K':[[80,0,20],[8,0,92],[0,0,100]]},
                    'At':{  'L2':[[37,0,63],[0,0,100],[0,0,100]]},
                    'Au':{  'L1':[[61,0,39],[0,0,100],[0,0,100]],
                            'L2':[[67,0,33],[0,0,100],[0,0,100]],
                            'L3':[[79,0,21],[7,0,93],[0,0,100]]},
                    'Ba':{  'L1':[[74,26,0],[91,0,9],[82,0,18]],
                            'L2':[[60,40,0],[93,0,7],[87,0,13]],
                            'L3':[[52,48,0],[95,0,5],[90,0,10]]},
                    'Bi':{  'L1':[[41,0,58],[0,0,100],[0,0,100]],
                            'L2':[[49,0,51],[0,0,100],[0,0,100]],
                            'L3':[[69,0,31],[0,0,100],[0,0,100]]},
                    'Br':{  'K':[[69,0,31],[0,0,100],[0,0,100]]},
                    'Ca':{  'K':[[15,85,0],[45,55,0],[70,30,0]]},
                    'Ce':{  'L1':[[100,0,0],[85,0,15],[75,0,25]],
                            'L2':[[83,17,0],[89,0,11],[79,0,21]],
                            'L3':[[66,34,0],[92,0,8],[85,0,15]]},
                    'Co':{  'K':[[97,0,3],[76,0,24],[59,0,41]]},
                    'Cr':{  'K':[[74,26,0],[91,0,9],[82,0,18]]},
                    'Cs':{  'L1':[[60,40,0],[93,0,7],[87,0,13]],
                            'L2':[[52,48,0],[95,0,5],[90,0,10]],
                            'L3':[[52,48,0],[96,0,4],[91,0,9]]},
                    'Cu':{  'K':[[93,0,7],[61,0,39],[35,0,65]]},
                    'Dy':{  'L1':[[93,0,7],[60,0,40],[34,0,66]],
                            'L2':[[95,0,5],[66,0,34],[44,0,56]],
                            'L3':[[97,0,3],[75,0,25],[58,0,42]]},
                    'Er':{  'L1':[[90,0,10],[49,0,51],[17,0,83]],
                            'L2':[[92,0,8],[57,0,43],[29,0,71]],
                            'L3':[[95,0,5],[69,0,31],[48,0,52]]},
                    'Eu':{  'L1':[[96,0,4],[72,0,28],[54,0,46]],
                            'L2':[[98,0,2],[77,0,23],[61,0,39]],
                            'L3':[[99,0,1],[83,0,17],[70,0,30]]},
                    'Fe':{  'K':[[100,0,0],[80,0,20],[70,0,30]]},
                    'Fr':{  'L1':[[12,0,88],[0,0,100],[0,0,100]],
                            'L2':[[23,0,77],[0,0,100],[0,0,100]],
                            'L3':[[55,0,45],[0,0,100],[0,0,100]]},
                    'Ga':{  'K':[[87,0,13],[39,0,61],[0,0,100]]},
                    'Gd':{  'L1':[[95,0,5],[69,0,31],[48,0,52]],
                            'L2':[[97,0,3],[74,0,26],[56,0,44]],
                            'L3':[[99,0,1],[81,0,19],[67,0,33]]},
                    'Ge':{  'K':[[84,0,16],[25,0,75],[0,0,100]]},
                    'Hf':{  'L1':[[83,0,17],[21,0,79],[0,0,100]],
                            'L2':[[86,0,14],[32,0,68],[0,0,100]],
                            'L3':[[91,0,9],[52,0,48],[22,0,78]]},
                    'Ho':{  'L1':[[92,0,8],[55,0,45],[26,0,74]],
                            'L2':[[94,0,6],[62,0,38],[37,0,63]],
                            'L3':[[96,0,4],[72,0,28],[53,0,47]]},
                    'I':{   'L1':[[52,48,0],[96,0,4],[91,0,9]],
                            'L2':[[45,55,0],[95,0,5],[92,0,8]],
                            'L3':[[40,60,0],[100,0,0],[95,0,5]]},
                    'In':{  'L1':[[16,84,0],[53,47,0],[80,20,0]]},
                    'Ir':{  'L1':[[69,0,31],[0,0,100],[0,0,100]],
                            'L2':[[73,0,27],[0,0,100],[0,0,100]],
                            'L3':[[83,0,17],[22,0,78],[0,0,100]]},
                    'La':{  'L1':[[85,15,0],[89,0,11],[79,0,21]],
                            'L2':[[71,29,0],[91,0,9],[83,0,17]],
                            'L3':[[60,40,0],[93,0,7],[87,0,13]]},
                    'Lu':{  'L1':[[85,0,15],[29,0,71],[0,0,100]],
                            'L2':[[88,0,12],[39,0,61],[0,0,100]],
                            'L3':[[92,0,8],[57,0,43],[29,0,71]]},
                    'Mn':{  'K':[[100,0,0],[85,0,15],[75,0,25]]},
                    'Mo':{  'K':[[0,0,100],[0,0,100],[0,0,100]]},
                    'Nb':{  'K':[[7,0,93],[0,0,100],[0,0,100]]},
                    'Nd':{  'L1':[[99,0,1],[82,0,18],[68,0,32]],
                            'L2':[[100,0,0],[85,0,15],[74,0,26]],
                            'L3':[[82,18,0],[89,0,11],[80,0,20]]},
                    'Ni':{  'K':[[95,0,5],[69,0,31],[48,0,52]]},
                    'Os':{  'L1':[[72,0,28],[0,0,100],[0,0,100]],
                            'L2':[[76,0,24],[0,0,100],[0,0,100]],
                            'L3':[[85,0,15],[29,0,71],[0,0,100]]},
                    'Pb':{  'L1':[[47,0,53],[0,0,100],[0,0,100]],
                            'L2':[[54,0,46],[0,0,100],[0,0,100]],
                            'L3':[[72,0,28],[0,0,100],[0,0,100]]},
                    'Pm':{  'L1':[[98,0,2],[79,0,21],[64,0,36]],
                            'L2':[[99,0,1],[83,0,17],[70,0,30]],
                            'L3':[[92,8,0],[87,0,13],[77,0,23]]},
                    'Po':{  'L3':[[66,0,34],[0,0,100],[0,0,100]]},
                    'Pr':{  'L1':[[100,0,0],[84,0,16],[72,0,28]],
                            'L2':[[91,9,0],[87,0,13],[77,0,23]],
                            'L3':[[73,27,0],[91,0,9],[83,0,17]]},
                    'Pt':{  'L1':[[65,0,35],[0,0,100],[0,0,100]],
                            'L2':[[70,0,30],[0,0,100],[0,0,100]],
                            'L3':[[80,0,20],[15,0,85],[0,0,100]]},
                    'Rb':{  'K':[[54,0,46],[0,0,100],[0,0,100]]},
                    'Re':{  'L1':[[75,0,25],[0,0,100],[0,0,100]],
                            'L2':[[79,0,21],[6,0,94],[0,0,100]],
                            'L3':[[87,0,13],[36,0,64],[0,0,100]]},
                    'Sb':{  'L1':[[40,60,0],[100,0,0],[95,0,5]],
                            'L2':[[16,84,0],[53,48,0],[80,20,0]],
                            'L3':[[15,85,0],[45,55,0],[70,30,0]]},
                    'Sc':{  'K':[[35,65,0],[100,0,0],[95,0,5]]},
                    'Se':{  'K':[[74,0,26],[0,0,100],[0,0,100]]},
                    'Sm':{  'L1':[[97,0,3],[76,0,24],[59,0,41]],
                            'L2':[[98,0,2],[80,0,20],[66,0,34]],
                            'L3':[[100,0,0],[85,0,15],[74,0,26]]},
                    'Sn':{  'L1':[[19,81,0],[61,39,0],[93,7,0]],
                            'L2':[[15,85,0],[45,55,0],[70,30,0]]},
                    'Sr':{  'K':[[44,0,56],[0,0,100],[0,0,100]]},
                    'Ta':{  'L1':[[81,0,19],[12,0,88],[0,0,100]],
                            'L2':[[84,0,16],[24,0,76],[0,0,100]],
                            'L3':[[90,0,10],[47,0,53],[14,0,86]]},
                    'Tb':{  'L1':[[94,0,6],[64,0,36],[41,0,59]],
                            'L2':[[96,0,4],[70,0,30],[50,0,50]],
                            'L3':[[98,0,2],[78,0,22],[63,0,37]]},
                    'Te':{  'L1':[[45,55,0],[95,0,5],[92,0,8]],
                            'L3':[[16,84,0],[53,48,0],[80,20,0]],
                            'L3':[[40,60,0],[100,0,0],[95,0,5]]},
                    'Th':{  'L3':[[42,0,58],[0,0,100],[0,0,100]]},
                    'Ti':{  'K':[[45,55,0],[95,0,5],[91,0,9]]},
                    'Tl':{  'L1':[[58,0,42],[0,0,100],[0,0,100]],       # douglas.beniz - to be confirmed!
                            'L2':[[52,0,48],[0,0,100],[0,0,100]],
                            'L3':[[74,0,26],[0,0,100],[0,0,100]]},
                    'Tm':{  'L1':[[89,0,11],[43,0,57],[8,0,92]],
                            'L2':[[91,0,9],[52,0,48],[22,0,78]],
                            'L3':[[94,0,6],[65,0,35],[42,0,58]]},
                    'U':{   'L1':[[0,0,100],[0,0,100],[0,0,100]],
                            'L2':[[0,0,100],[0,0,100],[0,0,100]],
                            'L3':[[32,0,68],[0,0,100],[0,0,100]]},
                    'V':{   'K':[[60,40,0],[93,0,7],[87,0,13]]},
                    'W':{   'L1':[[78,0,22],[2,0,98],[0,0,100]],
                            'L2':[[81,0,19],[15,0,85],[0,0,100]],
                            'L3':[[89,0,11],[42,0,58],[5,0,95]]},
                    'Y':{   'K':[[34,0,66],[0,0,100],[0,0,100]]},
                    'Yb':{  'L1':[[87,0,13],[37,0,63],[0,0,100]],
                            'L2':[[89,0,11],[46,0,54],[11,0,89]],
                            'L3':[[93,0,7],[61,0,39],[36,0,64]]},
                    'Zn':{  'K':[[90,0,10],[50,0,50],[20,0,80]]},
                    'Zr':{  'K':[[21,0,79],[0,0,100],[0,0,100]]}}


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
                  pvValvesDigitalPrefix="XAFS2:DIO:bo",
                  pvValvesDigitalPorts="9-16",
                  pvPressureI0Prefix="XAFS2:BD306A",
                  pvPressureI0Mnemonic="bd306a",
                  pvPressureI1_I2Prefix="XAFS2:BD306B",
                  pvPressureI1_I2Mnemonic="bd306b",
                  pressureVacuum=-6.26,
                  pressureWork=8.0,
                  extraTimeManifold=2.0,
                  extraTimeManifoldVacuum=5.0):
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
        self.element = element
        self.edge = edge

        # Pressure parameters
        self.pressureVacuum = pressureVacuum
        self.pressureWork = pressureWork

        # Extra-time to wait after reach target pressure
        self.extraTimeManifold = extraTimeManifold
        self.extraTimeManifoldVacuum = extraTimeManifoldVacuum


    def set_element(self, element):
        self.element = element


    def set_edge(self, edge):
        self.edge = edge


    def open_valve(self, io_port):
        try:
            self.valvesDigitalIO.putValue(io_port, 1)
        except:
            raise Exception("Error when trying to open valve at I/O: %d" % str(io_port))


    def open_all_valves(self):
        io_port = -1

        try:
            for valve in Valves:
                io_port = self.valvesArray[valve.value]
                # Open
                self.open_valve(io_port)
        except:
            raise Exception("Error when trying to open valve at I/O: %d" % str(io_port))


    def open_all_chambers(self):
        io_port = -1

        try:
            for i in range(Valves.I0.value, Valves.I2.value +1):
                io_port = self.valvesArray[i]
                # Open
                self.open_valve(io_port)
        except:
            raise Exception("Error when trying to open chamber valve at I/O: %d" % str(io_port))


    def close_valve(self, io_port):
        try:
            self.valvesDigitalIO.putValue(io_port, 0)
        except:
            raise Exception("Error when trying to close valve at I/O: %d" % str(io_port))


    def close_all_valves(self):
        io_port = -1

        try:
            for valve in Valves:
                io_port = self.valvesArray[valve.value]
                # Close
                self.close_valve(io_port)
        except:
            raise Exception("Error when trying to close valve at I/O: %d" % str(io_port))


    def close_all_chambers(self):
        io_port = -1

        try:
            for i in range(Valves.I0.value, Valves.I2.value +1):
                io_port = self.valvesArray[i]
                # Open
                self.close_valve(io_port)
        except:
            raise Exception("Error when trying to close chamber valve at I/O: %d" % str(io_port))


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
        except:
            return False

        return True


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
            return False

        return True


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

            # Wait an extra-time to guarantee all chambers are in synch
            sleep(self.extraTimeManifold)

            # Close all valves
            self.close_all_valves()
        else:
            # --------------------------------------------------
            # Fill gas in this ordering (for all chambers):
            # --------------------------------------------------
            # 1st: 'He'   -   lightest
            # 2nd: 'N2'
            # 3rd: 'Ar'   -   heaviest
            # --------------------------------------------------

            # --------------------------------------------------
            # Generic preparation
            # --------------------------------------------------
            updatedPressures = self.__getChambersPressures()
            deltaPressures = []

            # Check pressures
            # delta = self.pressureWork - P1
            for chamberNumber in range(3):
                deltaPressures.append(self.pressureWork - updatedPressures[chamberNumber])

            # --------------------------------------------------
            # 'He'
            # --------------------------------------------------
            self.fill_all_chambers_with_a_gas(enumGas=Valves.He, deltaPressures=deltaPressures)
            # Clean manifold
            self.do_vacuum_manifold()

            # --------------------------------------------------
            # 'N2'
            # --------------------------------------------------
            self.fill_all_chambers_with_a_gas(enumGas=Valves.N2, deltaPressures=deltaPressures)
            # Clean manifold
            self.do_vacuum_manifold()

            # --------------------------------------------------
            # 'Ar'
            # --------------------------------------------------
            self.fill_all_chambers_with_a_gas(enumGas=Valves.Ar, deltaPressures=deltaPressures)
            # Clean manifold
            self.do_vacuum_manifold()


    def fill_all_chambers_with_a_gas(self, enumGas, deltaPressures):
        try:
            targetPressures, updatedPressures  = self.__GetTargetPressures(deltaPressures=deltaPressures, indexGas=(enumGas.value - 1))

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


            # Wait until reach target work pressure on each chamber, closing each one individually
            if (not self.__waitEachChamberReachPressure(targetPressures, greaterThan=True)):
                # Close all valves
                self.close_all_valves()
                # Raise an exception
                raise Exception("Error when filling chambers with gas %s, aborting..." % (enumGas.name))

            # Close all valves
            self.close_all_valves()
        except:
            raise Exception("Error when filling chambers with gas %s, aborting..." % (enumGas.name))

        return True


    def purge_all_chambers(self):
        # Start doing vacuum on all chambers...
        if (self.do_vacuum_all_chambers()):

            # Fill all chambers with 'N2' (cheaper than 'He')
            self.fill_all_chambers(purge=True)

            # Finally, do vacuum on all chambers again...
            self.do_vacuum_all_chambers()
        else:
            raise Exception("Impossible to purge chambers, problem when doing vacuum...")


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


    def __GetTargetPressures(self, deltaPressures, indexGas):
        #
        targetPressures = []
        updatedPressures = self.__getChambersPressures()

        try:
            if (GAS_PROPORTIONS.get(self.element).get(self.edge)):
                for chamberNumber in range(3):
                    # Get values
                    curPress        = updatedPressures[chamberNumber]
                    deltaPress      = deltaPressures[chamberNumber]
                    gasProportion   = GAS_PROPORTIONS.get(self.element).get(self.edge)[chamberNumber][indexGas]
                    # --------------------------------------------------------------
                    # targetPressure = P1 + (Proportion * DeltaPressure)
                    # --------------------------------------------------------------
                    targetPressures.append(curPress + (gasProportion * deltaPress))
            else:
                raise Exception("Element and/or edge not found in proportions table, aborting...")
        except:
            raise Exception("Error when getting target pressures...")

        return targetPressures, updatedPressures

    def __waitAllChambersReachPressure(self, targetPressure, greaterThan=False):
        try:
            # Wait until reach target vacuum pressure on all chambers
            stopWaiting = False

            waitTime = 0.2      # seconds
            maximumLoops = MAXIMUM_TIMEOUT / waitTime

            tryNumber = 0

            while((not stopWaiting) and (tryNumber < maximumLoops)):
                # Wait a while...
                sleep(waitTime)
                # Check pressures
                updatedPressures = self.__getChambersPressures()

                for chamberNumber in range(3):
                    press = updatedPressures[chamberNumber]

                    if (chamberNumber == 0):
                        stopWaiting = (greaterThan ? (press >= targetPressure) : (press <= targetPressure))
                    else:
                        stopWaiting = stopWaiting and (greaterThan ? (press >= targetPressure) : (press <= targetPressure))

                # Increment try number
                tryNumber += 1

            if (tryNumber >= maximumLoops):
                # Close all valves
                self.close_all_valves()
                # Raise an exception
                raise Exception("Error when doing vacuum... did not reach vacuum pressure in %d seconds..." % (MAXIMUM_TIMEOUT))
        except:
            return False

        return True


    def __waitEachChamberReachPressure(self, targetPressures, greaterThan=False):
        try:
            # Wait until reach target vacuum pressure on all chambers
            stopWaiting = False

            waitTime = 0.2      # seconds
            maximumLoops = MAXIMUM_TIMEOUT / waitTime

            tryNumber = 0

            while((not stopWaiting) and (tryNumber < maximumLoops)):
                # Wait a while...
                sleep(waitTime)
                # Check pressures
                updatedPressures = self.__getChambersPressures()

                for chamberNumber in range(3):
                    press = updatedPressures[chamberNumber]
                    reachedTarget = (greaterThan ? (press >= targetPressure) : (press <= targetPressure))

                    # -------------------------------------------------------------------
                    # If this chamber has been reached the target, close its valve
                    if (reachedTarget):
                        self.close_valve(self.valvesArray[Valves.I0.value + chamberNumber])

                    # -------------------------------------------------------------------
                    # Check if all reached the targets
                    if (chamberNumber == 0):
                        stopWaiting = reachedTarget
                    else:
                        stopWaiting = stopWaiting and reachedTarget

                # Increment try number
                tryNumber += 1

            if (tryNumber >= maximumLoops):
                # Close all valves
                self.close_all_valves()
                # Raise an exception
                raise Exception("Error when doing vacuum... did not reach vacuum pressure in %d seconds..." % (MAXIMUM_TIMEOUT))
        except:
            return False

        return True


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

