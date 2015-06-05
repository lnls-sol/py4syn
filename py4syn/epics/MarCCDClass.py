"""MarCCD X-ray detector system class

Python class for MarCCD cameras

:platform: Unix
:synopsis: Python class for MarCCD cameras

.. moduleauthor:: Henrique Dante de Almeida <henrique.almeida@lnls.br>

"""
from socket import socket, AF_INET, SOCK_STREAM
from threading import Event
from time import sleep

from epics import PV, ca

from py4syn.epics.ICountable import ICountable
from py4syn.epics.StandardDevice import StandardDevice
from py4syn.utils.timer import Timer

class ToggleShutter(StandardDevice):
    def __init__(self, mnemonic, shutter, shutterReadback):
        super().__init__(mnemonic)

        self.read = PV(shutterReadback)
        self.toggle = PV(shutter)

        self._open = self.read.get()
        self.changed = Event()
        self.read.add_callback(self.onReadChange)

    def isOpen(self):
        return self._open

    def onReadChange(self, value, **kwargs):
        self._open = value
        self.changed.set()

    def wait(self, timeout=3):
        ca.flush_io()
        self.changed.wait(timeout)

    def change(self, open, wait=False):
        if self.isOpen() == open:
            self.changed.set()
            return

        self.changed.clear()
        self.toggle.put(1)
        ca.flush_io()

        if wait:
            self.wait()

    def open(self, wait=False):
        self.change(open=True, wait=wait)

    def close(self, wait=False):
        self.change(open=False, wait=wait)

class SimpleShutter(StandardDevice):
    SHUTTER_OPEN = 0
    SHUTTER_CLOSE = 1

    def __init__(self, mnemonic, shutter):
        super().__init__(mnemonic)

        self.shutter = PV(shutter)

    def isOpen(self):
        return self.shutter.get() == self.SHUTTER_OPEN

    def wait(self, timeout=3):
        pass

    def open(self, wait=False):
        self.shutter.put(self.SHUTTER_OPEN, wait=wait)

    def close(self, wait=False):
        self.shutter.put(self.SHUTTER_CLOSE, wait=wait)

class NullShutter(StandardDevice):
    def __init__(self, mnemonic):
        super().__init__(mnemonic)
        self.o = False

    def isOpen(self):
        return self.o

    def wait(self, timeout=3):
        pass

    def open(self, wait=False):
        self.o = True

    def close(self, wait=False):
        self.o = False

class MarCCD(StandardDevice, ICountable):
    """
    Class to control MarCCD cameras via TCP sockets.

    Examples
    --------
    >>> from shutil import move
    >>> from py4syn.epics.MarCCDClass import MarCCD
    >>> 
    >>> def getImage(host='localhost', port=2222, fileName='image.tif', shutter=''):
    ...     camera = MarCCD(name, (host, port), shutterType='simple', shutter=shutter)
    ...     camera.setCountTime(10)
    ...     camera.startCount()
    ...     camera.wait()
    ...     camera.stopCount()
    ...     camera.writeImage('/remote/' + fileName)
    ...     move('/remote/' + fileName, '/home/user/' + fileName)
    ...     camera.close()
    ...
    >>> def cameraWithoutShutter(name='', host='localhost', port=2222):
    ...     return MarCCD(name, (host, port), shutterType='null')
    ...
    >>> def acquireSetWithCorrection(camera, exposure=10, count=10, prefix='data'):
    ...     try:
    ...         camera.darkNoise()
    ...         camera.setCountTime(exposure)
    ...         camera.setSubScan(count=2)
    ...
    ...         for i in range(count):
    ...             remote = '/remote/%s-%02d.tif' % (prefix, i)
    ...             local = '/home/user/%s-%02d.tif' % (prefix, i)
    ...             camera.startCount()
    ...             camera.wait()
    ...             camera.stopCount()
    ...             camera.startCount()
    ...             camera.wait()
    ...             camera.stopCount()
    ...             camera.dezinger()
    ...             camera.correct()
    ...             camera.writeImage(remote)
    ...             move(remote, local)
    ...     finally:
    ...         camera.close()
    ...
    """

    STATE_MASK_BUSY = 0x8
    STATE_MASK_ACQUIRING = 0x30
    STATE_MASK_READING = 0x300
    STATE_MASK_CORRECTING = 0x3000
    STATE_MASK_WRITING = 0x30000
    STATE_MASK_DEZINGERING = 0x300000
    STATE_MASK_SAVING = 0x33300
    STATE_MASK_ERROR = 0x44444
    TIMEOUT = 60
    URGENT_TIMEOUT = 0.5

    def __init__(self, mnemonic, address, shutterType, shutter=None,
                 shutterReadBack=None):
        """
        **Constructor**
        See :class:`py4syn.epics.StandardDevice`

        Parameters
        ----------
        mnemonic : `string`
            Camera mnemonic
        address : `tuple`
            Camera host server Internet address
        shutterType : `string`
            The type of software controlled shutter. The type can be "simple", "toggle"
            or "null". The null shutter completely disables software controlled shutter.
            The simple shutter is an EPICS PV that must be set to 0 to open the shutter
            and 1 to close the shutter. The toggle shutter uses two PVs, one that
            changes the shutter state whenever written to and another to read back the
            current shutter state.
        shutter :  `string`
            The shutter PV name. Only meaningful if the shutter type is not null.
        shutterReadBack : `string`
            The toggle shutter read back PV.
        """
        super().__init__(mnemonic)
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect(address)
        self.counting = False
        self.timer = Timer(1)
        self.subScan = False
        self.subScanStep = 0

        shutterName = mnemonic + '_shutter'

        if shutterType == 'toggle':
            self.shutter = ToggleShutter(shutterName, shutter, shutterReadback)
        elif shutterType == 'simple':
            self.shutter = SimpleShutter(shutterName, shutter)
        else:
            self.shutter = NullShutter(shutterName)

        self.shutter.close(wait=True)

        # Force clearing busy and error flags. Both busy and error flags
        # May get stuck after exceptional conditions.
        try:
            state = self.waitWhile(self.STATE_MASK_BUSY, self.URGENT_TIMEOUT)
        except RuntimeError:
            self.socket.send(b'abort\n')

            try:
                self.setState(0, self.URGENT_TIMEOUT)
            except RuntimeError as e:
                self.socket.close()
                raise e from None

    def close(self):
        """
        Cleans up and closes camera remote connection. This method must be called when
        finishing operation with the camera.
        """
        self.stopCount()
        self.shutter.close()

        # If we caused an error, send an abort to try to fix things
        try:
            if self.getState(self.URGENT_TIMEOUT) & self.STATE_MASK_ERROR:
                self.socket.send(b'abort\n')
        except:
            pass

        self.socket.close()

    def __str__(self):
        return '%s %s' % (self.getMnemonic(), str(self.socket.getpeername()))

    def darkNoise(self, delay=0, moveShutter=True):
        """
        Prepares a dark noise image to be used as a correction image by the server.
        One of the steps after acquiring an image is to correct it by subtracting the
        dark noise image from it. This method is used to generate the dark noise image
        to be used later in the acquisitions. The method must be called with the camera
        covered. A dark noise image must be generated at least once after starting the
        MarCCD server.

        .. note::
            The following guideline is available on the MarCCD user guide: "The
            background doesn't have to be retaken for every data image taken, but
            generally should be retaken at the start of every new data set, or once every
            half hour, whichever is sooner (depending on the thermal stability of the
            hutch). For the MarCCD detector, if a mismatch in the level of the 4 quadrants
            of data frames is noticed, the bias is probably drifting and should be
            recollected (and maybe should be set to be collected more often)."

        Parameters
        ----------
        delay : `float`
            The time for each background acquisition. The MarCCD camera can either
            be calibrated with a zero delay between the acquisitions (this is called
            a bias frame acquisition in MarCCD manual), or with a non-zero (a standard
            dark frame acquisition). Note that 2 background acquisitions are done.
            They are then passed through the dezinger algorithm, which averages and
            removes outlier spots in the image.
        moveShutter : 'bool'
            Set to True to close and restore the shutter while acquiring the dark image.
        """
        closed = not self.shutter.isOpen()

        if not closed and moveShutter:
            self.shutter.close()

        self.socket.send(b'start\n')
        sleep(delay)
        self.socket.send(b'readout,2\n')
        self.socket.send(b'start\n')
        sleep(delay)
        self.socket.send(b'readout,1\n')
        self.socket.send(b'dezinger,1\n')

        if not closed and moveShutter:
            self.shutter.open()

    def getValue(self, **kwargs):
        """
        This is a dummy getValue method that always returns zero, which is part
        of the :class:`py4syn.epics.ICountable` interface. The MarCCD does not return
        a value while scanning. Instead, it stores a file with the resulting image.
        """
        return 0

    def setCountTime(self, t):
        """
        Sets the image acquisition time.

        Parameters
        ----------
        t : `float`
            Acquisition time
        """
        self.timer = Timer(t)

    def setPresetValue(self, channel, val):
        pass

    def setSubScan(self, count=2):
        """
        Configure the MarCCD object to know that each acquisition will be done in
        multiple steps. This effectivelly means that a series of acquisitions will
        be done in sequence, which will be processed together, resulting in a single
        final image. This method is mainly required for the :meth:`dezinger` method
        to work.

        Parameters
        ----------
        count : `int`
            Number of sub scans that will compose a single final image. Can be either
            1, to disable sub scan logic, or 2, which will make :meth:`stopCount` store
            images alternatedly in "scratch" (auxiliary) memory and "raw" (main) memory.
        """
        if count < 1 or count > 2:
            raise ValueError('Invalid count value')

        self.subScan = count == 2
        self.subScanStep = 0

    def startCount(self):
        """
        Starts acquiring an image. This will acquire image data until asked to stop
        with :meth:`stopCount`. This method automatically opens the shutter.

        .. note::
            Due to way the camera protocol is currently implemented, this method
            ignores the configured acquisition count time. Because of that, the proper
            way to do a timed acquisition is to follow this method call with :meth:`wait`,
            then immediatelly call :meth:`stopCount`. The :func:`py4syn.utils.scan.scan`
            function in Py4Syn executes this method sequence.

        See: :meth:`setCountTime`, :meth:`stopCount`, :meth:`wait`

            Examples
            --------
            >>> def acquire(marccd, time):
            ...     marccd.setCountTime(time)
            ...     marccd.startCount()
            ...     marccd.wait()
            ...     marccd.stopCount()
            ...
        """
        if self.counting == True:
            raise RuntimeError('Already counting')

        # Best effort wait for idle state
        try:
            self.waitWhile(self.STATE_MASK_ACQUIRING, self.URGENT_TIMEOUT)
        except RuntimeError as e:
            pass

        # Wait for reading done when doing fast exposures
        if self.timer.timeout < 1:
            try:
                self.waitWhile(self.STATE_MASK_READING, self.URGENT_TIMEOUT)
            except RuntimeError as e:
                pass

        self.socket.send(b'start\n')
        self.shutter.open()
        self.timer.mark()
        self.counting = True

    def stopCount(self):
        """
        Stops acquiring the image and stores it into server memory. The acquired image
        will be available to apply corrections and to be written to an output file.
        This method closes the shutter.

        If no call to :meth:`startCount` was done before calling this method, then
        nothing is done.
        """
        if not self.counting:
            return

        self.shutter.close()

        if self.subScan and self.subScanStep == 0:
            cmd = b'readout,2\n'
            self.subScanStep = 1
        else:
            cmd = b'readout,0\n'
            self.subScanStep = 0

        self.socket.send(cmd)
        self.counting = False

    def correct(self):
        """
        Queues image correction on the MarCCD server. After the image is corrected,
        it can be saved to a file.

        There are three corrections applied: dark noise image subtraction, flat field
        correction and geometric correction. The dark noise correction uses a dark image
        to fix the reference (zero) intensity levels for each pixel. The flat field
        correction uses a bright image to correct the gain for each pixel.
        The geometric correction fixes distortion from the fiber optic taper.

        .. note::
            The dark noise image should be frequently generated. Use the method
            :meth:`darkNoise` for that.
            
        See: :meth:`darkNoise`
        """

        self.waitWhile(self.STATE_MASK_DEZINGERING | self.STATE_MASK_CORRECTING |
                       self.STATE_MASK_BUSY, self.TIMEOUT)
        self.socket.send(b'correct\n')

    def dezinger(self):
        """
        Apply the dezinger correction algorithm in 2 images and store the resulting
        image in the MarCCD server. The dezinger algorithm averages corresponding pixels
        from each image, but if they deviate too much, it discards the brighter one and
        keeps the lower value. This removes the "zingers", bright spots in the image,
        which are not caused by the input light.

        To be able to use the dezinger method, 2 images must be present in server
        memory. This can be accomplished by calling :meth:`setSubScan` before the
        acquisition.

        .. note::
            The following guildeline is present in MarCCD manual: "Dezingering does
            require special care that the two images are truly identical (same X-ray
            dose, same movement of the sample, etc.); otherwise the statistical test
            will yield unpredictable results. In particular, if the X-ray beam is not
            constant intensity, or the sample is decaying, then the exposure times and
            diffractometer motions must compensate for that. If there are significant
            differences between the frames, then the artifacts created by dezingering
            may yield worse results than simply using normal, single-read images with
            zingers in them. Though they are not aethetically pleasing, some kinds of
            data analysis can tolerate many zingers.

            Examples
            --------
            >>> def acquireTwiceAndDezinger(marccd, time):
            ...     marccd.setCountTime(time)
            ...     marccd.setSubScan(count=2)
            ...     marccd.startCount()
            ...     marccd.wait()
            ...     marccd.stopCount()
            ...     marccd.startCount()
            ...     marccd.wait()
            ...     marccd.stopCount()
            ...     marccd.dezinger()
            ...
        """

        # It's not clear if dezinger can be correctly queued while reading and
        # correction is being done, so just wait until everything is finished
        # to make sure that dezinger will apply to the right images. There
        # have been cases where dezinger finished before the read command finished.
        self.waitWhile(self.STATE_MASK_READING | self.STATE_MASK_CORRECTING |
                       self.STATE_MASK_DEZINGERING | self.STATE_MASK_BUSY, self.TIMEOUT)
        self.socket.send(b'dezinger,0\n')

    def writeImage(self, fileName, wait=True):
        """
        Write the image stored in MarCCD server memory in a file. This method does not
        store the resulting image in the local machine. Since current MarCCD server
        protocol does not allow locally downloading the resulting image, this method only
        asks for the MarCCD camera server to store the image in a remote location. To
        make the file accessible locally, other means must be used, for example, by
        instructing the server to save the image in shared storage.

        Parameters
        ----------
        fileName : `string`
            Target file name in remote MarCCD server
        wait : `bool`
            Set to True if the method should block until the image is written to disk
        """
        self.waitWhile(self.STATE_MASK_ACQUIRING | self.STATE_MASK_READING |
                       self.STATE_MASK_CORRECTING |self.STATE_MASK_WRITING |
                       self.STATE_MASK_BUSY, self.TIMEOUT)
        cmd = 'writefile,%s,1\n' % fileName
        self.socket.send(cmd.encode())

        if wait:
            # Wait some time for the camera to say it started writing. This
            # is necessary because the server may return finished state (0)
            # before it started writing.
            try:
                self.waitUntil(self.STATE_MASK_WRITING, self.URGENT_TIMEOUT)
            except RuntimeError:
                pass

            self.waitWhile(self.STATE_MASK_ACQUIRING | self.STATE_MASK_READING |
                           self.STATE_MASK_CORRECTING |self.STATE_MASK_WRITING |
                           self.STATE_MASK_BUSY, self.TIMEOUT)

    def canMonitor(self):
        return False

    def canStopCount(self):
        return True

    def isCounting(self):
        return self.counting

    def wait(self):
        """
        Blocks until the configured count time passes since the call to
        :meth:`startCount`. The time amount is configured with :meth:`setCountTime`, or
        1 second by default.

        If an acquisition has not been started, this method returns immediatelly.

        See: :meth:`setCountTime`, :meth:`startCount`
        """
        if not self.isCounting():
            return

        ca.flush_io()
        self.timer.wait()

    def stateRequest(self, request, timeout=TIMEOUT):
        """
        Helper method used to get or set camera state.

        Parameters
        ----------
        request : `string`
            Command to be passed to the camera
        timeout : `float`
            Time to wait for camera answer

        Returns
        -------
        `int`
        """

        self.socket.send(request)
        timer = Timer(timeout)

        r = b''
        while b'\n' not in r and timer.wait(self.socket):
            r += self.socket.recv(1)

        if timer.expired():
            raise RuntimeError('Camera is not answering')

        r = r.strip(b'\x00\n')

        return int(r, 0)

    def getState(self, timeout=TIMEOUT):
        """
        Returns the camera state. The state can be used to check for errors, to find out
        which operations are queued or being executed and if the server is busy
        interpreting a command.

        The camera state is an integer with a 4-bit value, plus five 4-bit fields:
        acquire, read, correct, write and (highest) dezinger. The low 4-bit state value
        can be 0, for idle, 7 for bad request and 8 for busy. Each 4-bit field has
        4 flags: queued (0x1), executing (0x2), error (0x4) and reserved (0x8).
        For example, the state 0x011200 means that a read is executing, a correction is
        queued and a write is queued. The state mask 0x444444 can be used to look for an
        error on any operation. The lowest field (state) uses the value 8 to indicate
        it's busy processing a command, so state 0x8 means "interpreting command".

        Parameters
        ----------
        timeout : `float`
            Time to wait for camera answer

        Returns
        -------
        `int`
        """
        return self.stateRequest(b'get_state\n', timeout)

    def setState(self, state, timeout=TIMEOUT):
        """
        Changes the camera state bit field. This method does not change the operating
        state, just the reported integer value. It is a helper method to deal with a
        quirk in the MarCCD server that makes the error and busy bits to get stuck and
        never reset. Usually the only value that makes sense for the state is zero,
        to clear all the bits.

        See: :meth:`getState`

        Parameters
        ----------
        state : `int`
            Time to wait for camera answer
        timeout : `float`
            Time to wait for camera answer
        """
        cmd = 'set_state,%d\n' % state
        self.stateRequest(cmd.encode(), timeout)

    def waitWhileOrUntil(self, condition, timeout=TIMEOUT, until=False):
        """
        Helper method that implements :meth:`waitWhile` and :meth:`waitUntil`
        """

        state = self.getState(timeout)
        if state & self.STATE_MASK_ERROR:
            raise RuntimeError('Camera returned error: %x' % state)
        timer = Timer(timeout)

        while until ^ bool(state & condition) and timer.check():
            state = self.getState(timeout)

            if state & self.STATE_MASK_ERROR:
                raise RuntimeError('Camera returned error: %x' % state)

        if timer.expired():
            raise RuntimeError('Camera got stuck condition: %x, state: %x' %
                               (condition, state))

    def waitWhile(self, condition, timeout=TIMEOUT):
        """
        Blocks while the camera state asserts a certain condition. This method can
        be used to confirm that an operation has finished, or if the camera is reporting
        an error. The condition is a bit mask with the same meanings as described in
        :meth:`getState`. For example, calling this method with condition set to
        0x30 blocks while an aquisition is either queued or executing. Similarly,
        it's possible to block while the camera server is either processing or writing
        the image with condition set to 0x333308.

        This method detects errors automatically by raising an exception if any error
        bit is set.

        See: :meth:`getState`

        Parameters
        ----------
        condition : `int`
            State condition mask. If any of the condition bits is set, the condition
            is considered to be true.
        timeout : `float`
            Time to wait for the condition to be deasserted
        """

        self.waitWhileOrUntil(condition, timeout, until=False)

    def waitUntil(self, condition, timeout=TIMEOUT):
        """
        Blocks until the camera state asserts a certain condition. This method can
        be used to confirm that an operation has started, or if the camera is reporting
        an error. The condition is a bit mask with the same meanings as described in
        :meth:`getState`. For example, calling this method with condition set to
        0x20 blocks until an aquisition is executing.

        This method detects errors automatically by raising an exception if any error
        bit is set.

        See: :meth:`getState`

        Parameters
        ----------
        condition : `int`
            State condition mask. If any of the condition bits is set, the condition
            is considered to be true.
        timeout : `float`
            Time to wait for the condition to be deasserted
        """

        self.waitWhileOrUntil(condition, timeout, until=True)

    def waitForImage(self):
        """
        Blocks until the acquired image has been corrected and written to disk. This
        can be used any time after calling :meth:`stopCount` to make sure file
        operations can be performed on the resulting image (copied, post-processed, etc.)
        """
        # Wait some time for the camera to say it started writing. This
        # is necessary because the server may return finished state (0)
        # before it started writing.
        try:
            self.waitUntil(self.STATE_MASK_WRITING, self.URGENT_TIMEOUT)
        except RuntimeError:
            pass

        try:
            self.waitWhile(self.STATE_MASK_SAVING | self.STATE_MASK_BUSY)
        except RuntimeError:
            raise RuntimeError('Camera took too long to write image file')
