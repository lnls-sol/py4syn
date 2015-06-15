from select import select
from time import monotonic, sleep

class Timer:
    """
    A class to track elapsed time and timeouts. The timer class stores an initial time
    and a timeout value. These can be used to check or wait for a certain moment in time.

    Examples
    --------
    >>> from py4syn.utils.timer import Timer
    >>> 
    >>> def waitAcquisition(device, timeout=60):
    ...     timer = Timer(timeout)
    ...     while device.isAcquiring() and timer.check():
    ...         device.updateState()
    ...
    ...     if timer.expired():
    ...         raise TimeoutError()
    ...
    """
    def __init__(self, timeout):
        """
        The constructor receives a timeout parameter, which is saved and marks the initial
        time.

        See: :meth:`mark`

        Parameters
        ----------
        timeout : `float`
            Timeout limit
        """
        self.timeout = timeout
        self.mark()

    def mark(self):
        """
        Resets the initial time value and resets the expired flag. After calling this
        method, timeout checking or waiting will use the new time value as the initial
        moment.
        """
        self.t1 = monotonic()
        self.exp = False

    def check(self):
        """
        Checks if the timeout has been expired by reading the current time value and
        comparing it against the initial time and the timeout. The expiration value is
        saved and can be read later with :meth:`expired`. Returns True if the timeout
        hasn't been reached, or False if the timer expired.

        See: :meth:`expired`

        Returns
        -------
        `bool`
        """
        now = monotonic()
        if (now-self.t1) >= self.timeout:
            self.exp = True

        return not self.exp

    def expired(self):
        """
        Reads the cached expired value from :meth:`check` or :meth:`wait`.

        See: :meth:`check`, :meth:`wait`

        Returns
        -------
        `bool`
        """
        return self.exp

    def wait(self, file=None):
        """
        Blocks until the timeout has expired, or, if the file parameter is not empty,
        until the file becomes ready with input data. The expiration value is saved
        and can be read later with :meth:`expired`. Returns False if the timeout expired,
        or True if the file is ready for reading before the timer is expired.

        This method only checks if the file is ready for reading, but it does not read
        anything from it. It will continuously return True while the file is not
        read and the timeout does not expire.

        See: :meth:`expired`

        Returns
        -------
        `bool`
        """
        now = monotonic()
        t2 = self.t1 + self.timeout
        w = t2-now

        if w <= 0:
            self.exp = True
            return False

        if file is not None:
            l = [file]
        else:
            l = []

        ready = select(l, [], [], w)[0]
        self.exp = len(ready) == 0
        return not self.exp
