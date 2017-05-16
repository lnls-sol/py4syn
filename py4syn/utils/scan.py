import collections
import datetime
from enum import Enum
import os

import numpy

import py4syn as py4syn
from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.utils.counter import *
from py4syn.utils.fit import fitGauss
from py4syn.utils.motor import *
from py4syn.utils.plotter import Plotter
from py4syn.writing.FileWriter import FileWriter
from py4syn.writing.DefaultWriter import DefaultWriter


#
#DEFAULT CALLBACKS
#
def defaultPreScanCallback(**kwargs):
    pass

def defaultPostScanCallback(**kwargs):
    pass

def defaultPreScanOperationCallback(**kwargs):
    pass

def defaultScanOperationCallback(**kwargs):
    pass

def defaultPostScanOperationCallback(**kwargs):
    pass

#
#GLOBALS
#
global not_data_fields
not_data_fields = ['scan_object', 'scan_duration', 'scan_start', 'scan_end']

global SCAN_DATA
SCAN_DATA = collections.OrderedDict()

global USER_DATA_FIELDS
USER_DATA_FIELDS = []

global SCAN_CMD
SCAN_CMD = ""

global FILE_WRITER
FILE_WRITER = None

global PARTIAL_WRITE
PARTIAL_WRITE = False

global FILENAME
FILENAME = ""

global XFIELD
XFIELD = ""

global YFIELD
YFIELD = ""

global FWHM
FWHM = 0

global FWHM_AT
FWHM_AT = 0

global COM
COM = 0

global PEAK
PEAK = 0

global PEAK_AT
PEAK_AT = 0

global MIN
MIN = 0

global MIN_AT
MIN_AT = 0

global FITTED_DATA
FITTED_DATA = []

global FIT_RESULT
FIT_RESULT = None

global FIT_SCAN
FIT_SCAN = True

global PRINT_SCAN
PRINT_SCAN = True

global PLOT_GRAPH
PLOT_GRAPH = True

global DAEMON_GRAPH
DAEMON_GRAPH = False

global SCAN_COMMENT
SCAN_COMMENT = ""

global SCAN_PLOTTER
SCAN_PLOTTER = None

global SCAN_PLOTTER_AXIS
SCAN_PLOTTER_AXIS = 1

global PRE_SCAN_CALLBACK
PRE_SCAN_CALLBACK = defaultPreScanCallback

global PRE_POINT_CALLBACK
PRE_POINT_CALLBACK = None

global PRE_OPERATION_CALLBACK
PRE_OPERATION_CALLBACK = defaultPreScanOperationCallback

global OPERATION_CALLBACK
OPERATION_CALLBACK = defaultScanOperationCallback

global POST_OPERATION_CALLBACK
POST_OPERATION_CALLBACK = defaultPostScanOperationCallback

global POST_POINT_CALLBACK
POST_POINT_CALLBACK = None

global POST_SCAN_CALLBACK
POST_SCAN_CALLBACK = defaultPostScanCallback


class ScanType(Enum):
    SCAN = 0
    MESH = 1
    TIME = 2


class ScanStateEnum(str, Enum):
    idle = "idle"
    running = "running"
    error = "error"
    paused = "paused"
    interrupted = "interrupted"


class ScanInterruptedException(Exception):
    '''Scan was interrupted'''
    pass


#
#UTILITARY FUNCTIONS
#
def findDevice(device):
    d = None

    if(isinstance(device, str)):
        if(device in py4syn.mtrDB):
            d = py4syn.mtrDB[device]
        elif(device in globals()):
            d = globals()[device]
    else:
        d = device
    if(isinstance(d, IScannable)):
        return d
    else:
        raise Exception("Error. Only Scannable devices can be used on a scan. Please Check.")

def createUniqueFileName(name):
    import re

    leadingZeros = 4
    fileName, fileExtension = os.path.splitext(name)

    filePath, fileName = os.path.split(fileName)

    # check if fileName contains the number part and if so ignores it to
    # generate the next part
    expression = r'_\d{'+str(leadingZeros)+'}'
    fileName = re.sub(expression,'', fileName, count=1)
    fileName = os.path.join(filePath, fileName)

    newName = ""
    cont = 0
    while(True):
        cont += 1
        newName = fileName + "_" + str(cont).zfill(leadingZeros) + fileExtension
        if(os.path.isfile(newName)):
            continue
        else:
            break

    return newName

def scanHeader():
    global not_data_fields

    # insert scan devices header
    line = ''
    for key in SCAN_DATA.keys():
        if(key in not_data_fields):
            continue
        line += '  ' if line != '' else ''
        line += key

    return line

def fmt(n, precision):
    import math
    try:
        if(math.log10(abs(n)) < -precision):
            return '{:.{}e}'.format(n, precision)
    except Exception:
        pass
    return '{:.{}f}'.format(n, precision)

def scanDataToLine(idx = -1, format=""):
    global not_data_fields
    line = ''
    for key, val in SCAN_DATA.items():
        if(key in not_data_fields):
            continue
        line += ' ' if line != '' else ''
        try:
            if(format != ""):
                try: # some values are not possible to format, e.g strings, arrays, etc...
                    line += fmt(val[idx], int(format))
                except Exception:
                    line += str(val[idx])
            else:
                line += str(val[idx])
        except Exception:
            line += 'N/A'
    return line

def fitData(x, y):
    """
    Try to fit a Gaussian to data and calculate the MAX, FWHM and COM (Center of Mass)

    Parameters
    ----------
    x : `array`
        X data
    y : `array`
        Y data

    Examples
    ----------
    >>> fitData(myDataX, myDataY)
    >>> print("Peak ", PEAK, " at ", PEAK_AT)
    >>> print("Fwhm ", FWHM, " at ", FWHM_AT)
    >>> print("COM = ", COM)

    """
    global FWHM
    global FWHM_AT
    global COM
    global PEAK
    global PEAK_AT
    global MIN
    global MIN_AT
    global FITTED_DATA
    global FIT_RESULT

    X = numpy.asarray(x)
    Y = numpy.asarray(y)
    d = fitGauss(X,Y)
    pkv = d[0]
    pkp = d[1]
    minv = d[2]
    minp = d[3]
    fwhm = d[4]
    fwhmp = d[5]
    com = d[6]
    result = d[7]
    FWHM = fwhm
    FWHM_AT = fwhmp
    COM = com
    PEAK = pkv
    PEAK_AT = pkp
    MIN = minv
    MIN_AT = minp
    try:
        FITTED_DATA = result.best_fit
        FIT_RESULT = result
    except Exception:
        FITTED_DATA = None
        FIT_RESULT = None

def plot():
    """
    Plot a graph using the fields set in XFIELD and YFIELD.

    Examples
    ----------
    >>> setX("m1")
    >>> setY("det")
    >>> plot()

    """
    global XFIELD
    global YFIELD
    global FIT_SCAN
    p = Plotter(title="Plot", daemon=True)
    p.createAxis("", label=YFIELD, xlabel=XFIELD, ylabel=YFIELD,
                 grid=True, line_style="-", line_marker=".",
                 line_color="blue")
    x = SCAN_DATA[XFIELD]
    y = SCAN_DATA[YFIELD]
    p.plot(x, y)

    if(FIT_SCAN):
        fitData(x, y)
        if(PRINT_SCAN):
            print("Peak ", PEAK, " at ", PEAK_AT)
            print("Min ", MIN, " at ", MIN_AT)
            print("FWHM ", FWHM, " at ", FWHM_AT)
            print("COM = ", COM)

#
#SCAN AND MESH WRAPPERS
#
def scan(*args, **kwargs):
    """
    Run a scan with the given parameters

    Parameters
    ----------
    args : `*`
        List of parameters in the following order: device, start, end, points,
        time or device, start, end, device2, start2, end2,..., deviceN, startN,
        endN, points, time, delay.

        .. note::
            To use variable time for each point instead of an value user should
            pass an array with the time to count in each point.

        .. note::
            Instead of the common use of start and end, one can use an array of
            points. Beware that the array length cannot be different of points
            parameter.

        .. note::
            To use delay between points one can use a scalar value representing
            the number of seconds to wait until acquire next point, for
            variable delay time instead of an value user should pass an array.

    Examples
    ----------
    >>> createMotor('m1', 'SOL:DMC1:m1')
    >>> createMotor('m2', 'SOL:DMC1:m2')
    >>> scalerSOL = Scaler("SOL2:SCALER", 10, "scalerSOL")
    >>> createCounter("seconds", scalerSOL, 1, factor=1e+7)
    >>> createCounter("S10", scalerSOL, 10, monitor=True)
    >>> setX("points")
    >>> setY("S10")
    >>> setOutput("/home/ABTLUS/hugo.slepicka/scan1.txt")
    >>> scan('m1', 0, 1, 15, 0.01)
    >>> print("Scan Ended")
    >>> print("Time elapsed: ", SCAN_DATA['scan_duration'])

    """
    import numbers

    global SCAN_CMD
    SCAN_CMD = "scan("+", ".join(map(str, args)) + ")"
    device = None
    countTime = None

    waitingDevice = True
    waitingStart = False
    waitingEnd = False
    waitingSteps = False
    waitingTime = False
    waitingDelay = False

    # Criar Objeto Scan
    if 'scan' in kwargs:
        s = kwargs['scan']
    else:
        s = Scan(ScanType.SCAN)

    param = None

    devs = []
    starts = []
    ends = []
    points = []
    steps = None

    for item in args:
        if(isinstance(item, numbers.Number)):
            waitingDevice = False

        if(waitingDevice):
            # check if its not the time
            device = findDevice(item)

            devs.append(device)

            waitingDevice = False
            waitingStart = True
            waitingEnd = False
            waitingSteps = False
            waitingTime = False
            continue

        if(waitingStart):
            # user sent the points array
            if isinstance(item, collections.Iterable):
                points.append(item)
                starts.append(None)
                ends.append(None)

                waitingDevice = True
                waitingStart = False
                waitingEnd = False
                waitingSteps = True
                waitingTime = False
                continue

            points.append(None)
            starts.append(item)
            waitingDevice = False
            waitingStart = False
            waitingEnd = True
            waitingSteps = False
            waitingTime = False
            continue

        if(waitingEnd):
            ends.append(item)

            waitingDevice = True
            waitingStart = False
            waitingEnd = False
            waitingSteps = True
            waitingTime = False
            continue

        if(waitingSteps):
            steps = item
            for i in range(len(devs)):
                param = ScanParam(devs[i])
                if(starts[i] is None):
                    param.setPoints(points[i])
                else:
                    param.setPoints(starts[i], ends[i], steps)

                s.addScanParam(param)

            waitingDevice = False
            waitingStart = False
            waitingEnd = False
            waitingSteps = False
            waitingTime = True
            continue

        if(waitingTime):
            countTime = item
            if(isinstance(countTime, collections.Iterable)):
                if(s.getNumberOfPoints() != len(countTime)):
                    err_msg = 'Error creating the scan. The time array ({} ' \
                              'points) and the scan ({} points) must have '\
                              'the same number of points. Please check.'
                    raise Exception(err_msg.format(len(countTime),s.getNumberOfPoints()))

            s.setCountTime(countTime)
            waitingTime = False
            waitingDelay = True
            continue

        if(waitingDelay):
            delayTime = item
            if(isinstance(delayTime, collections.Iterable)):
                if(s.getNumberOfPoints() != len(delayTime)):
                    err_msg = 'Error creating the scan. The delay array ({} ' \
                              'points) and the scan ({} points) must have '\
                              'the same number of points. Please check.'
                    raise Exception(err_msg.format(len(delayTime),s.getNumberOfPoints()))
            s.setDelayTime(delayTime)
            continue

    s.start()

def mesh(*kwargs):
    """
    Run a mesh scan with the given parameters

    Parameters
    ----------
    kwargs : `*`
        List of parameters in the following order: device, start, end, points,
        device2, start2, end2, points2, ..., deviceN, startN, endN, pointsN,
        time, delay.

        .. note::
            To use variable time for each point instead of an value user should
            pass an array with the time to count in each point.

        .. note::
            Instead of the common use of start and end, one can use an array of
            points. Beware that the array length cannot be different of points
            parameter. 

        .. note::
            To use delay between points one can use a scalar value representing
            the number of seconds to wait until acquire next point, for
            variable delay time instead of an value user should pass an array.

    Examples
    ----------
    >>> createMotor('m1', 'SOL:DMC1:m1')
    >>> createMotor('m2', 'SOL:DMC1:m2')
    >>> scalerSOL = Scaler("SOL2:SCALER", 10, "scalerSOL")
    >>> createCounter("seconds", scalerSOL, 1, factor=1e+7)
    >>> createCounter("S10", scalerSOL, 10, monitor=True)
    >>> setX("points")
    >>> setY("S10")
    >>> setOutput("/home/ABTLUS/hugo.slepicka/mesh1.txt")
    >>> mesh('m1', 0, 1, 15, 'm2', 0, 180, 1001, 0.01)
    >>> print("Scan Ended")
    >>> print("Time elapsed: ", SCAN_DATA['scan_duration'])

    """
    import numbers

    global SCAN_CMD
    SCAN_CMD = "mesh("+", ".join(map(str, kwargs)) + ")"

    device = None
    start = None
    end = None
    steps = None
    points = None
    countTime = None

    waitingDevice = True
    waitingSteps = False
    waitingTime = False
    waitingDelay = False

    # Criar Objeto Scan
    s = Scan(ScanType.MESH)
    param = None

    for item in kwargs:
        if(isinstance(item, numbers.Number)):
            waitingDevice = False

        if(waitingDevice):
            # check if its not the time
            device = findDevice(item)

            param = ScanParam(device)
            waitingDevice = False
            waitingSteps = True
            start = None
            end = None
            steps = None
            points = None
            continue

        if(waitingSteps):
            # user sent the points array
            if isinstance(item, collections.Iterable):
                points = item
                param.setPoints(points)
                s.addScanParam(param)
                waitingSteps = False
                waitingDevice = True
                waitingTime = True
                continue

            if(start is None):
                start = item
                continue

            if(end is None):
                end = item
                continue

            if(steps is None):
                if not isinstance(item, int):
                    raise Exception('Step value is not a valid integer.' \
                                    'Please check.')

                steps = item
                param.setPoints(start, end, steps)
                s.addScanParam(param)
                waitingSteps = False
                waitingDevice = True
                waitingTime = True
                continue

        if(waitingTime):
            countTime = item
            if(isinstance(countTime, collections.Iterable)):
                if(s.getNumberOfPoints() != len(countTime)):
                    err_msg = 'Error creating the mesh. The time array ({} '\
                              'points) and the mesh ({} points) must have '\
                              'the same number of points. Please check.'
                    raise Exception(err_msg.format(len(countTime),s.getNumberOfPoints()))

            s.setCountTime(countTime)
            waitingDelay = True
            waitingTime = False
            continue

        if(waitingDelay):
            delayTime = item
            if(isinstance(delayTime, collections.Iterable)):
                if(s.getNumberOfPoints() != len(delayTime)):
                    err_msg = 'Error creating the mesh. The delay array ({} '\
                              'points) and the mesh ({} points) must have '\
                              'the same number of points. Please check.'
                    raise Exception(err_msg.format(len(delayTime),s.getNumberOfPoints()))

            s.setDelayTime(delayTime)
            continue

    s.start()

def timescan(t=1, delay=1, repeat=-1):
    """
    Executes a scan in time.

    Parameters
    ----------
    t : `double`
        Time in seconds to count
    delay : `double`
        Time to wait before new count
    repeat : `int`
        Number of repeats to acquire (default is infinity), if repeat = 1
        it will run 2 times an acquire
    """
    global SCAN_CMD
    SCAN_CMD = "timescan("+str(t)+", "+str(delay)+")"

    setX("points")

    # Criar Objeto Scan
    s = Scan(ScanType.TIME)
    s.setCountTime(t)
    s.setDelayTime(delay)
    s.setRepeat(repeat)
    s.start()

"""
SCAN AND SCAN PARAM CLASSES
"""
class Scan(object):
    def __init__(self, type):
        global PRE_SCAN_CALLBACK
        global PRE_POINT_CALLBACK
        global PRE_OPERATION_CALLBACK
        global OPERATION_CALLBACK
        global POST_OPERATION_CALLBACK
        global POST_POINT_CALLBACK
        global POST_SCAN_CALLBACK

        self.setScanType(type)

        # state, pause and interrupt support
        self.__interrupt=False
        self.__pause=False
        self.__state = ScanStateEnum.idle
        self.__pause_polling_rate = 0.1

        self.__scanParams = []
        self.__minNumberOfPoints = 0
        self.__countTime = 1
        self.__delayTime = 0
        self.__repeat = -1

        self.__plotter = None
        self.__plotter_axis = None

        # callbacks
        self.__preScanCallback = PRE_SCAN_CALLBACK
        self.__prePointCallback = PRE_POINT_CALLBACK
        self.__preOperationCallback = PRE_OPERATION_CALLBACK
        self.__operationCallback = OPERATION_CALLBACK
        self.__postOperationCallback = POST_OPERATION_CALLBACK
        self.__postPointCallback = POST_POINT_CALLBACK
        self.__postScanCallback = POST_SCAN_CALLBACK

        # statistics
        self.__startTimestamp = None
        self.__endTimestamp = None

    def __str__(self):
        r = ""
        return r

    def setPlotter(self, p):
        self.__plotter = p

    def getPlotter(self):
        return self.__plotter

    def setPlotterAxis(self, a):
        self.__plotter_axis = a

    def getPlotterAxis(self):
        return self.__plotter_axis

    def setCountTime(self, t):
        self.__countTime = t

    def getCountTime(self):
        return self.__countTime

    def setRepeat(self, r):
        self.__repeat = r

    def getRepeat(self):
        return self.__repeat

    def setDelayTime(self, t):
        self.__delayTime = t

    def getDelayTime(self):
        return self.__delayTime

    def setScanType(self, t):
        if(t not in ScanType):
            raise Exception(t + " is not a valid ScanType, please check!")

        self.__scanType = t

    def addScanParam(self, param):
        if(self.__scanType == ScanType.SCAN):
            if (len(self.__scanParams) != 0) and (param.getNumberOfPoints() !=
                                                  self.__minNumberOfPoints):
                raise Exception('All devices must have the same number of'\
                                'points, please check.')
            else:
                self.__minNumberOfPoints = param.getNumberOfPoints()

        self.__scanParams.append(param)

    def getScanParams(self):
        return self.__scanParams

    def setPreScanCallback(self, call):
        self.__preScanCallback = call

    def getPreScanCallback(self):
        return self.__preScanCallback

    def setPrePointCallback(self, call):
        self.__prePointCallback = call

    def getPrePointCallback(self):
        return self.__prePointCallback

    def setPreOperationCallback(self, call):
        self.__preOperationCallback = call

    def getPreOperationCallback(self):
        return self.__preOperationCallback

    def setOperationCallback(self, call):
        self.__operationCallback = call

    def getOperationCallback(self):
        return self.__operationCallback

    def setPostOperationCallback(self, call):
        self.__postOperationCallback = call

    def getPostOperationCallback(self):
        return self.__postOperationCallback

    def setPostPointCallback(self, call):
        self.__postPointCallback = call

    def getPostPointCallback(self):
        return self.__postPointCallback

    def setPostScanCallback(self, call):
        self.__postScanCallback = call

    def getPostScanCallback(self):
        return self.__postScanCallback

    def getNumberOfParams(self):
        return len(self.__scanParams)

    def getNumberOfPoints(self):
        if(self.__scanType == ScanType.SCAN):
            return self.__minNumberOfPoints
        elif(self.__scanType == ScanType.MESH):
            total = 1
            for p in self.__scanParams:
                total *= len(p.getPoints())
            return total

    def getStartTimestamp(self):
        return self.__startTimestamp

    def getEndTimestamp(self):
        return self.__endTimestamp

    def getElapsedTime(self):
        return self.__endTimestamp - self.__startTimestamp

    def getElapsedTimePerPoint(self):
        return self.getElapsedTime() / self.getNumberOfPoints()

    def setPausePoolingRate(rate):
        self.__pause_pooling_rate = float(rate)

    def interrupt(self):
        self.__interrupt=True
        self.__pause=False

    def pause(self):
        self.__pause=True

    def resume(self):
        if self.__state == ScanStateEnum.paused:
            self.__pause = False
        else:
            raise ValueError('Cannot resume, scan is not paused. Current state is: {}'.format(self.__state))

    def getState(self):
        return self.__state

    def start(self):
        import datetime
        global XFIELD
        global YFIELD
        global USER_DATA_FIELDS

        global FILENAME
        global PARTIAL_WRITE
        global FILE_WRITER
        global SCAN_DATA
        global SCAN_COMMENT
        global SCAN_CMD

        # Setup of File Writer
        if FILE_WRITER is None:
            if(FILENAME is not None and FILENAME != ""):
                FILENAME = createUniqueFileName(FILENAME)
                FILE_WRITER = DefaultWriter(FILENAME)

        # Setup of SCAN_DATA with points, scannable and countable        
        SCAN_DATA = collections.OrderedDict()
        SCAN_DATA['points'] = []
        SCAN_DATA['scan_object'] = self

        for p in self.getScanParams():
            dev = p.getDevice()
            SCAN_DATA[dev.getMnemonic()] = []
            if(FILE_WRITER is not None):
                FILE_WRITER.insertDevice(dev.getMnemonic())

        for c in py4syn.counterDB:
            if(py4syn.counterDB[c]['enable']):
                SCAN_DATA[c] = []
                if(FILE_WRITER is not None):
                    FILE_WRITER.insertSignal(c)

        for u in USER_DATA_FIELDS:
            SCAN_DATA[u] = []
            if(FILE_WRITER is not None):
                FILE_WRITER.insertSignal(u)

        # if no value is passed, assume the first device of the scan
        if(XFIELD is None or XFIELD == "" or (XFIELD not in SCAN_DATA)):
            XFIELD = self.getScanParams()[0].getDevice().getMnemonic()

        # if no value is passed, assume the first device of the scan
        if(YFIELD is None or YFIELD == "" or (YFIELD not in SCAN_DATA)):
            try:
                YFIELD = list(py4syn.counterDB.keys())[0]
            except IndexError:
                YFIELD = XFIELD


        try:
            self.__startTimestamp = datetime.datetime.now()

            # Header Fields
            if(FILE_WRITER is not None):
                FILE_WRITER.setStartDate(self.__startTimestamp)
                FILE_WRITER.insertComment(SCAN_COMMENT)
                FILE_WRITER.setUsername(os.getlogin())
                FILE_WRITER.setCommand(SCAN_CMD)
                FILE_WRITER.setDataSize(self.getNumberOfPoints())


            # If its a partial write the header must be ready
            if(PARTIAL_WRITE and FILE_WRITER is not None):
                FILE_WRITER.writeHeader()

            # Define the scan as Running
            self.__state = ScanStateEnum.running

            if(self.__scanType == ScanType.SCAN):
                self.doScan()
            elif(self.__scanType == ScanType.MESH):
                self.doMesh()
            elif(self.__scanType == ScanType.TIME):
                self.doTime()
            else:
                self.__startTimestamp = datetime.datetime.now()
                self.__endTimestamp = datetime.datetime.now()
                raise Exception("Invalid Scan Type. Please Check.")

            self.__endTimestamp = datetime.datetime.now()
            self.__state = ScanStateEnum.idle

            if not PARTIAL_WRITE and FILE_WRITER is not None:
                print("\tSaving data to file: {}".format(FILENAME))
                FILE_WRITER.setEndDate(self.__endTimestamp)
                FILE_WRITER.writeHeader()
                FILE_WRITER.writeData(idx=-1)

        except KeyboardInterrupt:
            self.__endTimestamp = datetime.datetime.now()
            self.__state = ScanStateEnum.interrupted
            print("\tUser Interrupted")
            if(FILENAME is not None and FILENAME != "" and not PARTIAL_WRITE
               and FILE_WRITER is not None):
                print("\tSaving data to file: {}".format(FILENAME))
                FILE_WRITER.setEndDate(self.__endTimestamp)
                FILE_WRITER.writeHeader()
                FILE_WRITER.writeData(idx=-1)

        try:
            if(FILE_WRITER is not None):
                FILE_WRITER.close()
        except:
            pass

        self.__cleanup()

        SCAN_DATA['scan_start'] = self.getStartTimestamp()
        SCAN_DATA['scan_end'] = self.getEndTimestamp()
        SCAN_DATA['scan_duration'] = self.getElapsedTime()

    def __cleanup(self):
        global USER_DATA_FIELDS
        global FILE_WRITER
        global SCAN_PLOTTER
        global SCAN_PLOTTER_AXIS

        FILE_WRITER = None
        SCAN_PLOTTER = None
        SCAN_PLOTTER_AXIS = 1


    def __waitDevices(self):
        for p in self.getScanParams():
            p.getDevice().wait()

    def __launchCounters(self, **kwargs):
        t = self.getCountTime()
        idxs = kwargs["idx"]

        if isinstance(t, collections.Iterable):
            t = t[int(idxs[-1])]

        if(t < 0):
            ctr(t * -1, use_monitor=True, wait=False)
        else:
            ctr(t, wait=False)

    def __waitDelay(self, **kwargs):
        from time import sleep

        t = self.getDelayTime()

        idx = int(SCAN_DATA["points"][-1])

        if isinstance(t, collections.Iterable):
            t = t[idx]

        if(t > 0):
            time.sleep(t)

    def __saveCounterData(self, **kwargs):
        t = self.getCountTime()
        idxs = kwargs["idx"]

        if isinstance(t, collections.Iterable):
            t = t[int(idxs[-1])]

        if(t < 0):
            waitAll(monitor=True)
        else:
            waitAll(monitor=False)

        stopAll()

        d = getCountersData()

        for k, v in d.items():
            SCAN_DATA[k].append(v)


    def __printAndPlot(self, **kwargs):
        p = self.getPlotter()
        if(PLOT_GRAPH):
            p.plot(SCAN_DATA[XFIELD][-1], SCAN_DATA[YFIELD][-1],
                   axis=self.getPlotterAxis())

        if(PRINT_SCAN):
            print(scanDataToLine(format="4"))

    def __writeData(self, idx):
        global PARTIAL_WRITE
        global FILE_WRITER
        global SCAN_DATA

        if (FILE_WRITER is not None):
            for d in FILE_WRITER.getDevices():
                try:
                    FILE_WRITER.insertDeviceData(d, SCAN_DATA[d][idx])
                except:
                    pass

            for s in FILE_WRITER.getSignals():
                try:
                    FILE_WRITER.insertSignalData(s, SCAN_DATA[s][idx])
                except:
                    pass

            if PARTIAL_WRITE:
                FILE_WRITER.writeData(partial=PARTIAL_WRITE, idx=idx)

    def __initialize(self):
        global XFIELD
        global YFIELD
        global FILENAME
        global PLOT_GRAPH
        global PRINT_SCAN
        global DAEMON_GRAPH
        global SCAN_PLOTTER
        global SCAN_PLOTTER_AXIS

        s = self

        if(PLOT_GRAPH):
            if(SCAN_PLOTTER is None):
                p = Plotter("Scan: " + str(FILENAME), daemon=DAEMON_GRAPH)
                p.createAxis("", label=YFIELD, xlabel=XFIELD, ylabel=YFIELD,
                             grid=True, line_style="-", line_marker=".",
                             line_color="blue")
                SCAN_PLOTTER = p
            else:
                p = SCAN_PLOTTER

            s.setPlotter(p)

            if(SCAN_PLOTTER_AXIS is None or SCAN_PLOTTER_AXIS < 1):
                SCAN_PLOTTER_AXIS = 1
            s.setPlotterAxis(SCAN_PLOTTER_AXIS)

        if(PRINT_SCAN):
            print(scanHeader())

    def __terminate(self):
        global SCAN_DATA
        global FWHM
        global FWHM_AT
        global COM
        global PEAK
        global PEAK_AT
        global FIT_SCAN

        x = SCAN_DATA[XFIELD]
        y = SCAN_DATA[YFIELD]
        if(FIT_SCAN):
            fitData(x, y)
            if(PRINT_SCAN):
                print("Peak = ", PEAK, " at ", PEAK_AT)
                print("Fwhm = ", FWHM, " at ", FWHM_AT)
                print("COM = ", COM)


    def __check_pause_interrupt(self, pointIdx):
        if self.__pause:
            self.__state = ScanStateEnum.paused
            print('Pausing scan before point {}:'.format(pointIdx))
            while self.__pause:
                time.sleep(self.__pause_polling_rate)
            if not self.__interrupt:
                print('Resuming scan at point {}:'.format(pointIdx))

        if self.__interrupt:
            self.__state = ScanStateEnum.interrupted
            print('Aborting the Scan... Please wait for cleanup!')
            raise ScanInterruptedException()


    def doMesh(self):
        """
        IDX = MOD(QUOTIENT(I,MULT(Steps(N->1))),Steps(N))
        """
        import operator
        import functools

        numberOfStepsArray = [p.getNumberOfPoints() for p in self.getScanParams()]
        multiplicationIndexArray = numpy.zeros(self.getNumberOfParams(), dtype=int)
        for i in range(0, self.getNumberOfParams()):
            if(i == self.getNumberOfParams() - 1):
                multiplicationIndexArray[i] = 1
            else:
                multiplicationIndexArray[i] = functools.reduce(operator.mul, numberOfStepsArray[i + 1:])

        def calculatePositionIndex(idx, divisor, steps):
            """
            IDX = MOD(QUOTIENT(I,MULT(Steps(N->1))),Steps(N))
            """
            p1 = (idx // divisor)
            p2 = p1 % steps
            return p2

        # Arrays to store positions and indexes to be used as callback arguments
        positions = []
        indexes = []

        # Pre Scan Callback
        if(self.__preScanCallback):
            self.__preScanCallback(scan=self, pos=positions, idx=indexes)

        self.__initialize()

        # Scan main loop
        for pointIdx in range(0, self.getNumberOfPoints()):
            # Saves point index at SCAN_DATA
            SCAN_DATA['points'].append(pointIdx)

            # Pre Point Callback
            if(self.__prePointCallback):
                self.__prePointCallback(scan=self, pos=positions, idx=indexes)

            # verify pauses and interrupts
            try:
                self.__check_pause_interrupt(pointIdx)
            except ScanInterruptedException:
                break

            self.__waitDelay(scan=self, pos=positions, idx=indexes)

            positions = []
            indexes = []

            # iterate over each device (Scan Param)
            for deviceIdx in range(0, self.getNumberOfParams()):
                # Grab the ScanParam
                param = self.getScanParams()[deviceIdx]

                # Calculate the Index based on the scan point index and on the multiplication array
                idx = calculatePositionIndex(pointIdx,
                                             multiplicationIndexArray[deviceIdx],
                                             param.getNumberOfPoints())

                # Set the setpoint into device
                param.getDevice().setValue(param.getPoints()[idx])

                # Store the index and the position of the device for callbacks
                indexes.append(idx)

            # Wait for devices to reach the desired set point
            self.__waitDevices()

            for deviceIdx in range(0, self.getNumberOfParams()):
                # Grab the ScanParam
                param = self.getScanParams()[deviceIdx]

                # Store the index and the position of the device for callbacks
                positions.append(param.getDevice().getValue())

                # Saves device position at SCAN_DATA
                SCAN_DATA[param.getDevice().getMnemonic()].append(param.getDevice().getValue())

            # Pre Operation Callback
            if(self.__preOperationCallback):
                self.__preOperationCallback(scan=self, pos=positions, idx=indexes)

            # Launch the counters
            self.__launchCounters(scan=self, pos=positions, idx=indexes)

            # Operation Callback
            if(self.__operationCallback):
                self.__operationCallback(scan=self, pos=positions, idx=indexes)

            # Save data to SCAN_DATA
            self.__saveCounterData(scan=self, pos=positions, idx=indexes)

            # Post Operation Callback
            if(self.__postOperationCallback):
                self.__postOperationCallback(scan=self, pos=positions, idx=indexes)

            self.__writeData(idx=pointIdx)

            # Updates the screen and plotter
            self.__printAndPlot()

            # Post Point Callback
            if(self.__postPointCallback):
                self.__postPointCallback(scan=self, pos=positions, idx=indexes)

        self.__terminate()

        # Post Scan Callback
        if(self.__postScanCallback):
            self.__postScanCallback(scan=self)

    def doScan(self):
        # Arrays to store positions and indexes to be used as callback arguments
        positions = []
        indexes = []


        # Pre Scan Callback
        if(self.__preScanCallback):
            self.__preScanCallback(scan=self, pos=positions, idx=indexes)

        self.__initialize()

        for pointIdx in range(0, self.getNumberOfPoints()):
            # Saves point index at SCAN_DATA
            SCAN_DATA['points'].append(pointIdx)

            # Pre Point Callback
            if(self.__prePointCallback):
                self.__prePointCallback(scan=self, pos=positions, idx=indexes)

            # verify pauses and interrupts
            try:
                self.__check_pause_interrupt(pointIdx)
            except ScanInterruptedException:
                break

            self.__waitDelay(scan=self, pos=positions, idx=indexes)

            positions = []
            indexes = []

            for deviceIdx in range(0, self.getNumberOfParams()):
                param = self.getScanParams()[deviceIdx]
                param.getDevice().setValue(param.getPoints()[pointIdx])
                indexes.append(pointIdx)

            self.__waitDevices()

            for deviceIdx in range(0, self.getNumberOfParams()):
                param = self.getScanParams()[deviceIdx]
                positions.append(param.getDevice().getValue())
                # Saves device position at SCAN_DATA
                SCAN_DATA[param.getDevice().getMnemonic()].append(param.getDevice().getValue())

            # Pre Operation Callback
            if(self.__preOperationCallback):
                self.__preOperationCallback(scan=self, pos=positions, idx=indexes)

            # Launch the counters
            self.__launchCounters(scan=self, pos=positions, idx=indexes)

            # Operation Callback
            if(self.__operationCallback):
                self.__operationCallback(scan=self, pos=positions, idx=indexes)

            # Save data to SCAN_DATA
            self.__saveCounterData(scan=self, pos=positions, idx=indexes)

            # Post Operation Callback
            if(self.__postOperationCallback):
                self.__postOperationCallback(scan=self, pos=positions, idx=indexes)

            self.__writeData(idx=pointIdx)

            # Updates the screen and plotter
            self.__printAndPlot()

            # Post Point Callback
            if(self.__postPointCallback):
                self.__postPointCallback(scan=self, pos=positions, idx=indexes)

        self.__terminate()

        # Post Scan Callback
        if(self.__postScanCallback):
            self.__postScanCallback(scan=self)

    def doTime(self):
        positions = []
        indexes = []

        # Pre Scan Callback
        if(self.__preScanCallback):
            self.__preScanCallback(scan=self)

        self.__initialize()

        pointIdx = 0
        while(True):
           # Pre Point Callback
            if(self.__prePointCallback):
                self.__prePointCallback(scan=self, pos=positions, idx=indexes)

            # verify pauses and interrupts
            try:
                self.__check_pause_interrupt(pointIdx)
            except ScanInterruptedException:
                break

            # Saves point index at SCAN_DATA
            SCAN_DATA['points'].append(pointIdx)

            positions = [pointIdx]
            indexes = [pointIdx]

            self.__waitDelay(scan=self, pos=positions, idx=indexes)

            # Pre Operation Callback
            if(self.__preOperationCallback):
                self.__preOperationCallback(scan=self, pos=positions, idx=indexes)

            # Launch the counters
            self.__launchCounters(scan=self, pos=positions, idx=indexes)

            # Operation Callback
            if(self.__operationCallback):
                self.__operationCallback(scan=self, pos=positions, idx=indexes)

            # Save data to SCAN_DATA
            self.__saveCounterData(scan=self, pos=positions, idx=indexes)

            # Post Operation Callback
            if(self.__postOperationCallback):
                self.__postOperationCallback(scan=self, pos=positions, idx=indexes)

            self.__writeData(idx=pointIdx)

            # Updates the screen and plotter
            self.__printAndPlot()

            # Post Point Callback
            if(self.__postPointCallback):
                self.__postPointCallback(scan=self, pos=positions, idx=indexes)

            pointIdx += 1

            if self.__repeat != -1 and self.__repeat < pointIdx:
                break

        self.__terminate()

        # Post Scan Callback
        if(self.__postScanCallback):
            self.__postScanCallback(scan=self)

class ScanParam(object):
    def __init__(self, device):
        # if(not isinstance(device, IScannable)):
        #    raise Exception("Error: Only scannable devices can be used on
        #    scans. Please Check.")
        self.__device = device
        self.__points = []

    def __str__(self):
        pointsstr = "[" + str(self.getPoints()[0]) + "..." + str(self.getPoints()[-1]) + "]"
        r = "#Scan Param: device = " + str(self.__device) + " / Points: " + pointsstr + " >"
        return r

    def getDevice(self):
        return self.__device

    def setPoints(self, start, end=None, steps=None):
        if(end is None):
            self.__points = start
        else:
            if steps < 1:
                raise Exception("At least one point is needed to create scan points")
            diff = (float(end) - start) / (steps)
            self.__points = [diff * i + start for i in range(steps + 1)]

        # PseudoMotors dont have Low and High Limit values
        d = self.getDevice()
        p = self.getPoints()

        if(isinstance(d, PseudoMotor)):
            if(not d.canPerformMovement(min(p))[0]):
                err_msg = 'Error. The lower value exceeds the Low Limit Value'\
                          ' for this device. Device: {}'

                raise Exception(err_msg.format(str(d)))
            if(not d.canPerformMovement(max(p))[0]):
                err_msg = 'Error. The higher value exceeds the High Limit Value'\
                          ' for this device. Device: {}'

                raise Exception(err_msg.format(str(d)))
        else:
            ll = d.getLowLimitValue()
            hl = d.getHighLimitValue()

            if ll == 0.0 and hl == 0.0:
                return

            if(ll > min(p)):
                err_msg = 'Error. The lower value exceeds the Low Limit Value'\
                          ' for this device. Device: {}, Low Limit: {}'

                raise Exception(err_msg.format(str(d), str(ll)))

            if(hl < max(p)):
                err_msg = 'Error. The higher value exceeds the High Limit Value'\
                          ' for this device. Device: {}, High Limit: {}'

                raise Exception(err_msg.format(str(d), str(hl)))

    def getPoints(self):
        return self.__points

    def getNumberOfPoints(self):
        return len(self.__points)

#
#GLOBALS GETTERS AND SETTERS
#
def setPlotGraph(b):
    """
    Set the global variable PLOT_GRAPH to enable or disable the live plot

    Parameters
    ----------
    b : `bool`

    """
    global PLOT_GRAPH
    PLOT_GRAPH = b

def getPlotGraph():
    """
    Get the global variable PLOT_GRAPH value

    Returns
    ----------
    `bool`

    """
    global PLOT_GRAPH
    return PLOT_GRAPH

def setFitScan(b):
    """
    Set the global variable FIT_SCAN to enable or disable the scan fit at end

    Parameters
    ----------
    b : `bool`

    """
    global FIT_SCAN
    FIT_SCAN = b

def getFitScan():
    """
    Get the global variable FIT_SCAN to enable or disable the scan fit at end

    Returns
    ----------
    `bool`

    """
    global FIT_SCAN
    return FIT_SCAN


def setPrintScan(b):
    """
    Set the global variable PRINT_SCAN to enable or disable the scan print on
    terminal

    Parameters
    ----------
    b : `bool`

    """
    global PRINT_SCAN
    PRINT_SCAN = b

def getPrintScan():
    """
    Get the global variable PRINT_SCAN value

    Returns
    ----------
    `bool`

    """
    global PRINT_SCAN
    return PRINT_SCAN

def setPreScanCallback(c):
    """
    Set the pre scan callback.

    Parameters
    ----------
    c : `function`
        A function to be executed

        .. note::
            This function must receive an argument `**kwargs`

    Examples
    ----------
    >>> def myCallback(**kwargs):
    >>>     print("Print from my callback")
    >>>
    >>> setPreScanCallback(myCallback)
    >>>

    """
    global PRE_SCAN_CALLBACK
    if not callable(c):
        raise Exception('Error. Only functions can be used as callbacks.'\
                        'Please check.')
    PRE_SCAN_CALLBACK = c

def setPrePointCallback(c):
    """
    Set the pre point callback.

    Parameters
    ----------
    c : `function`
        A function to be executed

        .. note::
            This function must receive an argument `**kwargs`

    Examples
    ----------
    >>> def myCallback(**kwargs):
    >>>     print("Print from my callback")
    >>>
    >>> setPrePointCallback(myCallback)
    >>>

    """
    global PRE_POINT_CALLBACK
    if not callable(c):
        raise Exception('Error. Only functions can be used as callbacks. '\
                        'Please check.')
    PRE_POINT_CALLBACK = c

def setPreOperationCallback(c):
    """
    Set the pre operation callback.

    Parameters
    ----------
    c : `function`
        A function to be executed

        .. note::
            This function must receive an argument `**kwargs`

    Examples
    ----------
    >>> def myCallback(**kwargs):
    >>>     print("Print from my callback")
    >>>
    >>> setPreOperationCallback(myCallback)
    >>>

    """
    global PRE_OPERATION_CALLBACK
    if not callable(c):
        raise Exception('Error. Only functions can be used as callbacks. '\
                        'Please check.')
    PRE_OPERATION_CALLBACK = c

def setOperationCallback(c):
    """
    Set the operation callback.

    Parameters
    ----------
    c : `function`
        A function to be executed

        .. note::
            This function must receive an argument `**kwargs`

    Examples
    ----------
    >>> def myCallback(**kwargs):
    >>>     print("Print from my callback")
    >>>
    >>> setOperationCallback(myCallback)
    >>>

    """
    global OPERATION_CALLBACK
    if not callable(c):
        raise Exception('Error. Only functions can be used as callbacks. '\
                        'Please check.')
    OPERATION_CALLBACK = c

def setPostOperationCallback(c):
    """
    Set the post operation callback.

    Parameters
    ----------
    c : `function`
        A function to be executed

        .. note::
            This function must receive an argument `**kwargs`

    Examples
    ----------
    >>> def myCallback(**kwargs):
    >>>     print("Print from my callback")
    >>>
    >>> setPostOperationCallback(myCallback)
    >>>

    """
    global POST_OPERATION_CALLBACK
    if not callable(c):
        raise Exception('Error. Only functions can be used as callbacks. '\
                        'Please check.')
    POST_OPERATION_CALLBACK = c

def setPostPointCallback(c):
    """
    Set the post point callback.

    Parameters
    ----------
    c : `function`
        A function to be executed

        .. note::
            This function must receive an argument `**kwargs`

    Examples
    ----------
    >>> def myCallback(**kwargs):
    >>>     print("Print from my callback")
    >>>
    >>> setPostPointCallback(myCallback)
    >>>

    """
    global POST_POINT_CALLBACK
    if not callable(c):
        raise Exception('Error. Only functions can be used as callbacks. '\
                        'Please check.')
    POST_POINT_CALLBACK = c

def setPostScanCallback(c):
    """
    Set the post scan callback.

    Parameters
    ----------
    c : `function`
        A function to be executed

        .. note::
            This function must receive an argument `**kwargs`

    Examples
    ----------
    >>> def myCallback(**kwargs):
    >>>     print("Print from my callback")
    >>>
    >>> setPostScanCallback(myCallback)
    >>>

    """
    global POST_SCAN_CALLBACK
    if not callable(c):
        raise Exception('Error. Only functions can be used as callbacks. '\
                        'Please check.')
    POST_SCAN_CALLBACK = c

def getPreScanCallback(c):
    """
    Get the pre scan callback.

    Returns
    -------
    `function`
    """
    global PRE_SCAN_CALLBACK
    return PRE_SCAN_CALLBACK

def getPrePointCallback(c):
    """
    Get the pre point callback.

    Returns
    -------
    `function`
    """
    global PRE_POINT_CALLBACK
    return PRE_POINT_CALLBACK

def getPreOperationCallback(c):
    """
    Get the pre operation callback.

    Returns
    -------
    `function`
    """
    global PRE_OPERATION_CALLBACK
    return PRE_OPERATION_CALLBACK

def getOperationCallback(c):
    """
    Get the operation callback.

    Returns
    -------
    `function`
    """
    global OPERATION_CALLBACK
    return OPERATION_CALLBACK

def getPostOperationCallback(c):
    """
    Get the post operation callback.

    Returns
    -------
    `function`
    """
    global POST_OPERATION_CALLBACK
    return POST_OPERATION_CALLBACK

def getPostPointCallback(c):
    """
    Get the post point callback.

    Returns
    -------
    `function`
    """
    global POST_POINT_CALLBACK
    return POST_POINT_CALLBACK

def getPostScanCallback(c):
    """
    Get the post scan callback.

    Returns
    -------
    `function`
    """
    global POST_SCAN_CALLBACK
    return POST_SCAN_CALLBACK

def setFileWriter(writer):
    """
    Set the file writer to be used in order to save the data. If None is
    informed the **DefaultWriter** is used, generating a PyMCA-like file.

    Parameters
    ----------
    writer : `FileWriter`

    Examples
    ----------
    >>> writer = DefaultWriter("/tmp/test.txt")
    >>> setFileWrite(writer)
    """
    global FILE_WRITER

    if not isinstance(writer, FileWriter):
        raise Exception('Error. The parameter is not a valid File Writer. '\
                        'Please check.')

    FILE_WRITER = writer

def getFileWriter():
    """
    Get the current File Writer. See :class:`py4syn.writing.FileWriter`

    Returns
    -------
    `FileWriter`

    """
    global FILE_WRITER
    return FILE_WRITER

def setPartialWrite(partial):
    """
    Set enable or disable the Partial Write, if partial is set to **True** then
    the data written every iteration, otherwise data is only saved at the end.

    Parameters
    ----------
    partial : `bool`

    Examples
    ----------
    >>> setPartialWrite(True)

    """
    global PARTIAL_WRITE
    PARTIAL_WRITE = partial

def getPartialWrite():
    """
    Check if Partial write is enable.

    Returns
    -------
    `bool`

    """
    global PARTIAL_WRITE
    return PARTIAL_WRITE

def setOutput(out):
    """
    Set the Output, if output is set to **None** then the data is only stored
    in the SCAN_DATA dictionary.

    Parameters
    ----------
    out : `string`
        The complete filename.

        .. note::
            The files will be renamed to fit the format: filename_000N.ext.

            Each file represents one scan and they are automatically
            incremented.

    Examples
    ----------
    >>> setOutput("/home/user/teste.txt")

    """
    global FILENAME
    FILENAME = out

def getOutput():
    """
    Get the Output, if output is set to **None** then the data is only stored
    in the SCAN_DATA dictionary.

    Returns
    -------
    `string`
    """
    global FILENAME
    return FILENAME

def setX(x):
    """
    Set which field will be used to plot in the X axis

    Parameters
    ----------
    x : `string`
        Mneumonic of the data, e.g. "m1", "tth", "det", "mon"

    Examples
    ----------
    >>> setX("tth")

    """
    global XFIELD
    XFIELD = x

def setY(y):
    """
    Set which field will be used to plot in the Y axis

    Parameters
    ----------
    y : `string`
        Mneumonic of the data, e.g. "m1", "tth", "det", "mon"

    Examples
    ----------
    >>> setY("mon")

    """
    global YFIELD
    YFIELD = y

def getX():
    """
    Get which field will be used to plot in the X axis

    Returns
    -------
    `string`
    """
    global XFIELD
    return XFIELD

def getY():
    """
    Get which field will be used to plot in the X axis

    Returns
    -------
    `string`
    """
    global YFIELD
    return YFIELD

def getScanData():
    """
    Get the SCAN_DATA dictionary

    Returns
    -------
    `dictionary`
    """
    global SCAN_DATA
    return SCAN_DATA

def getFitValues():
    """
    Get the Fit values (Peak value, Peak Position, FWHM, FWHM Position and
    Center of Mass)

    Returns
    -------
    `list`
    """
    global PEAK
    global PEAK_AT
    global FWHM
    global FWHM_AT
    global COM

    return PEAK, PEAK_AT, FWHM, FWHM_AT, COM

def getPeak():
    """
    Get the Peak value of Fit

    Returns
    -------
    `double`
    """
    return PEAK

def getPeakAt():
    """
    Get the Peak position of Fit

    Returns
    -------
    `double`
    """
    return PEAK_AT

def getFwhm():
    """
    Get the FWHM value of Fit

    Returns
    -------
    `double`
    """
    return FWHM

def getFwhmAt():
    """
    Get the FWHM position of Fit

    Returns
    -------
    `double`
    """
    return FWHM_AT

def getMin():
    """
    Get the Min value of Fit

    Returns
    -------
    `double`
    """
    return MIN

def getMinAt():
    """
    Get the Min position of Fit

    Returns
    -------
    `double`
    """
    return FWHM_AT

def getCom():
    """
    Get the Center Of Mass of Fit (COM)

    Returns
    -------
    `double`
    """
    return COM

def getFittedData():
    """
    Get the best fit data.

    Returns
    -------
    `array`

    """
    return FITTED_DATA

def getFitResult():
    """
    Get the fit results.

    Returns
    -------
    `ModelFit`

    """
    return FIT_RESULT


def getScanCommand():
    """
    Get the last scan command executed

    Returns
    -------
    `string`
    """
    global SCAN_CMD
    return SCAN_CMD

def getUserDefinedDataFields():
    global USER_DATA_FIELDS
    return USER_DATA_FIELDS

def createUserDefinedDataField(field_name):
    """
    Create an user defined field in the SCAN_DATA dictionary

    Parameters
    ----------
    field_name : `string`
        Field name

    Examples
    ----------
    >>> createUserDefinedDataField("norm")

    """
    global USER_DATA_FIELDS
    USER_DATA_FIELDS.append(field_name)

def removeUserDefinedDataField(field_name):
    """
    Remove an user defined field in the SCAN_DATA dictionary

    Parameters
    ----------
    field_name : `string`
        Field name

    Examples
    ----------
    >>> removeUserDefinedDataField("norm")

    """
    global USER_DATA_FIELDS
    USER_DATA_FIELDS.remove(field_name)

def clearUserDefinedDataField():
    """
    Remove all user defined fields

    Examples
    ----------
    >>> clearUserDefinedDataField()

    """
    global USER_DATA_FIELDS
    USER_DATA_FIELDS = []

def setPlotDaemon(b):
    """
    Configure if the scan plot should or not be daemon

    Parameters
    ----------
    b : `bool`
        True of False indicating if should be daemon

    Examples
    ----------
    >>> setPlotDaemon(True)

    """
    global DAEMON_GRAPH
    DAEMON_GRAPH = b

def setScanComment(c):
    """
    Insert a custom comment in the scan file

    Parameters
    ----------
    c : `string`
        The comment to be inserted

    Examples
    ----------
    >>> setScanComment("Scan of sample X, using Y")

    """
    global SCAN_COMMENT
    SCAN_COMMENT = c

def getScanComment():
    """
    Get the custom comment

    Returns
    ----------
    `string`
        The comment to be inserted

    Examples
    ----------
    >>> print(getScanComment())

    """
    global SCAN_COMMENT
    return SCAN_COMMENT

def setScanPlotter(p):
    """
    Define the Plotter to be used in the scan

    Parameters
    ----------
    p : `Plotter`
        The plotter to be used

    Examples
    ----------
    >>> p = Plotter("My Plotter ", daemon=False)
    >>> setScanPlotter(p)

    """
    if isinstance(p, Plotter):
        global SCAN_PLOTTER
        SCAN_PLOTTER = p
    else:
        raise Exception('Error. Parameter is not a valid Plotter. '\
                        'Please check.')

def getScanPlotter():
    """
    Get the current plotter

    Returns
    ----------
    `Plotter`
        The current plotter

    Examples
    ----------
    >>> p = getScanPlotter()

    """
    global SCAN_PLOTTER
    return SCAN_PLOTTER

def setScanPlotterAxis(ax):
    """
    Define the axis index to be used when plotting

    Parameters
    ----------
    ax : `int`
        The axis index to be used when plotting

    Examples
    ----------
    >>> p = Plotter("My Plotter ", daemon=False)
    >>> p.createAxis("", label="Data label", xlabel="Energy", ylabel="I0",
    >>> grid=True, line_style="-", line_marker=".", line_color="blue")
    >>> setScanPlotter(p)
    >>> setScanPlotterAxis(1)

    """
    if ax > 0:
        global SCAN_PLOTTER_AXIS
        SCAN_PLOTTER_AXIS = ax
    else:
        raise Exception("Error. Invalid axis value index.")

def getScanPlotterAxis():
    """
    Get the current plotter axis

    Returns
    ----------
    `int`
        The current axis

    Examples
    ----------
    >>> p = getScanPlotterAxis()

    """
    global SCAN_PLOTTER_AXIS
    return SCAN_PLOTTER_AXIS

if __name__ == "__main__":
    #createMotor('m1', 'SOL:DMC1:m1')
    #createMotor('m2', 'SOL:DMC1:m2')

    #ummv(m1=0, m2=0)

    scalerSOL = Scaler("IMX:SCALER", 13, "scalerIMX")
    createCounter("seconds", scalerSOL, 1, factor=1e+7)
    createCounter("cyberstar", scalerSOL, 13, monitor=True)

    createUserDefinedDataField("myField")
    setX("m1")
    setY("cyberstar")
    setOutput("/home/ABTLUS/hugo.slepicka/testeHugo.txt")
    #scan('m1', 0, 1, 100, 0.01)
    timescan(1, 1)

    print("Scan Ended")
    print("Time elapsed: ", SCAN_DATA['scan_duration'])
