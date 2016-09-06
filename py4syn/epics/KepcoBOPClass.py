"""Kepco BOP power supply class

Python class for Kepco BOP GL power supplies

:platform: Unix
:synopsis: Python class for Kepco BOP GL power supplies

.. moduleauthor:: Henrique Dante de Almeida <henrique.almeida@lnls.br>

"""
from epics import PV, Device
from epics.ca import poll
from numpy import array
from py4syn.epics.IScannable import IScannable
from py4syn.epics.StandardDevice import StandardDevice
from time import monotonic

class KepcoBOP(IScannable, StandardDevice):
    """
    Class to control Kepco BOP GL power supplies via EPICS.

    Examples
    --------
    >>> from py4syn.epics.KepcoBOPClass import KepcoBOP
    >>>    
    >>> def configurePower(pv="", name="", voltage=5.0, currentLimit=1.0):
    ...    bop = KepcoBOP(pv, name)
    ...    bop.reset()
    ...    bop.setCurrentLimits(currentLimit, currentLimit)
    ...    bop.setVoltage(voltage)
    ...    return bop
    ...
    >>> def smoothVoltageTransition(bop, initial=0.0, final=12.0, duration=2.0):
    ...    bop.setRampWaveform(duration, final-initial, (initial+final)/2)
    ...    bop.waveformStart()
    ...    bop.waveformWait()
    ...
    >>> def noiseCurrent(bop):
    ...    bop.reset()
    ...    bop.setMode(KepcoBOP.MODE_CURRENT)
    ...    bop.setVoltageLimits(20, 20)
    ...    points = [random.uniform(-5, 5) for i in range(100)]
    ...    bop.clearWaveform()
    ...    bop.addWaveformPoints(points, [0.025])
    ...    bop.waveformStart()
    ...
    """

    MODE_VOLTAGE = 'VOLTAGE'
    MODE_CURRENT = 'CURRENT'
    MAX_POINTS_SINGLE_DWELL = 5900
    MAX_POINTS_FEW_DWELLS = 3933
    MAX_POINTS_MANY_DWELLS = 2950
    FEW_DWELLS_THRESHOLD = 126
    MAX_POINTS_PER_ADD = 21
    WAVEFORM_RUNNING_FLAG = 16384
    MAX_VOLTAGE = 50
    MAX_CURRENT = 20
    MIN_DWELL = 0.000093
    MAX_DWELL = 0.034

    RANGE = ['GET', 'GET.PROC', 'SET', 'SET:LIMIT:POSITIVE', 'SET:LIMIT:NEGATIVE',
             'SET:PROTECTION:POSITIVE', 'SET:PROTECTION:NEGATIVE', 'GET:LIMIT:POSITIVE',
             'GET:LIMIT:POSITIVE.PROC', 'GET:LIMIT:NEGATIVE', 'GET:LIMIT:NEGATIVE.PROC',
             'GET:PROTECTION:POSITIVE', 'GET:PROTECTION:POSITIVE.PROC',
             'GET:PROTECTION:NEGATIVE', 'GET:PROTECTION:NEGATIVE.PROC']

    PROGRAM = ['WAVEFORM:TYPE', 'WAVEFORM:PERIOD', 'WAVEFORM:AMPLITUDE',
               'WAVEFORM:OFFSET', 'REPEAT', 'CLEAR', 'MARK:REPEAT']

    PROGRAM_SUB = ['ADD', 'WAVEFORM:ADD:2ARGUMENTS', 'WAVEFORM:ADD:3ARGUMENTS',
                   'WAVEFORM:SET:ANGLE', 'WAVEFORM:START:ANGLE', 'WAVEFORM:STOP:ANGLE',
                   'START', 'STOP', 'ABORT', 'POINTS', 'POINTS.PROC']

    WAVEFORM_PARAM1_LIMITS = {
            'SQUARE': (0.02, 1000),
            'RAMP+': (0.02, 532),
            'RAMP-': (0.02, 532),
            'SINE': (0.01, 443),
            'LEVEL': (0.0005, 5),
    }

    def __init__(self, pvName, mnemonic):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`
        
        Parameters
        ----------
        pvName : `string`
            Power supply base naming of the PV (Process Variable)
        mnemonic : `string`
            Power supply mnemonic
        """

        super().__init__(mnemonic)

        self.pvName = pvName
        self.voltage = Device(pvName + ':VOLTAGE:', self.RANGE)
        self.current = Device(pvName + ':CURRENT:', self.RANGE)
        self.program = Device(pvName + ':PROGRAM:', self.PROGRAM)
        self.programVoltage = Device(pvName + ':PROGRAM:VOLTAGE:', self.PROGRAM_SUB)
        self.programCurrent = Device(pvName + ':PROGRAM:CURRENT:', self.PROGRAM_SUB)
        self.resetPV = PV(pvName + ':RESET')
        self.mode = Device(pvName + ':MODE:', ['SET', 'GET', 'GET.PROC'])
        self.operationFlag = Device(pvName + ':',
                                    ['GET:OPERATION:FLAG', 'GET:OPERATION:FLAG.PROC'])
        self.timePV = PV(pvName + ':PROGRAM:TIME:ADD')
        self.error = Device(pvName + ':', ['ERROR', 'ERROR.PROC', 'ERROR:TEXT'])

        self.defaults()

        # Operation mode (voltage x current) is cached, so get it immediatelly
        self.procAndGet(self.mode, 'GET')        

    def procAndGet(self, device, pv):
        """
        Helper method to synchronously execute a query in the device.
        """
        device.put(pv + '.PROC', 0, wait=True)
        return device.PV(pv).get(use_monitor=False)

    def getError(self):
        """
        Helper method to pop the last error from the device error queue.
        """
        error = self.procAndGet(self.error, 'ERROR')
        text = self.error.PV('ERROR:TEXT').get(use_monitor=False)
        return error, text

    def checkError(self):
        """
        Helper method to raise an exception if the device reports an error.
        """
        error, text = self.getError()
        if error != 0:
            raise RuntimeError('Device returned error: %d, %s' % (error, text))

    def defaults(self):
        """
        Helper method to reset internal data.
        """
        self.programPoints = 0
        self.programTimes = []
        self.blockStopCommand = False
        self.oneShotTime = 0

    def setVoltage(self, voltage, wait=True):
        """
        Sets the voltage value. This method can only be used when in voltage mode.
        The voltage values must be within the power supply acceptable range and
        also within the configured limit values.

        See also: :meth:`setMode`, :meth:`setVoltageLimits`

        Parameters
        ----------
        voltage : `float`
            The desired voltage value
        """
        if self.cachedMode() != self.MODE_VOLTAGE:
            raise RuntimeError('Not in voltage mode')

        if abs(voltage) > self.MAX_VOLTAGE*1.01:
            raise ValueError('Voltage out of range: %g' % voltage)

        self.voltage.put('SET', voltage, wait)

    def setCurrent(self, current, wait=True):
        """
        Sets the current value. This method can only be used when in current mode.
        The current values must be within the power supply acceptable range and
        also within the configured limit values.

        See also: :meth:`setMode`, :meth:`setCurrentLimits`
        
        Parameters
        ----------
        current : `float`
            The desired current value
        """
        if self.cachedMode() != self.MODE_CURRENT:
            raise RuntimeError('Not in current mode')

        if abs(current) > self.MAX_CURRENT*1.01:
            raise ValueError('Current out of range: %g' % current)

        self.current.put('SET', current, wait)

    def getVoltage(self):
        """
        Measures the voltage value. The measured value that is read back is known
        to have an error (less than 1%) and a delay (up to 320ms).

        Returns
        -------
        `float`
        """
        return self.procAndGet(self.voltage, 'GET')

    def getCurrent(self):
        """
        Measures the current value. The measured value that is read back is known
        to have an error (less than 1%) and a delay (up to 320ms).

        Returns
        -------
        `float`
        """
        return self.procAndGet(self.current, 'GET')

    def setMode(self, mode):
        """
        Changes the operating mode. Supported modes are voltage mode and current mode.
        In the voltage mode, the device tries to set a specific voltage, while staying
        within the current protection limits. In current mode, the device tries to set
        a specific current, while staying within the voltage protection limits.
        See also: :meth:`setCurrentLimits`, :meth:`setVoltageLimits`

        Parameters
        ----------
        mode : {KepcoBOP.MODE_CURRENT, KepcoBOP.MODE_VOLTAGE}
            The desired mode
        """
        self.mode.put('SET', mode, wait=True)
        # GET is used as the cached mode, so it needs to be updated too
        self.procAndGet(self.mode, 'GET')

    def cachedMode(self):
        """
        Helper method to return cached operating mode
        """
        return self.MODE_VOLTAGE if self.mode.get('GET') == 0 else self.MODE_CURRENT

    def setLimits(self, device, mode, negative=None, positive=None, maximum=1e100):
        """
        Helper method that implements :meth:`setVoltageLimits` and
        :meth:`setCurrentLimits`
        """
        pv = 'LIMIT' if self.cachedMode() == mode else 'PROTECTION'

        if negative is not None and negative < 0:
                raise ValueError('Value must be absolute: %g' % negative)

            if negative > maximum:
                raise ValueError('Value out of range: %g (max: %g)' % (negative, maximum))

            device.put('SET:%s:NEGATIVE' % pv, negative, wait=True)
        if positive is not None and positive < 0:
                raise ValueError('Value must be absolute: %g' % positive)

            if positive > maximum:
                raise ValueError('Value out of range: %g (max: %g)' % (positive, maximum))

            device.put('SET:%s:POSITIVE' % pv, positive, wait=True)

    def setVoltageLimits(self, negative=None, positive=None):
        """
        Sets the negative and positive voltage limits allowed for operation. The specific
        limit type that is set depends on the operating mode. When in voltage mode,
        the limit set is a main channel limit: it defines the limits of the voltages that
        can be programmed by the user. When in current mode, the limit is a protection
        limit: it defines the voltage limits that the load may impose because of the
        requested current. When changing the operating modes, the set limits no longer
        apply: they must be set again for the new mode.

        See also: :meth:`setMode`

        Parameters
        ----------
        negative : `float`
            The absolute value of the negative limit
        positive : `float`
            The absolute value of the positive limit
        """
        self.setLimits(self.voltage, self.MODE_VOLTAGE, negative, positive,
                       self.MAX_VOLTAGE)

    def setCurrentLimits(self, negative=None, positive=None):
        """
        Sets the negative and positive current limits allowed for operation. The specific
        limit type that is set depends on the operating mode. When in current mode,
        the limit set is a main channel limit: it defines the limits of the current that
        can be programmed by the user. When in voltage mode, the limit is a protection
        limit: it defines the current limits that the load may impose because of the
        requested voltage. When changing the operating modes, the set limits no longer
        apply: they must be set again for the new mode.

        See also: :meth:`setMode`

        Parameters
        ----------
        negative : `float`
            The absolute value of the negative limit
        positive : `float`
            The absolute value of the positive limit
        """
        self.setLimits(self.current, self.MODE_CURRENT, negative, positive,
                       self.MAX_CURRENT)

    def getLimits(self, device, mode):
        """
        Helper method that implements :meth:`getVoltageLimits` and :meth:
        `getCurrentLimits`
        """
        pv = 'LIMIT' if self.cachedMode() == mode else 'PROTECTION'

        negative = self.procAndGet(device, 'GET:%s:NEGATIVE' % pv)
        positive = self.procAndGet(device, 'GET:%s:POSITIVE' % pv)

        return negative, positive

    def getVoltageLimits(self):
        """
        Gets the negative and positive voltage limits allowed for operation. The specific
        limit type that is read depends on the operating mode. When in voltage mode,
        the limit set is a main channel limit: it defines the limits of the voltages that
        can be programmed by the user. When in current mode, the limit is a protection
        limit: it defines the voltage limits that the load may impose because of the
        requested current. When changing the operating modes, the set limits no longer
        apply: they are different for the new mode.

        See also: :meth:`setMode`

        Returns
        -------
        negative : `float`
            The absolute value of the negative limit
        positive : `float`
            The absolute value of the positive limit
        """
        return self.getLimits(self.voltage, self.MODE_VOLTAGE)

    def getCurrentLimits(self):
        """
        Gets the negative and positive current limits allowed for operation. The specific
        limit type that is read depends on the operating mode. When in current mode,
        the limit set is a main channel limit: it defines the limits of the current that
        can be programmed by the user. When in voltage mode, the limit is a protection
        limit: it defines the current limits that the load may impose because of the
        requested voltage. When changing the operating modes, the set limits no longer
        apply: they are different for the new mode.

        See also: :meth:`setMode`

        Returns
        -------
        negative : `float`
            The absolute value of the negative limit
        positive : `float`
            The absolute value of the positive limit
        """
        return self.getLimits(self.current, self.MODE_CURRENT)

    def reset(self):
        """
        Resets the device to a known state. Possible reset states may vary with the
        device configuration, but generally will be a zero value output (either voltage
        or current) with low protection limits. The device error queue will be cleared.
        """
        self.resetPV.put(0, wait=True)
        self.defaults()
        self.procAndGet(self.mode, 'GET')

    def clearWaveform(self):
        """
        Clears the programmed waveform data. This is required when building a new
        waveform program. Waveform data can only be cleared while the program is
        not running.
        """
        self.program.put('CLEAR', 0, wait=True)
        self.checkError()
        self.defaults()

    def getProgramLength(self):
        """
        Helper method that returns the number of points in current waveform program.
        """
        if self.cachedMode() == self.MODE_VOLTAGE:
            device = self.programVoltage
        else:
            device = self.programCurrent

        p = self.procAndGet(device, 'POINTS')
        self.checkError()
        return p

    def addWaveformPoints(self, points, times):
        """
        Adds a set of points to the waveform program. This is one of the ways that the
        device can be programmed to generate a complex waveform. It's the most flexible
        way, allowing arbitrary waveforms, but it's also the slowest one (a 10 second
        waveform may take at least 4 seconds just to upload the program). This method
        adds more points to the current waveform program. It does not overwrite the
        existing program.
        
        Adding points does not execute the program. The method :meth:`waveformStart` must
        be called.

        See also: :meth:`setWaveformPoints`, :meth:`addSineWaveform`,
        :meth:`addTriangleWaveform`, :meth:`addRampWaveform`, :meth:`addSquareWaveform`,
        :meth:`addLevelWaveform`, :meth:`waveformStart`

        .. note::
            When changing operating mode, the waveform program must be cleared if
            necessary, because the device will prohibit mixing points from different
            modes.

        Parameters
        ----------
        points : `array of floats`
            The array of points to be added to the program. The total number of allowed
            points may vary, depending on the times array. When the times array has
            exactly one element, the maximum number of points is 5900. When the
            times array has at most 126 distinct values, the maximum number of points
            is 3933. When the times array has more than 126 distinct values, the
            maximum number of points is 2950.
        times : `array of floats`
            The dwell times for each point. Either there must be one time entry for
            each point, or the array of times must contain exactly one element, which
            sets the time for all points. The allowed time range is [93e-6, 34e-3]
            (93µs to 34ms).
        """
        x = min(times)
        if x < self.MIN_DWELL:
            raise ValueError('Minimum time out of range: %g (min: %g)' %
                             (x, self.MIN_DWELL))

        x = max(times)
        if x > self.MAX_DWELL:
            raise ValueError('Maximum time out of range: %g (max: %g)' %
                             (x, self.MAX_DWELL))

        p = self.programPoints + len(points)
        t = self.programTimes + times
        distinct = len(set(t))

        if distinct > self.FEW_DWELLS_THRESHOLD:
            maxPoints = self.MAX_POINTS_MANY_DWELLS
        elif distinct > 1:
            maxPoints = self.MAX_POINTS_FEW_DWELLS
        else:
            maxPoints = self.MAX_POINTS_SINGLE_DWELL

        if p > maxPoints:
            raise ValueError('Requested waveform too large: %u (maximum is: %u)' %
                             (p, maxPoints))

        if self.cachedMode() == self.MODE_VOLTAGE:
            device = self.programVoltage
        else:
            device = self.programCurrent

        for i in range(0, len(points), self.MAX_POINTS_PER_ADD):
            l = array(points[i:i+self.MAX_POINTS_PER_ADD])
            device.put('ADD', l, wait=True)

        for i in range(0, len(times), self.MAX_POINTS_PER_ADD):
            l = array(times[i:i+self.MAX_POINTS_PER_ADD])
            self.timePV.put(l, wait=True)

        self.programPoints = p
        self.programTimes = t

    def setWaveformPoints(self, points, times):
        """
        A shortcut to clearing the waveform program, adding waveform points and setting
        the repeat count to 1.

        See also: :meth:`clearWaveform`, :meth:`addWaveformPoints`,
        :meth:`setWaveformRepeat`

        Parameters
        ----------
        points : `array of floats`
            Parameter passed to :meth:`addWaveformPoints`
        times : `array of floats`
            Parameter passed to :meth:`addWaveformPoints`
        """
        self.clearWaveform()
        self.addWaveformPoints(points, times)
        self.setWaveformRepeat(1)
        self.checkError()

    def setWaveformAngle(self, start=0, stop=360):
        """
        Helper method that configures start and stop angles for sine and triangle
        waveforms.
        """
        if start < 0 or start > 359.99:
            raise ValueError('Start angle must be between 0 and 359.99')

        if stop < 0.01 or stop > 360:
            raise ValueError('Stop angle must be between 0.01 and 360')

        if self.cachedMode() == self.MODE_VOLTAGE:
            device = self.programVoltage
        else:
            device = self.programCurrent

        if device.get('WAVEFORM:START:ANGLE') != start:
            device.put('WAVEFORM:START:ANGLE', start, wait=True)

        if device.get('WAVEFORM:STOP:ANGLE') != stop:
            device.put('WAVEFORM:STOP:ANGLE', stop, wait=True)

        device.put('WAVEFORM:SET:ANGLE', 0, wait=True)
        self.checkError()

    def addWaveform(self, type, param1, param2, param3=None):
        """
        Helper method that implements adding waveform segments.
        """
        if type not in self.WAVEFORM_PARAM1_LIMITS:
            raise ValueError('Invalid waveform type: %s' % type)

        x, y = self.WAVEFORM_PARAM1_LIMITS[type]
        if param1 < x or param1 > y:
            raise ValueError('Frequency or period parameter out of range: %g '
                             '(interval: [%g, %g])' % (param1, x, y))

        if self.cachedMode() == self.MODE_VOLTAGE:
            device = self.programVoltage
            maxValue = self.MAX_VOLTAGE
        else:
            device = self.programCurrent
            maxValue = self.MAX_CURRENT

        if param2 < 0 or param2 > 2*maxValue:
            raise ValueError('Amplitude out of range: %g (range: [%g, %g])' %
                             (param2, 0, 2*maxValue))

        if param3 is not None and abs(param3) > maxValue:
            raise ValueError('Offset out of range: %g (range: [%g, %g])' %
                             (param3, -maxValue, maxValue))

        self.program.put('WAVEFORM:TYPE', type, wait=True)
        self.program.put('WAVEFORM:PERIODORFREQUENCY', param1, wait=True)
        self.program.put('WAVEFORM:AMPLITUDE', param2, wait=True)

        if param3 is not None:
            self.program.put('WAVEFORM:OFFSET', param3, wait=True)
            device.put('WAVEFORM:ADD:3ARGUMENTS', 0, wait=True)
        else:
            device.put('WAVEFORM:ADD:2ARGUMENTS', 0, wait=True)

        self.checkError()
        l = self.getProgramLength()
        self.programPoints = l
        # Fake distinct dwell time for waveform
        self.programTimes += [0]

    def addSineWaveform(self, frequency, amplitude, offset, start=0, stop=360):
        """
        Adds a sine wave to the waveform program. This is one of the ways that the
        device can be programmed to generate a complex waveform. The other way is
        sending the complete array of points for the waveform. This method is limited
        to a specific waveform type and it also consumes a lot of points, but it's
        faster to program than uploading individual points. When the final desired
        waveform can be composed of simple waveform segments, this is the best way
        to program the device.

        Adding points does not execute the program. The method :meth:`waveformStart` must
        be called.

        See also: :meth:`waveformStart`, :meth:`setSineWaveform`,
        :meth:`addWaveformPoints`, :meth:`addTriangleWaveform`, :meth:`addRampWaveform`,
        :meth:`addSquareWaveform`, :meth:`addLevelWaveform`

        .. note::
            When changing operating mode, the waveform program must be cleared if
            necessary, because the device will prohibit mixing points from different
            modes.

        Parameters
        ----------
        frequency : `float`
            The sine wave frequency. The allowed range is 0.01Hz to 443Hz. The number
            of points used vary from 3840, for lower frequency waves to 24, for
            higher frequency waves.
        amplitude : `float`
            The sine wave peak to peak amplitude. The peak to peak amplitude cannot
            exceed the range defined by the configured operating device limits.
        offset : `float`
            The offset of the sine wave zero amplitude. The offset cannot exceed the
            configured device limits.
        start : `float`
            The starting angle for the sine wave, in degrees. Allowed range is
            [0.0, 359.99]
        stop : `float`
            The stop angle for the sine wave, in degrees. Allowed range is [0.01, 360.0]
        """
        self.setWaveformAngle(start, stop)
        self.addWaveform('SINE', frequency, amplitude, offset)

    def setSineWaveform(self, frequency, amplitude, offset, start=0, stop=360):
        """
        A shortcut to clearing the waveform program, adding sine waveform and setting
        the repeat count to 1.

        See also: :meth:`clearWaveform`, :meth:`addSineWaveform`,
        :meth:`setWaveformRepeat`

        Parameters
        ----------
        frequency : `float`
            Parameter passed to :meth:`addSineWaveform`
        amplitude : `float`
            Parameter passed to :meth:`addSineWaveform`
        offset : `float`
            Parameter passed to :meth:`addSineWaveform`
        start : `float`
            Parameter passed to :meth:`addSineWaveform`
        stop : `float`
            Parameter passed to :meth:`addSineWaveform`
        """
        self.clearWaveform()
        self.addSineWaveform(frequency, amplitude, offset, start, stop)
        self.setWaveformRepeat(1)

    def addTriangleWaveform(self, frequency, amplitude, offset, start=0, stop=360):
        """
        Adds a triangle wave to the waveform program. This is one of the ways that the
        device can be programmed to generate a complex waveform. The other way is
        sending the complete array of points for the waveform. This method is limited
        to a specific waveform type and it also consumes a lot of points, but it's
        faster to program than uploading individual points. When the final desired
        waveform can be composed of simple waveform segments, this is the best way
        to program the device.

        Adding points does not execute the program. The method :meth:`waveformStart` must
        be called.

        See also: :meth:`waveformStart`, :meth:`setTriangleWaveform`,
        :meth:`addWaveformPoints`, :meth:`addSineWaveform`, :meth:`addRampWaveform`,
        :meth:`addSquareWaveform`, :meth:`addLevelWaveform`

        .. note::
            When changing operating mode, the waveform program must be cleared if
            necessary, because the device will prohibit mixing points from different
            modes.

        Parameters
        ----------
        frequency : `float`
            The triangle wave frequency. The allowed range is 0.01Hz to 443Hz. The number
            of points used vary from 3840, for lower frequency waves to 24, for
            higher frequency waves.
        amplitude : `float`
            The triangle wave peak to peak amplitude. The peak to peak amplitude cannot
            exceed the range defined by the configured operating device limits.
        offset : `float`
            The offset of the triangle wave zero amplitude. The offset cannot exceed the
            configured device limits.
        start : `float`
            The starting angle for the triangle wave, in degrees. Allowed range is
            [0.0, 359.99]
        stop : `float`
            The stop angle for the triangle wave, in degrees. Allowed range is
            [0.01, 360.0]
        """
        self.setWaveformAngle(start, stop)
        self.addWaveform('TRIANGLE', frequency, amplitude, offset)

    def setTriangleWaveform(self, frequency, amplitude, offset, start=0, stop=360):
        """
        A shortcut to clearing the waveform program, adding triangle waveform and setting
        the repeat count to 1.

        See :meth:`clearWaveform`, :meth:`addTriangleWaveform`, :meth:`setWaveformRepeat`

        Parameters
        ----------
        frequency : `float`
            Parameter passed to :meth:`addTriangleWaveform`
        amplitude : `float`
            Parameter passed to :meth:`addTriangleWaveform`
        offset : `float`
            Parameter passed to :meth:`addTriangleWaveform`
        start : `float`
            Parameter passed to :meth:`addTriangleWaveform`
        stop : `float`
            Parameter passed to :meth:`addTriangleWaveform`
        """
        self.clearWaveform()
        self.addTriangleWaveform(frequency, amplitude, offset, start, stop)
        self.setWaveformRepeat(1)

    def addRampWaveform(self, length, height, offset):
        """
        Adds a ramp wave to the waveform program. This is one of the ways that the
        device can be programmed to generate a complex waveform. The other way is
        sending the complete array of points for the waveform. This method is limited
        to a specific waveform type and it also consumes a lot of points, but it's
        faster to program than uploading individual points. When the final desired
        waveform can be composed of simple waveform segments, this is the best way
        to program the device.

        Adding points does not execute the program. The method :meth:`waveformStart` must
        be called.

        See also: :meth:`waveformStart`, :meth:`setRampWaveform`,
        :meth:`addWaveformPoints`, :meth:`addSineWaveform`, :meth:`addTriangleWaveform`,
        :meth:`addSquareWaveform`, :meth:`addLevelWaveform`

        .. note::
            When changing operating mode, the waveform program must be cleared if
            necessary, because the device will prohibit mixing points from different
            modes.

        Parameters
        ----------
        length : `float`
            The ramp length. The allowed range is [1/532, 100] (1.88ms to 100s).
            The number of points used vary from 20, for smaller ramps, to 3840, for
            larger ramps.
        height : `float`
            The ramp height. The height can be positive or negative. It cannot
            exceed the range defined by the configured operating device limits.
        offset : `float`
            The offset of the ramp middle height. The offset cannot exceed the
            configured device limits.
        """
        if height >= 0:
            type = 'RAMP+'
        else:
            type = 'RAMP-'
            height = -height

        self.addWaveform(type, 1.0/length, height, offset)

    def setRampWaveform(self, length, height, offset):
        """
        A shortcut to clearing the waveform program, adding ramp waveform and setting
        the repeat count to 1.

        See also: :meth:`clearWaveform`, :meth:`addRampWaveform`,
        :meth:`setWaveformRepeat`

        Parameters
        ----------
        length : `float`
            Parameter passed to :meth:`addRampWaveform`
        height : `float`
            Parameter passed to :meth:`addRampWaveform`
        offset : `float`
            Parameter passed to :meth:`addRampWaveform`
        """
        self.clearWaveform()
        self.addRampWaveform(length, height, offset)
        self.setWaveformRepeat(1)

    def addSquareWaveform(self, frequency, amplitude, offset):
        """
        Adds a square wave (constant 50% duty cycle, starts with positive excursion)
        to the waveform program. This is one of the ways that the device can be
        programmed to generate a complex waveform. The other way is sending the complete
        array of points for the waveform. This method is limited to a specific waveform
        type and it also consumes a lot of points, but it's faster to program than
        uploading individual points. When the final desired waveform can be composed
        of simple waveform segments, this is the best way to program the device.

        Adding points does not execute the program. The method :meth:`waveformStart` must
        be called.

        See also: :meth:`waveformStart`, :meth:`setSquareWaveform`,
        :meth:`addWaveformPoints`, :meth:`addSineWaveform`, :meth:`addTriangleWaveform`,
        :meth:`addRampWaveform`, :meth:`addLevelWaveform`

        .. note::
            When changing operating mode, the waveform program must be cleared if
            necessary, because the device will prohibit mixing points from different
            modes.

        Parameters
        ----------
        frequency : `float`
            The square wave frequency. The allowed range is 0.02Hz to 1000Hz. The number
            of points used vary from 3840, for lower frequency waves to 10, for
            higher frequency waves.
        amplitude : `float`
            The square wave peak to peak amplitude. The peak to peak amplitude cannot
            exceed the range defined by the configured operating device limits.
        offset : `float`
            The offset of the square wave zero amplitude. The offset cannot exceed the
            configured device limits.
        """
        self.addWaveform('SQUARE', frequency, amplitude, offset)

    def setSquareWaveform(self, frequency, amplitude, offset):
        """
        A shortcut to clearing the waveform program, adding square waveform and setting
        the repeat count to 1.

        See also: :meth:`clearWaveform`, :meth:`addSquareWaveform`, :meth:`setWaveformRepeat`

        Parameters
        ----------
        frequency : `float`
            Parameter passed to :meth:`addSquareWaveform`
        amplitude : `float`
            Parameter passed to :meth:`addSquareWaveform`
        offset : `float`
            Parameter passed to :meth:`addSquareWaveform`
        """
        self.clearWaveform()
        self.addSquareWaveform(frequency, amplitude, offset)
        self.setWaveformRepeat(1)

    def addLevelWaveform(self, length, offset):
        """
        Adds a fixed level wave to the waveform program. This is one of the ways that the
        device can be programmed to generate a complex waveform. The other way is
        sending the complete array of points for the waveform. This method is limited
        to a specific waveform type, but it's faster to program than uploading
        individual points. When the final desired waveform can be composed of simple
        waveform segments, this is the best way to program the device.

        Adding points does not execute the program. The method :meth:`waveformStart` must
        be called.

        See also: :meth:`waveformStart`, :meth:`setLevelWaveform`,
        :meth:`addWaveformPoints`, :meth:`addSineWaveform`, :meth:`addRampWaveform`,
        :meth:`addTriangleWaveform`, :meth:`addSquareWaveform`

        .. note::
            When changing operating mode, the waveform program must be cleared if
            necessary, because the device will prohibit mixing points from different
            modes.

        Parameters
        ----------
        length : `float`
            The duration of the level waveform. The allowed range is 500µs to 5s. The
            number of points used is 60.
        offset : `float`
            The level offset. The offset cannot exceed the configured device limits.
        """
        self.addWaveform('LEVEL', length, offset)

    def setLevelWaveform(self, length, offset):
        """
        A shortcut to clearing the waveform program, adding a level waveform and setting
        the repeat count to 1.

        See also: :meth:`clearWaveform`, :meth:`addLevelWaveform`,
        :meth:`setWaveformRepeat`

        Parameters
        ----------
        length : `float`
            Parameter passed to :meth:`addLevelWaveform`
        offset : `float`
            Parameter passed to :meth:`addLevelWaveform`
        """
        self.clearWaveform()
        self.addLevelWaveform(length, offset)
        self.setWaveformRepeat(1)

    def setWaveformRepeat(self, repeat):
        """
        Set the number of times the waveform program will run. By default, the program
        runs an indeterminate number of times, until it's explicitly stopped. This method
        is used to specify the number of times the waveform program will repeat.

        A waveform may also have separate one-shot part and repeatable part. Use the
        method :meth:`setWaveformRepeatMark` to separate them.

        See also: :meth:`setWaveformRepeatMark`, :meth:`waveformStop`,
        :meth:`waveformAbort`

        Parameters
        ----------
        repeat : `int`
            Number of times the programmed waveform will run. A value of zero means
            run until explicitly stopped.
        """
        if repeat < 0:
            raise ValueError('Negative repeat value: %d' % repeat)

        self.program.put('REPEAT', repeat, wait=True)
        self.checkError()
        
        # It's not reliable to call waveformStop with a finite repeat count
        # because calling immediatelly after the waveform program stops results
        # in an error and there's no atomic way to check and disable it,
        # so we just disallow using the stop command with finite repeat counts
        self.blockStopCommand = repeat > 0

    def getWaveformRepeat(self):
        """
        Gets the last requested waveform repeat count.

        See also: :meth:`setWaveformRepeat`

        Returns
        -------
        `int`
        """
        return self.program.get('REPEAT')

    def setWaveformRepeatMark(self, position=None):
        """
        Separates the one-short part from the repeating part in the waveform program. By
        default, the whole waveform repeats, according to the repeat count. This method
        marks the separation point that allows the definition of an initial one-shot
        part of the wave. The part before the marked point will be the one-shot part
        and after the marked point will be the repeating part.

        See also: :meth:`setWaveformRepeat`

        Parameters
        ----------
        position : `int`
            Desired position of the setWaveformRepeatMark, representing the point in
            the waveform that starts the repeating part. If unset, the current first
            free position in the waveform is set as the mark.
        """
        if position is None:
            position = self.getProgramLength()
        elif position < 0:
            raise ValueError('Negative position: %d' % position)

        self.program.put('MARK:REPEAT', position, wait=True)
        self.checkError()

    def waveformStart(self):
        """
        Executes a waveform program. The program must be already defined by using the
        waveform add methods. This methods triggers the execution and returns
        immediatelly. It does not wait for the complete waveform execution to finish.
        
        By default, the waveform will repeat until it is explicitly stopped, but this
        can be configured by the :meth:`setWaveformRepeat` method. To stop the
        waveform execution, the methods :meth:`waveformStop` and
        :meth:`waveformAbort` can be used. For a program with finite repeat count,
        it's possible to wait until the waveform finishes with :meth:`waveformWait`.

        See also: :meth:`addWaveformPoints`, :meth:`addSineWaveform`,
        :meth:`addTriangleWaveform`, :meth:`addRampWaveform`, :meth:`addSquareWaveform`,
        :meth:`addLevelWaveform`, :meth:`waveformStop`, :meth:`waveformAbort`,
        :meth:`waveformWait`, :meth:`isWaveformRunning`
        """
        if self.cachedMode() == self.MODE_VOLTAGE:
            self.programVoltage.put('START', 0, wait=True)
        else:
            self.programCurrent.put('START', 0, wait=True)

        self.checkError()

    def waveformStop(self):
        """
        Requests to stop a running waveform. The waveform will execute until the end
        and then will stop, without repeating the program again. The final output value
        will be the final point in the program.

        See also: :meth:`waveformAbort`, :meth:`waveformWait`

        .. note::
            Because it's not possible to reliably stop a program with finite repeat
            count without potentially triggering an "already finished" error, this
            command is only enabled for stopping waveform programs with inifinite
            repeat count. For finite repeat counts, use :meth:`waveformAbort`, or
            :meth:`waveformWait` instead.
        """
        if self.blockStopCommand:
            raise RuntimeError('Cannot use stop command with finite repeat counts')

        if self.cachedMode() == self.MODE_VOLTAGE:
            self.programVoltage.put('STOP', 0, wait=True)
        else:
            self.programCurrent.put('STOP', 0, wait=True)

        self.checkError()

    def waveformAbort(self):
        """
        Immediatelly stops a running waveform. The final output value will be the value
        before running the waveform program.

        See also: :meth:`waveformStop`, :meth:`waveformWait`
        """
        if self.cachedMode() == self.MODE_VOLTAGE:
            self.programVoltage.put('ABORT', 0, wait=True)
        else:
            self.programCurrent.put('ABORT', 0, wait=True)

        self.checkError()

    def getOperationFlag(self):
        """
        Returns the real time value of the device operation condition register.
        The register contains a set of bits representing the following flags:
        "list running" (16384), "list complete" (4096), "sample complete" (2048),
        "constant current mode" (1024), "transient complete" (512)", "constant voltage
        mode" (256), "transient armed" (64), "waiting for trigger" (32). Refer to the
        Kepco BOP GL manual for specific details. The relevant flag used by the library
        is the "list running" flag, which indicates that theres a waveform program
        running.

        See also: :meth:`isWaveformRunning`, :meth:`waveformWait`

        Returns
        -------
            `int`
        """
        return self.procAndGet(self.operationFlag, 'GET:OPERATION:FLAG')

    def isWaveformRunning(self):
        """
        Returns whether there's a running waveform program.

        See also: :meth:`getOperationFlag`, :meth:`waveformWait`
        
        Returns
        -------
            `bool`
        """
        return bool(self.getOperationFlag() & self.WAVEFORM_RUNNING_FLAG)

    def waveformWait(self):
        """
        Waits until the whole waveform program finishes, including all repetitions.
        It's only possible to wait for waveform programs with finite repeat counts.

        .. note::
            When using the Kepco power supply with a serial port, it's not possible to
            receive a notification from the device when the waveform finishes, so this
            method works by repeatedly polling the device requesting the operation flag.
            Because of this, the recommended way to use this method is first sleeping
            for as much time as possible to avoid the loop and only on the last second
            call this method. Example of a helper function that accomplishes this:
            
            Examples
            --------
            >>> def runAndWait(bop, totalTime):
            ...     bop.waveformStart()
            ...     sleep(max(totalTime-1, 0))
            ...     bop.waveformWait()
            ...
        """
        while self.isWaveformRunning():
            poll(1e-2)

    def getValue(self):
        """
        Returns either the readback voltage or the current, depending on operating mode.

        Returns
        -------
            `float`
        """
        if self.cachedMode() == self.MODE_VOLTAGE:
            return self.getVoltage()

        return self.getCurrent()

    def setValue(self, v, wait=True):
        """
        Sets either the current voltage or current, depending on operating mode.

        Parameters
        ----------
        v : `float`
            Either voltage, or current to set, depending on operating mode.
        """
        if self.cachedMode() == self.MODE_VOLTAGE:
            self.setVoltage(v, wait)
        else:
            self.setCurrent(v, wait)

    def wait(self):
        """
        Does the same as :meth:`waveformWait`.
        """
        self.waveformWait()

    def getLowLimitValue(self):
        """
        Gets either the voltage or current low limit value, depending on operation mode.

        Returns
        -------
            `float`
        """
        if self.cachedMode() == self.MODE_VOLTAGE:
            return -self.getLimits(self.voltage, self.MODE_VOLTAGE)[0]

        return -self.getLimits(self.current, self.MODE_CURRENT)[0]

    def getHighLimitValue(self):
        """
        Gets either the voltage or current high limit value, depending on operation mode.

        Returns
        -------
            `float`
        """

        if self.cachedMode() == self.MODE_VOLTAGE:
            return self.getLimits(self.voltage, self.MODE_VOLTAGE)[1]

        return self.getLimits(self.current, self.MODE_CURRENT)[1]
