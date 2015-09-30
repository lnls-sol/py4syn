"""E5CK temperature controller class

Python class for Omron E5CK temperature controllers

:platform: Unix
:synopsis: Python class for Omron E5CK temperature controllers

.. moduleauthor:: Henrique Dante de Almeida <henrique.almeida@lnls.br>

"""
from epics import Device, ca
from numpy import array
from threading import Event

from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice

class OmronE5CK(StandardDevice, IScannable):
    """
    Class to control Omron E5CK temperature controllers via EPICS.

    Examples
    --------
    >>> from py4syn.epics.OmronE5CKClass import OmronE5CK
    >>> 
    >>> def showTemperature(pv='', name=''):
    ...     e5ck = OmronE5CK(pv, name)
    ...     print('Temperature is: %d' % e5ck.getValue())
    ...
    >>> def fastRaiseTemperature(e5ck, amount, rate=30):
    ...     e5ck.setRate(rate)
    ...     e5ck.setValue(e5ck.getValue() + amount)
    ...
    >>> def complexRamp(e5ck):
    ...     e5ck.setRate(10)
    ...     e5ck.setValue(200)
    ...     e5ck.wait()
    ...     e5ck.setRate(2)
    ...     e5ck.setValue(220)
    ...     e5ck.wait()
    ...     sleep(500)
    ...     e5ck.setRate(5)
    ...     e5ck.setValue(100)
    ...     e5ck.wait()
    ...     e5ck.stop()
    ...
    >>> import py4syn
    >>> from py4syn.epics.ScalerClass import Scaler
    >>> from py4syn.utils.counter import createCounter
    >>> from py4syn.utils.scan import scan
    >>> 
    >>> def temperatureScan(start, end, rate, pv='', counter='', channel=2):
    ...     e5ck = OmronE5CK(pv, 'e5ck')
    ...     py4syn.mtrDB['e5ck'] = e5ck
    ...     c = Scaler(counter, channel, 'simcountable')
    ...     createCounter('counter', c, channel)
    ...     e5ck.setRate(rate)
    ...     scan('e5ck', start, end, 10, 1)
    ...     e5ck.stop()
    ...
    """

    STATUS_IS_RUNNING = 1<<7
    PROGRAM_LENGTH = 4
    COMMAND_GET_STEP = '4010000'
    COMMAND_SET_TARGET = '5%02d%04d'
    TARGETS = (5, 8, 11, 14,)
    TIMES = (7, 10, 13, 16,)

    def __init__(self, pvName, mnemonic):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`

        Parameters
        ----------
        pvName : `string`
            Power supply base naming of the PV (Process Variable)
        mnemonic : `string`
            Temperature controller mnemonic
        """
        super().__init__(mnemonic)

        self.device = Device(pvName + ':', ['termopar', 'target', 'status', 'stepNum',
                             'programTable', 'programming', 'run', 'stop', 'advance',
                             'setPatternCount', 'timeScale', 'level1', 'reset', 'pause',
                             'sendCommand', 'pidtable', 'numPIDElements', 'paused', 'getP',
                             'getI', 'getD', 'power'])

        self.programmingDone = Event()
        self.newTemperature = Event()
        self.newStep = Event()
        self.device.add_callback('programming', self.onProgrammingChange)
        self.device.add_callback('termopar', self.onTemperatureChange)
        self.device.add_callback('stepNum', self.onStepChange)
        self.timeScaleCache = self.device.get('timeScale')

        self.pvName = pvName
        self.rate = 5
        self.presetDone = False

    def __str__(self):
        return '%s (%s)' % (self.getMnemonic(), self.pvName)

    def isRunning(self):
        """
        Returns true if the controller is in program mode. Whenever it is program mode,
        it is following a target temperature.

        Returns
        -------
        `bool`
        """
        v = self.device.get('status')
        r = not bool(int(v) & self.STATUS_IS_RUNNING)
        if not r:
            self.presetDone = False

        return r

    def isPaused(self):
        """
        Returns true if the controller is paused (keep temperature).

        Returns
        -------
        `bool`
        """
        paused = self.device.get('paused')

        return paused

    def getValue(self):
        """
        Returns the current measured temperature.

        Returns
        -------
        `float`
        """
        return self.device.get('termopar')

    def getTarget(self):
        """
        Returns the current target temperature. If the device is running, the target
        temperature is the temperature the device is changing to. If the device is not
        running, the target temperature is ignored.

        Returns
        -------
        `float`
        """
        return self.device.get('target')

    def getRealPosition(self):
        """
        Returns the same as :meth:`getValue`.

        See: :meth:`getValue`

        Returns
        -------
        `float`
        """
        return self.getValue()

    def getStepNumber(self):
        """
        Helper method to get the current program step.

        Returns
        -------
        `int`
        """
        return self.device.get('stepNum')

    def getLowLimitValue(self):
        """
        Returns the controller low limit temperature.

        Returns
        -------
        `float`
        """
        return 0.0

    def getHighLimitValue(self):
        """
        Returns the controller high limit temperature.

        Returns
        -------
        `float`
        """
        return 1300.0

    def onProgrammingChange(self, value, **kwargs):
        """
        Helper callback that tracks when the IOC finished programming the device.
        """
        self.presetDone = False
        if value == 0:
            self.programmingDone.set()

    def onStepChange(self, value, **kwargs):
        """
        Helper callback that indicates when a new program step has been reached
        """
        self.newStep.set()

    def onTemperatureChange(self, value, **kwargs):
        """
        Helper callback that indicates when the measured temperature has changed
        """
        self.newTemperature.set()

    def stop(self):
        """
        Stops executing the current temperature program and puts the device in idle
        state. In the idle state, the device will not try to set a target temperature.
        """
        self.device.put('stop', 1)
        self.presetDone = False

    def run(self):
        """
        Starts or resumes executing the current temperature program.
        """
        self.device.put('run', 1)

    def advance(self):
        """
        Helper method to skip the current program step and execute the next one.
        """
        self.device.put('advance', 1)

    def pause(self):
        """
        Pauses current ramp program. To resume program, use :meth:`run`

        See: :meth:`run`
        """
        self.device.put('pause', 1)

    def sendCommand(self, command):
        """
        Helper method to send a custom command to the controller.

        Parameters
        ----------
        command : `str`
            The command to be send
        """
        self.device.put('sendCommand', command.encode(), wait=True)

    def preset(self):
        """
        Makes the controler enter a well defined known state. This method creates and
        runs an "empty" ramp program. The program simply mantains the current
        temperature forever, whatever that temperature is. This is mostly a helper
        function, to allow making complex temperature ramps starting from a known
        state and reusing the preset values.

        .. note::
            Running a new program requires stopping the current program. While the
            program is stopped, the controller power generation drops to zero. Because
            of this power drop, this method may be slow to stabilize.
        """
        self.stop()
        current = self.getValue()

        # Steps 0 and 2 are fake steps, steps 1 and 3 are the real ones.
        # The fake steps are used for synchronizing with the device.
        program = [self.PROGRAM_LENGTH] + self.PROGRAM_LENGTH*[current, 99]
        self.programmingDone.clear()
        self.device.put('setPatternCount', 9999)
        self.device.put('programTable', array(program))
        ca.flush_io()
        self.programmingDone.wait(10)
        self.run()
        self.presetDone = True

    def program(self, programTable):
        """
        Set a programTable to the furnace
        """
        self.programmingDone.clear()
        self.device.put('programTable', array(programTable))
        ca.flush_io()
        self.programmingDone.wait(10)

    def setPIDTable(self, pidTable):
        """
        Set a PIDtable to the furnace
        """
        self.device.put('pidtable', array(pidTable))
    
    def getPIDTable(self):
        """
        Return the current PID table at the furnace

        Returns
        -------
        `array`
        """
        pidTablePV = self.device.PV('pidtable')
        
        return pidTablePV.get()

    def getP(self):
        """
        Return the current P value at the furnace

        Returns
        -------
        `double`
        """
        getPV = self.device.PV('getP')
        
        return getPV.get()

    def getI(self):
        """
        Return the current I value at the furnace

        Returns
        -------
        `double`
        """
        getPV = self.device.PV('getI')
        
        return getPV.get()

    def getD(self):
        """
        Return the current D value at the furnace

        Returns
        -------
        `double`
        """
        getPV = self.device.PV('getD')
        
        return getPV.get()

    def getPower(self):
        """
        Return the current Power value at the furnace

        Returns
        -------
        `double`
        """
        getPV = self.device.PV('power')
        
        return getPV.get()

    def getNumPIDElements(self):
        """
        Return the number of all parameters at a PID table
        
        Returns
        -------
        `int`
        """
        numPIDElementsPV = self.device.PV('numPIDElements')
        
        return numPIDElementsPV.get()

    def getTimeScale(self):
        """
        Returns the time scale being used by the controller. The timescale can either
        be zero, for hours:minutes, or one, for minutes:seconds.

        Returns
        -------
        `int`
        """
        t = self.device.PV('timeScale')
        v = t.get()
        t.get_ctrlvars()
        if t.severity == 0:
            self.timeScaleCache = v

        return self.timeScaleCache

    def setTimeScale(self, minutes):
        """
        Changes the time scale being used by the controller. The timescale can either
        be zero, for hours:minutes, or one, for minutes:seconds. This operation requires
        switching the controller operation mode to be successful, and then a reset is
        issued after it. The whole operation takes more than 5 seconds.

        Parameters
        ----------
        minutes : `int`
            Set to 1 for minutes:seconds, or 0 for hours:minutes
        """
        if minutes == self.getTimeScale() and self.device.PV('timeScale').severity == 0:
            return

        t = self.getValue()

        self.device.put('level1', 1)
        self.device.put('timeScale', minutes)
        self.device.put('reset', 1)

    def getStepNumberSync(self):
        """
        Helper module to retrieve an up-to-date value for the current program step
        number. Similar to :meth:`getStepNumber`, but it doesn't rely on monitor value
        and instead does a synchronous caget() call.

        See: :meth:`getStepNumber`

        Returns
        -------
        `int`
        """
        self.device.put('stepNum.PROC', 0, wait=True)
        v = self.device.PV('stepNum').get(use_monitor=False)
        return int(v)

    def synchronizeStep(self, current):
        """
        Helper method to set up a constant temperature right before running a ramp
        program. This method detects if a current ramp program is running or not. If
        it's not, then it doesn't do anything. If there is a ramp running, then it
        configures and advances to a "synchronization step", that is, a step where
        the temperature does not change. This step marks the beginning of the new
        ramp.

        The method returns the resulting step number

        Parameters
        ----------
        current : `float`
            The temperature target for the synchronization step

        Returns
        -------
        `int`
        """

        # This method uses the advance() call to skip steps. Suprisingly, advancing
        # steps with E5CK is not trivial. The reason for this is that E5CK quickly
        # acknowledges the advance command, but delays to actually advance. Ignoring
        # this deficiency results in other commands issued later doing the wrong thing.
        # In particular, calling advance again later may silently fail. We work around
        # this by using a synchronous call to get the current step number and a busy
        # wait to check when the step was really changed.
        #
        # To make things worse, some component in EPICS seems to break serialization by
        # not respecting the order which PVs are updated, so it's not possible to
        # change the program using two separate PVs, like, for example, stepNumConfig
        # setStepTarget, which are implemented in E5CK's IOC. Because of that, a custom
        # PV was added in the IOC to support arbitrary commands sent in a serialized
        # way. This sendCommand procedure is what this method uses.
        step = self.getStepNumberSync()
        while step % 2 == 1:
            target = self.TARGETS[(step+1)%self.PROGRAM_LENGTH]
            self.sendCommand(self.COMMAND_SET_TARGET % (target, current))
            self.advance()

            # E5CK is slow, so loop until it changes state. This is required: calling
            # advance twice in a row doesn't work. A state transition must happen first.
            old = step
            while old == step:
                step = self.getStepNumberSync()
        assert step % 2 == 0

        return step

    def timeToValue(self, t):
        """
        Helper method to convert between minutes to the format used by the controller.

        Parameters
        ----------
        t : `float`
            The desired time, in minutes

        Returns
        -------
        `float`
        """
        if self.getTimeScale() == 0:
            minutes = int(t)%60
            hours = int(t)//60
            value = 100*hours + minutes

            if hours > 99:
                raise OverflowError('Ramp time is too large: %g' % rampTime)
        else:
            minutes = int(t)

            if minutes > 99:
                raise OverflowError('Ramp time is too large with current settings: %g' %
                                    t)

            seconds = min(round((t-minutes)*60), 59)
            value = 100*minutes + seconds

        return value

    def setRate(self, r):
        """
        Sets the ramp speed in degrees per minutes for use with :meth:`setValue`. This
        method does not send a command to the controller, it only stores the rate for
        the next ramps.

        See: :meth:`setValue`

        Parameters
        ----------
        r : `float`
            Ramp speed in °C/min
        """
        self.rate = r

    def setValue(self, v):
        """
        Changes the temperature to a new value. This method calls preset if it has not
        already been called first. The speed that the new temperature is reached is set
        with :meth:`setRate`. The default rate is 5 °C/minute.

        See: :meth:`setRate`

        Parameters
        ----------
        v : `float`
            The target temperature in °C
        """

        # This method depends on a program preset being loaded and the program being
        # in a synchronization step. Given the two precondition, this method simply
        # programs a ramp, a synchronization step after the ramp and advances to the
        # ramp step.
        if not self.presetDone:
            self.preset()

        # We accept float as input, but the controller is integer only
        v = round(v)

        current = self.getValue()
        minutes = abs(v-current)/self.rate
        time = self.timeToValue(minutes)

        step = self.synchronizeStep(current)
        self.waitStep = (step+2)%self.PROGRAM_LENGTH
        x = self.TARGETS[step+1]
        y = self.TIMES[step+1]
        z = self.TARGETS[self.waitStep]
        self.sendCommand(self.COMMAND_SET_TARGET % (x, v))
        self.sendCommand(self.COMMAND_SET_TARGET % (y, time))
        self.sendCommand(self.COMMAND_SET_TARGET % (z, v))
        self.advance()
        self.valueTarget = v

    def wait(self):
        """
        Blocks until the requested temperature is achieved.
        """
        if not self.presetDone:
            return

        # Waiting is done in two steps. First step waits until the program reaches
        # the next synchronization step. Second step waits util the measured temperature
        # reaches the requested temperature
        self.newStep.clear()
        while self.getStepNumber() != self.waitStep:
            ca.flush_io()
            self.newStep.wait(60)
            self.newStep.clear()

        self.newTemperature.clear()
        while self.getValue() != self.valueTarget:
            ca.flush_io()

            # Safety timeout, temperature didn't change after a long time
            if not self.newTemperature.wait(120):
                return

            self.newTemperature.clear()
