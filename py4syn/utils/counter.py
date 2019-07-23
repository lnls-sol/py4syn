import py4syn
from py4syn.epics.ICountable import ICountable
from py4syn.epics.ScalerClass import Scaler
import collections

def findMonitor():
    for k, v in py4syn.counterDB.items():
        if v['monitor'] and v['enable']:
            return k, v

    return None, None

def createCounter(mnemonic, device, channel=None, monitor=False, factor=1, write=True): 
    """
    Add a countable to the counterDB dictionary

    Parameters
    ----------
    mnemonic : `string`
        Mnemonic of the counter
    device : `ICountable`
        The device that handles this counter and implements ICountable interface
    channel : `int`
        Specify where usable the channel index for this counter
    monitor : `bool`
        If monitor is set to True the process will be by counts and not by time
    factor : `int`
        Specify the factor to be used when reading the counter value

    Examples
    ----------

    >>> scaler = Scaler("SOL:SCALER", 10, "scaler1") # Creates an EPICS Scaler
    >>> scalerSIM = SimCountable("ANY:PV:HERE", "simMnemonic")
    >>> createCounter("seconds", scaler, 1, factor=1e+7) # Create a channel using the real 
    >>>                                                  # scaler, channel number 1 and a factor.
    >>> createCounter("det", scaler, 3)
    >>> createCounter("mon", scaler, 10, monitor=True) # Create a channel that will act as a monitor
    >>> createCounter("cyberSim", scalerSIM, 2)
    >>> ct(10000) # Start a count process until 10000 counts in the monitor 
    >>>           # and show the results for each channel at the end.
    >>> counts = ctr(2, use_monitor=False) # Start a count process with 2 seconds  
    >>>                                    # of integration time. Returns the counts as a map.
    >>> print("Counts on det: ", counts['det'])
    """ 
    try:
        if(not isinstance(device, ICountable)):
            raise Exception("The device is not a ICountable. Please check!")

        if(mnemonic in py4syn.counterDB):
            raise Exception("Mnemonic already in use at counterDB. Please check!")

        mne, pars = findMonitor()
        if(monitor and mne is not None):
            raise Exception("There is already one monitor at counterDB. Monitor mnemonic is: "+str(mne)+". Please check.")

        if(monitor and not device.canMonitor()):
            raise Exception("The device cannot be used as a monitor. Please check.")

        counterData = {}
        counterData['device'] = device
        counterData['channel'] = channel
        counterData['monitor'] = monitor
        counterData['factor'] = factor
        counterData['enable'] = True
        counterData['write'] = write
        py4syn.counterDB[mnemonic] = counterData

    except Exception as e:
        print("\tError: ",e)

def waitAll(monitor=False):
    if(monitor):
        k, v = findMonitor()
        dev = v['device']
        dev.wait()
    else:
        for k, v in py4syn.counterDB.items():
            v = py4syn.counterDB[k]
            if v['enable']:
                dev = v['device']
                dev.wait()

def stopAll():
    for k, v in py4syn.counterDB.items():
        dev = v['device']
        dev.stopCount()

def startCounters(use_monitor=False):
    for k, v in py4syn.counterDB.items():
        dev = v['device']
        if not dev.isCounting() and v['enable']:
            if(use_monitor and not dev.canStopCount()):
                continue
            dev.startCount()

def printCountersValue(data):
    print("-"*32)
    print("Counts:")
    print("-"*32)
    for m, v in data.items():
        if(isinstance(v, collections.Iterable)):
            print("{0:>10} {1:>20}".format(m, v.sum()))
        else:
            print("{0:>10} {1:>20}".format(m, int(v)))
    print("-"*32)

def ctr(t=1, use_monitor=False, wait=True):
    from epics import ca
    k, v = findMonitor()
    if(k is not None and use_monitor):
        # We have a monitor, so we start the monitor, wait until it finishes, stop all other counters and grab count values
        v['device'].setPresetValue(v['channel'], t)

        for kT, vT in py4syn.counterDB.items():
            dev = vT['device']
            if(dev == v['device']):
                continue
            if not dev.isCounting() and dev.canStopCount() and v['enable']:
                dev.setCountTime(ICountable.INFINITY_TIME)

        startCounters(use_monitor=True)
        ca.poll()
        if(wait):
            waitAll(monitor=True)
            stopAll()
            return getCountersData()
    else:
        for k, v in py4syn.counterDB.items():
            dev = v['device']
            if not dev.isCounting() and v['enable']:
                dev.setCountTime(t)

        startCounters()

        ca.poll()
        if(wait):
            waitAll()
            return getCountersData()

def getCountersData():
    data = collections.OrderedDict()
    for k, v in py4syn.counterDB.items():
        if (v['enable'] == True):
            dev = v['device']
            cnt = 0
            if(v['channel'] is not None):
                cnt = dev.getValue(channel=v['channel'])
            else:
                cnt = dev.getValue()

            data[k] = cnt/(v['factor']*1.0)

    return data


def ct(t=1, use_monitor=False):
    """
    Count all counters available using the given time

    Parameters
    ----------
    t : `double`
        Time of Preset to be used
    use_monitor : `bool`
        If monitor is set to True the process will be by counts and not by time

    """
    data = ctr(t, use_monitor)
    printCountersValue(data)


def getActiveCountersNumber():
    """
    Count all counters available using the given time

    Returns
    ----------
    `int`
        The number of enabled counters in counterDB

    """

    cnt = 0
    for k, v in py4syn.counterDB.items():
        v = py4syn.counterDB[k]
        if v['enable']:
            cnt += 1
    return cnt

def disableCounter(mne):
    """
    Disable an specific counter

    Parameters
    ----------
    mne : `string`
        The counter mnemonic

    """

    if(mne not in py4syn.counterDB):
        raise Exception("Counter "+mne+" not found in counterDB. Please check!")
    c = py4syn.counterDB[mne]
    c['enable'] = False

def enableCounter(mne):
    """
    Enable an specific counter

    Parameters
    ----------
    mne : `string`
        The counter mnemonic

    """

    if(mne not in py4syn.counterDB):
        raise Exception("Counter "+mne+" not found in counterDB. Please check!")
    c = py4syn.counterDB[mne]
    c['enable'] = True

def clearCounterDB():
    py4syn.counterDB = collections.OrderedDict()

if __name__ == "__main__":
    scalerSIM = Scaler("IMX:SCALER", 13, "scalerSIM")
    createCounter("seconds", scalerSIM, 1)
    createCounter("cyberstar", scalerSIM, 13, monitor=True)

    ct(1)
    disableCounter("seconds")
    disableCounter("mon")
    ct(10000, use_monitor=True)

    #timescan(0.1, delay=0.1)
    '''

    import datetime

    countTime = 1

    s = datetime.datetime.now()
    ct(countTime)
    e = datetime.datetime.now()

    print("Elapsed Time: ", e-s)

    #scaler.setCountTime(1)
    #scaler.setCountStart()
    #scaler.wait()
    #print("S1 = ", scaler.getIntensity(1))
    #print("S10 = ", scaler.getIntensity(10))
    '''
