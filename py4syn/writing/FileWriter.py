from abc import ABCMeta, abstractmethod

"""Standard File Writer Class

Python Class for File Writer functions and informations.

:platform: Unix
:synopsis: Python Class for Standard Device informations.

.. moduleauthor:: Hugo Henrique Slepicka <hugo.slepicka@lnls.br>

"""
class FileWriter:
    """
    Class to be inherited by all data output classes in order to be transparently used in scan functions.

    By default some informations such as username, start and end timestamp, command and others are already filled by the scan routines using the getters and setters bellow.
    """
    def __init__(self, fileName):
        """
        **Constructor**

        Parameters
        ----------
        fileName : `string`
            The output filename
        """
        self.__fileName = fileName

        self.__username = ""
        self.__command = ""
        self.__comments = []
        self.__startDate = None
        self.__endDate = None

        self.__dataSize = None
        self.__devices = []
        self.__signals = []
        self.__devicesData = {}
        self.__signalsData = {}

    @abstractmethod
    def writeHeader(self):
        """
        Abstract method to start the header write process.

        """
        raise NotImplementedError

    @abstractmethod
    def writeData(self, partial=False, idx=-1):
        """
        Abstract method to start the data write process.

        Parameters
        ----------
        channel : `int`
            If `partial` is **True** it means that only data at position `idx` must be written. Otherwise this function must write all data. 
        idx : `int`
            The data index to be saved

        """
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """
        Abstract method called at the end of the process.

        """
        raise NotImplementedError

    def getFileName(self):
        """
        Returns the filename in use.

        Returns
        -------
        `string`
        """
        return self.__fileName

    def getUsername(self):
        """
        Returns the username.

        Returns
        -------
        `string`
        """
        return self.__username

    def getCommand(self):
        """
        Returns the command.

        Returns
        -------
        `string`
        """
        return self.__command

    def getComments(self):
        """
        Returns the comments list.

        Returns
        -------
        `list`
        """
        return self.__comments

    def getStartDate(self):
        """
        Returns the process start timestamp.

        Returns
        -------
        `string`
        """
        return self.__startDate

    def getEndDate(self):
        """
        Returns the process end timestamp.

        Returns
        -------
        `string`
        """
        return self.__endDate

    def getDataSize(self):
        """
        Returns the data size in number of lines.

        Returns
        -------
        `int`
        """
        if self.__dataSize is None:
            s = [len(d) for _, d in self.__signalsData.items()]
            d = [len(d) for _, d in self.__devicesData.items()]
            self.__dataSize = max(s+d)
        return self.__dataSize

    def getDevices(self):
        """
        Returns the list of devices mnemonics.

        Returns
        -------
        `list`
        """
        return self.__devices

    def getSignals(self):
        """
        Returns the list of signals mnemonics.

        Returns
        -------
        `list`
        """
        return self.__signals

    def getDevicesData(self):
        """
        Returns the map containing all devices data in a map where the device mnemonic is the key and the values are an array.

        Returns
        -------
        `map`
        """
        return self.__devicesData

    def getSignalsData(self):
        """
        Returns the map containing all signals data in a map where the device mnemonic is the key and the values are an array.

        Returns
        -------
        `map`
        """
        return self.__signalsData

    def setUsername(self, value):
        """
        Set the username information

        Parameters
        ----------
        value : `string`
            Username information
        """
        self.__username = value

    def setCommand(self, value):
        """
        Set the command information

        Parameters
        ----------
        value : `string`
            Command information
        """
        self.__command = value

    def setComments(self, value):
        """
        Set the comments list

        Parameters
        ----------
        value : `list`
            Comments list
        """
        self.__comments = value

    def insertComment(self, value):
        """
        Insert a new comment in the list

        Parameters
        ----------
        value : `string`
            Comment information
        """
        self.__comments.append(value)

    def setStartDate(self, value):
        """
        Set the start date

        Parameters
        ----------
        value : `string`
            Date when the process started
        """
        self.__startDate = value

    def setEndDate(self, value):
        """
        Set the end date

        Parameters
        ----------
        value : `string`
            Date when the process finished
        """
        self.__endDate = value

    def setDataSize(self, value):
        """
        Set the data size in number of lines

        Parameters
        ----------
        value : `int`
            Data size
        """
        self.__dataSize = value

    def setDevices(self, value):
        """
        Set the devices list

        Parameters
        ----------
        value : `list`
            Devices Mnemonic list
        """
        self.__devices = value

    def insertDevice(self, value):
        """
        Insert a new device in the list

        Parameters
        ----------
        value : `string`
            Device mnemonic
        """
        self.__devices.append(value)

    def setSignals(self, value):
        """
        Set the signals list

        Parameters
        ----------
        value : `list`
            Signals Mnemonic list
        """
        self.__signals = value

    def insertSignal(self, value):
        """
        Insert a new signal in the list

        Parameters
        ----------
        value : `string`
            Signal mnemonic
        """
        self.__signals.append(value)

    def setDevicesData(self, value):
        """
        Set the devices data map

        Parameters
        ----------
        value : `map`
            Devices data map
        """
        self.__devicesData.append(value)

    def insertDeviceData(self, device, value, index=None):
        """
        Insert a new data value for the informed device in the map.
        Parameters
        ----------
        device : `string`
            Device mnemonic
        value : `float, int, str, etc`
            Collected value
        """
        for i in device:
            if device not in list(self.getDevicesData().keys()):
                self.getDevicesData()[i] = value
            else:
                self.getDevicesData()[i].append(value)

    def setSignalsData(self, value):
        """
        Set the signals data map

        Parameters
        ----------
        value : `map`
            Signals data map
        """
        self.__signalsData = value

    def insertSignalData(self, signal, value, index=None):
        """
        Insert a new data value for the informed signal in the map.
        Parameters
        ----------
        signal : `string`
            Signal mnemonic
        value : `float, int, str, etc`
            Collected value
        """

        for i in signal:
            if signal not in list(self.getSignalsData().keys()):
                self.getSignalsData()[i] = value
            else:
                self.getSignalsData()[i].append(value)
