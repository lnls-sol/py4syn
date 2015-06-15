"""Keithley6514 Class

Python Class for EPICS Keithley control.

:platform: Unix
:synopsis: Python Class for EPICS Keithley control.

.. moduleauthor:: Diego Henrique Dorta <diego.dorta@lnls.br>
    .. note:: 18/08/2014 [diego.dorta]  first version released
"""
from epics import Device, ca, PV
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable

class Keithley6514(StandardDevice, ICountable):
    """

    Python class to help configuration and control the Keithley 6514 Electrometer.

    Keithley is an electrical instrument for measuring electric charge or electrical potential difference.
    This instrument is capable of measuring extremely low currents. E.g.: pico (10e-12), i.e.: 0,000 000 000 001.

    For more information, please, refer to: `Model 6514 System Electrometer Instruction Manual <http://www.tunl.duke.edu/documents/public/electronics/Keithley/keithley-6514-electrometer-manual.pdf>`_
    """
    
    def onStatusChange(self, value, **kw):
        self._counting = (value == 1)
    
    def __init__(self, pvName, mnemonic, timeBased=False):
        """
        **Constructor**
        To use this Keithley Class you must pass the PV (Process Variable) prefix.

            .. Note::
                e.g.: SXS:K6514

        Examples
        --------

        >>> from KeithleyClass import *
        >>> name = Keithley('SOL:K6514', 'k1')

        """
        StandardDevice.__init__(self, mnemonic)
        self.pvName = pvName
        self.timeBased = timeBased
        self.keithley = Device(pvName+':', 
                               ('GetMed','SetMed','GetMedRank','SetMedRank','GetAver',
                                'SetAver','GetAverCoun','SetAverCoun','GetNPLC','SetNPLC',
                                'GetAutoZero', 'SetAutoZero','GetZeroCheck','SetZeroCheck',
                                'GetAverTCon','SetAverTCon','GetCurrRange','SetCurrRange',
                                'GetZeroCor','SetZeroCor', 'GetAutoCurrRange','SetAutoCurrRange'
                                'Count','ContinuesMode', 'CNT', 'OneMeasure'))

        self.pvMeasure = PV(pvName+':'+'Measure', auto_monitor=False)
        self._counting = self.isCountingPV()
        self.keithley.add_callback('CNT', self.onStatusChange)

    def isCountingPV(self):
        return (self.keithley.get('CNT') == 1)

    def isCounting(self):
        return self._counting

    def wait(self):
        while(self.isCounting()):
            ca.poll(0.00001)

    def getTriggerReading(self):            
        """
        Trigger and return reading(s).

        Returns
        -------
        Value: Float, e.g.: -6.0173430000000003e-16.

        Examples
        --------
        >>> name.getTriggerReading()
        >>> -1.0221850000000001e-15
        """
        return self.pvMeasure.get(use_monitor=False)
        #return self.keithley.get('Measure')
    
    def getCountNumberReading(self):            
        """
        Count the number of reading(s).

        Returns
        -------
        Value: Integer, e.g.: 963.

        Examples
        --------
        >>> name.CountNumberReading()
        >>> 161.0
        """

        return self.keithley.get('Count')

    def getStatusContinuesMode(self):            
        """
        Get the status of Continues Mode (enable/disable).
        Default: enable.

        Returns
        -------
        Value: Boolean, i.e.: 0 - False (Off/Disable), 1 - True (On/Enable).

        Examples
        --------
        >>> name.getStatusContinuesMode()
        >>> True
        """

        return bool(self.keithley.get('ContinuesMode'))

    def setStatusContinuesMode(self, cmode):
        """
        Set enable/disable to continues mode. Let this enable if you want a continuing measuring.

        Parameters
        ----------
        Value: Boolean, i.e.: 0 - False (Off/Disable), 1 - True (On/Enable).

        Examples
        --------
        >>> name.setStatusContinuesMode(0)
        """

        if(cmode != 0 and cmode != 1):
            raise ValueError('Invalid number - It should be 0 or 1') 
        self.keithley.put('ContinuesMode', cmode)

    def getAutoZeroing(self):
        """
        Get the status of Auto Zero (enable/disable).
        Default: enable.

        Returns
        -------
        Value: Boolean, i.e.: 0 - False (Off/Disable), 1 - True (On/Enable).

        Examples
        --------
        >>> name.getAutoZeroing()
        >>> True
        """

        return bool(self.keithley.get('GetAutoZero'))

    def setAutoZeroing(self, autozero):    
        """
        Set enable/disable for Auto Zero.

        Parameters
        ----------
        Value: Boolean, i.e.: 0 - False (Off/Disable), 1 - True (On/Enable).

        Examples
        --------
        >>> name.setAutoZeroing(1)
        """

        if(autozero != 0 and autozero != 1):
            raise ValueError('Invalid number - It should be 0 or 1') 
        self.keithley.put('SetAutoZero', autozero)

    def getMedianFilter(self):
        """
        Get the status of Median Filter (enable/disable).
        Default: enable.

        Returns
        -------
        Value: Boolean, i.e.: 0 - False (Off/Disable), 1 - True (On/Enable).

        Examples
        --------
        >>> name.getMedianFilter()
        >>> True
        """

        return bool(self.keithley.get('GetMed'))

    def setMedianFilter(self, med):
        """
        Set enable/disable for Median Filter.

        Parameters
        ----------
        Value: Boolean, i.e.: 0 - False (Off/Disable), 1 - True (On/Enable).

        Examples
        --------
        >>> name.setMedianFilter(1)
        """

        if(med != 0 and med != 1):
            raise ValueError('Invalid number - It should be 0 or 1') 
        self.keithley.put('SetMed', med)

    def getMedianRank(self):
        """
        Get the value of Median Rank, this number of sample readings are between 1 to 5.
        Default: 5.

        Returns
        -------
        Value: Integer, i.e.: 1 to 5.

        Examples
        --------
        >>> name.getMedianRank()
        >>> 5.0
        """

        return self.keithley.get('GetMedRank')

    def setMedianRank(self, medrank): 
        """
        Set the number of sample readings used for the median calculation.

        Parameters
        ----------
        Value: Integer, i.e.: 1 to 5.

        Examples
        --------
        >>> name.setMedianRank(3)
        """

        if (medrank < 1 or medrank > 5):
            raise ValueError('Invalid number - It should be 1 to 5') 
        self.keithley.put('SetMedRank', medrank)

    def getAverageDigitalFilter(self):
        """
        Get the status of Digital Filter (enable/disable).
        Default: enable.

        Returns
        -------
        Value: Boolean, i.e.: 0 - False (Off/Disable), 1 - True (On/Enable).

        Examples
        --------
        >>> name.getAverageDigitalFilter()
        >>> True
        """

        return bool(self.keithley.get('GetAver'))

    def setAverageDigitalFilter(self, aver):
        """
        Set enable/disable for Digital Filter.

        Parameters
        ----------
        Value: Boolean, i.e.: 0 - False (Off/Disable), 1 - True (On/Enable).

        Examples
        --------
        >>> name.setAverageDigitalFilter(1)
        """

        if(aver != 0 and aver != 1):
            raise ValueError('Invalid number - It should be 0 or 1') 
        self.keithley.put('SetAver', aver)

    def getAverageCount(self): 
        """
        Get the number of filter count.
        Default: 10.

        Returns
        -------
        Value: Integer, i.e.: 2 to 100.

        Examples
        --------
        >>> name.getAverageCount()
        >>> 10.0
        """

        return self.keithley.get('GetAverCoun')

    def setAverageCount(self, avercoun):
        """
        Set the number of filter count.

        Parameters
        ----------
        Value: Integer, i.e.: 2 to 100.

        Examples
        --------
        >>> name.setAverageCount(80)
        """

        if (avercoun < 2 or avercoun > 100):
            raise ValueError('Invalid number - It should be 2 to 100') 
        self.keithley.put('SetAverCoun', avercoun)

    def getIntegrationTime(self):
        """
        Get the number of integration rate.
        Default: 1.

        Returns
        -------
        Value: Float, i.e.: 0.01 to 10 (PLCs). Where 1 PLC for 60Hz is 16.67msec (1/60).

        Examples
        --------
        >>> name.getIntegrationTime()
        >>> 1.0
        """
        return self.keithley.get('GetNPLC')

    def setIntegrationTime(self, nplc):
        """
        Set the number of integration rate.

        Parameters
        ----------
        Value: Float, i.e.: 0.01 to 10 (PLCs). Where 1 PLC for 60Hz is 16.67msec (1/60).

        Examples
        --------
        >>> name.setIntegrationTime(0.01)
        """

        if (nplc < 0.01 or nplc > 10):
            raise ValueError('Invalid number - It should be 0.01 to 10') 
        self.keithley.put('SetNPLC', nplc)

    def getAverageTControl(self):
        """
        Get the filter control.
        Default: REP.

        Returns
        -------
        Value: String, i.e.: REP or MOV.

        Examples
        --------
        >>> name.getAverageTControl()
        >>> 'REP'
        """

        return self.keithley.get('GetAverTCon')

    def setAverageTControl(self, tcon):
        """
        Set the filter control.

        Parameters
        ----------
        Value: String, i.e.: 'REP' or 'MOV', where REP means 'Repeat' and MOV means 'Moving'.

        Examples
        --------
        >>> name.setAverageTControl('MOV')
        """

        if (tcon != 'REP' and tcon != 'MOV'):
            raise ValueError('Invalid name - It should be REP or MOV') 
        self.keithley.put('SetAverTCon', bytes(tcon, 'ascii'))

    def getZeroCheck(self):
        """
        Get the status of Zero Check (enable/disable).
        Default: disable.

        Returns
        -------
        Value: Boolean, i.e.: 0 - False (Off/Disable), 1 - True (On/Enable).

        Examples
        --------
        >>> name.getZeroCheck()
        >>> False
        """

        return bool(self.keithley.get('GetZeroCheck'))

    def setZeroCheck(self, check):
        """
        Set enable/disable for Zero Check.

        Parameters
        ----------
        Value: Boolean, i.e.: 0 - False (Off/Disable), 1 - True (On/Enable).

        Returns
        -------
        One value (1).

        Examples
        --------
        >>> name.setZeroCheck(1)
        >>> 1
        """

        if(check != 0 and check != 1):
            raise ValueError('Invalid number - It should be 0 or 1') 
        return self.keithley.put('SetZeroCheck', check)

    def getZeroCorrect(self):
        """
        Get the status of Zero Correct (enable/disable).
        Default: disable.

        Returns
        -------
        Value: Boolean, i.e.: 0 - False (Off/Disable), 1 - True (On/Enable).
    
        Examples
        --------
        >>> name.getZeroCorrect()
        >>> False
        """

        return bool(self.keithley.get('GetZeroCor'))

    def setZeroCorrect(self, cor):
        """
        Set enable/disable for Zero Correct.

        Parameters
        ----------
        Value: Boolean, i.e.: 0 - False (Off/Disable), 1 - True (On/Enable).

        Returns
        -------
        One value (1).

        Examples
        --------
        >>> name.setZeroCorrect(1)
        >>> 1
        """

        if(cor != 0 and cor != 1):
            raise ValueError('Invalid number - It should be 0 or 1') 
        return self.keithley.put('SetZeroCor', cor)

    def getAutoCurrentRange(self):
        """
        Get the status of Auto Current Range (enable/disable).
        Default: enable.

        Returns
        -------
        Value: Boolean, i.e.: 0 - False (Off/Disable), 1 - True (On/Enable).

        Examples
        --------
        >>> name.getAutoCurrentRange()
        >>> True
        """

        return bool(self.keithley.get('GetAutoCurrRange'))

    def setAutoCurrentRange(self, autorange):
        """
        Set enable/disable for Auto Current Range.

        Parameters
        ----------
        Value: Boolean, i.e.: 0 - False (Off/Disable), 1 - True (On/Enable).

        Returns
        -------
        One value (1).

        Examples
        --------
        >>> name.setAutoCurrentRange(1)
        >>> 1
        """

        if(autorange != 0 and autorange != 1):
            raise ValueError('Invalid number - It should be 0 or 1') 
        return self.keithley.put('SetAutoCurrRange', autorange)

    def getCurrentRange(self):
        """
        Get the value of range.
        Default: Auto range.

        Returns
        -------
        Value: Integer, i.e.: 
        0 (Undefined ZERO), 1 (Indefined UM), 2 (20 mA), 3 (2 mA), 4 (200 uA), 5 (20 uA), 6 (2 uA), 7 (200 nA), 8 (20 nA), 9 (2 nA), 10 (200 pA), 11 (20 pA).
    
        Examples
        --------
        >>> name.getCurrentRange()
        >>> 11
        """

        return self.keithley.get('GetCurrRange')

    def setCurrentRange(self, curange):
        """
        Set the range.

        Parameters
        ----------
        Value: Integer, i.e.: 
        0 (Undefined ZERO), 1 (Indefined UM), 2 (20 mA), 3 (2 mA), 4 (200 uA), 5 (20 uA), 6 (2 uA), 7 (200 nA), 8 (20 nA), 9 (2 nA), 10 (200 pA), 11 (20 pA).

        Examples
        --------
        >>> name.setCurrentRange(5)
        """
        if (curange < 0 or curange > 11):
            raise ValueError('Invalid number - It should be 0 to 11') 
        self.keithley.put('SetCurrRange', curange)

    def getValue(self, **kwargs):
        """
        Get the current value of a countable device.

        Parameters
        ----------
        kwargs : value
            Where needed informations can be passed, e.g. select which channel must be read.

        Returns
        -------
        out : value
            Returns the current value of the device. Type of the value depends on device settings.
        """
        return self.getTriggerReading()

    def setCountTime(self, time):
        """
        Method to set the count time of a Keithley device.

        .. note::
            Whenever the median filter is active, changing the count time results in
            the filter being reset, so the first measurement will take additional
            time to collect new data for the filter. The extra time is proportional
            to the median filter rank. After the first measurement, the following
            measurements will have the correct integration time.
        .. note:: Unlike scalers, the count time is only an approximation. The
            requested integration time will be split into multiple parts, which includes
            the analog integration time (varying between approximatelly 10ms to 50ms),
            the digital integration time (that averages a set of 2 to 100 analog
            integrations), and other operations unrelated to integration, like auto zero
            calibration (triples the integration time) and calculation times. When
            calling this method, the digital average filter will be activated if it's
            not already and the filter type will be set to repeat.

        See also: :meth:`setIntegrationTime`, :meth:`setAverageCount`

        Parameters
        ----------
        time : value
            The target count time to be set. The allowed time range is 100ms to 15s
            (limited by software).

        Returns
        -------
        out : None
        """
        if(not self.timeBased):
            return
        
        if time < 0.1 or time > 15:
            raise ValueError('Invalid integration time: %g' % time)

        # Keithley timing model:
        # ----------------------
        #
        # Keithley fundamental delay is the analog integration delay, which is the
        # time it takes to measure the current using the measurement hardware.
        # The integration delay can be configured to values in the range between
        # 166,7µs to 166,7ms (or 200µs to 200ms in 50Hz electricity grids).
        # On top of the analog integration delay, two delays are significant:
        # the digital filter delay, which works as a digital integrator (when configured
        # in "repeating" mode) and the auto zero setting, which performs continuous
        # device recalibration. The digital filter works by taking multiple analog
        # measurements, then averaging the result, so it multiplies the delay by the
        # repeat count. The auto zero setting always triples the integration time.
        # So, the basic initial timing model for the Keithley device is the following:
        #
        #       (1) time = Azero*Rcount*Atime
        #
        # Where time is the final count time, Azero is 2,97 when auto zero is enabled,
        # or 0,95 when auto zero is disabled, Rcount is the digital average repeat count and
        # Atime is the analog integration time. For example, with auto zero enabled,
        # integration time of 33,33ms and a repeat count of 10,0, the total count time is
        # 990ms.
        #
        # Empirical tests with equation (1) were done by trying analog integration times
        # around 33,33ms and choosing a suitable repeat count. The region around 33,33ms
        # was chosen by chance and because it's inside the recommended integration range
        # (16,7ms to 166,7ms).
        #
        # The calculated repeat count is rounded to an integer and the analog integration
        # time is corrected back. For example, given an integration time of 0,5 seconds,
        # we set 33,67ms (close to 33,33ms) and repeat count 5, as calculated below:
        #
        #       time = Azero*Rcount*Atime
        #       0,5 = 2,97*Rcount*0,03333
        #       Rcount = 5,0505...
        #       Rcount,rounded = 5
        #       time = Azero*Rcount,rounded*Atime
        #       0,5 = 2,97*5*Atime
        #       Atime = 33,67ms
        #
        # Using the above procedure to compare the modeled time and the real Keithley time
        # resulted in a line with factor and displacement errors:
        #
        #       (2) time = Azero*Rcount*Atime*f + d
        #
        # The variable f represents an error proportional to the integration time,
        # while d represents a fixed delay. For example, f could be due to hardware
        # delays while integrating and computation overhead to calculate the
        # digital average. The delay d is due to "warm up" and "clean up" procedures,
        # in particular, due to device to computer communication. With a serial port
        # configuration, the factors were found to be the following:
        #
        #       (2') time = Azero*Rcount*Atime*f' + d'
        #       (3) f' = 1,09256, d' = 0,0427154
        #
        # The serial port communication is significant and happens before and after the
        # acquisition. It takes 20,83ms for sending and receiving a measurement using the
        # serial port (20 bytes/960 bytes/s). This value needs to be removed from the
        # measured delay, since it's not part of the integration time. The resulting
        # equation is accurate enough for usage as the timing model for Keithley:
        #
        #       (4) time = Azero*Rcount*Atime*1,09256 + 0,021882
        #
        # Equation (4) can then be reversed and solved for Rcount and Atime:
        #
        #       (5) Rcount = (time-0.021882)/(Azero*Atime*1,09256)
        #       (6) Atime = (time-0.021882)/(Rcount*Atime*1,09256)
        #
        # The algorithm implemented calculates (5) assuming initially Atime == 33,33ms,
        # then rounds Rcount to an integer, calculates (6) with the resulting Rcount and
        # if results are not within proper bounds, it iterates a second time.
        #
        # Note: it is known that the first and second measurements after changing the
        # count time takes longer than usual to return a measurement. The timing becomes
        # more precise starting from the third measurement. When the median filter is
        # active, the first measurement takes much longer, because the median filter
        # buffer is cleaned and filled again.

        azero = 2.97 if self.getAutoZeroing() else 0.95
        f = 1.09256
        d = 0.021882

        # Analog integration time initially equal to 33,33ms
        atime = 2/60

        # Repeat count must be between 2 and 100
        rcount = int((time-d)/(azero*atime*f))
        rcount = max(rcount, 2)
        rcount = min(rcount, 100)

        # Then, solve for integration time
        atime = (time-d)/(azero*rcount*f)

        # If integration time is out of range, fix it and iterate one more time
        if atime < 0.1/60 or atime > 10/60:
            atime = max(atime, 0.1/60)
            atime = min(atime, 10/60)
            rcount = int((time-d)/(azero*atime*f))
            rcount = max(rcount, 2)
            rcount = min(rcount, 100)
            atime = (time-d)/(azero*rcount*f)
            atime = max(atime, 0.1/60)
            atime = min(atime, 10/60)

        changed = False
        
        # Integration time must be rounded to 2 digits or Keithley will crash
        nplc = round(atime*60, 2)
        if nplc != self.getIntegrationTime():
            self.setIntegrationTime(nplc)
            changed = True

        if rcount != self.getAverageCount():
            self.setAverageCount(rcount)
            changed = True

        if not self.getAverageDigitalFilter():
            self.setAverageDigitalFilter(1)
            changed = True

        if self.getAverageTControl() != 'REP':
            self.setAverageTControl('REP')
            changed = True

        if changed:
            ca.poll(0.05)
            
    def setPresetValue(self, channel, val):
        """
        Abstract method to set the preset count of a countable target device.

        Parameters
        ----------
        channel : `int`
            The monitor channel number
        val : `int`
            The preset value

        Returns
        -------
        out : None
        """
        pass

    def startCount(self):
        """
        Abstract method trigger a count in a counter

        """
        if(not self.getStatusContinuesMode()):
            self._counting = True
            self.keithley.put("OneMeasure", 1)        
        pass
    
    def stopCount(self):
        """
        Abstract method stop a count in a counter

        """
        if(not self.getStatusContinuesMode()):
            self.keithley.put("OneMeasure", 0)        
        pass

    def canMonitor(self):
        """
        Abstract method to check if the device can or cannot be used as monitor.

        Returns
        -------
        out : `bool`
        """        
        return False

    def canStopCount(self):
        """
        Abstract method to check if the device can or cannot stop the count and return values.

        Returns
        -------
        out : `bool`
        """        
        return True

