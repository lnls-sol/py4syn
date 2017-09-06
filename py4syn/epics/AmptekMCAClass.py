"""Amptek MCA (MultiChannel Analyzer) class

Python class for Amptek MCA (MultiChannel Analyzer) 123 SDD device

:platform: Unix
:synopsis: Python class for Amptek MCA (MultiChannel Analyzer) 123 SDD device

.. moduleauthor:: Douglas Bezerra Beniz <douglas.beniz@lnls.br>

"""
import socket
import numpy

from threading import Thread
from time import sleep

from py4syn.epics.StandardDevice import StandardDevice
from py4syn.epics.ICountable import ICountable

# ------------------------------------------------------------
# Resquests
# ------------------------------------------------------------
CLEAR_SPECTRUM        = 'f5faf0010000fd20'
ENABLE_MCA            = 'f5faf0020000fd1f'
DISABLE_MCA           = 'f5faf0030000fd1e'
KEEP_ALIVE            = 'f5faf0200000fd01'
REQUEST_PACKET        = 'f5fa01010000fe0f'
REQUEST_SPECTRUM      = 'f5fa02010000fe0e'
REQUEST_SCA_COUNTERS  = 'f5fa04010000fe0c'

# ------------------------------------------------------------
# Responses
# ------------------------------------------------------------
ACK_OK = 'f5faff000000fd12'


"""
Class to handle Amptek MCA (Multiple Channel Analyzer) devices
"""
class AmptekMCA():

    udp_sock = None
    mca_alive = False
    mca_pause_alive = False
    mca_status = ''
    mca_ip = None
    mca_port = None

    def __init__(self, mca_ip='10.2.48.34', udp_port=10001):
        # update attributes
        self.mca_ip = mca_ip
        self.mca_port = udp_port

        # initial instantiation of attributes
        self.threadToCount = None
        self.threadToKeepAlive = None
        self.mca_counting = False
        self.sca_values = [0] * 16        # 16 channels

        # try to connect
        self.openConnection(mca_ip=mca_ip, udp_port=udp_port)

    def __del__(self):
        self.mca_alive = False
        self.udp_sock.close()

    def getMcaIP(self):
        return str(self.mca_ip)

    def getMcaPort(self):
        return str(self.mca_port)

    def openConnection(self, mca_ip='10.2.48.34', udp_port=10001):
        # Check if exist a previous connection
        previousConnection = self.mca_alive

        # Force any pre-existent connection to be closed
        self.closeConnection()

        # We intend to close any previous started thread
        # so, wait 0.1 second more than 2.0 seconds of loop to keep connection alive after close any previous connection established
        if (previousConnection):
            sleep(2.1)

        try:
            self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_sock.settimeout(2)
            self.udp_sock.connect((mca_ip, udp_port))

            self.mca_status = 'connected'
        except socket.timeout as e:
            self.mca_status = e

        self.mca_alive = True
        self.mca_pause_alive = False

        def keepAmptekAlive():
            # Send a keep-alive packet every 2 seconds to avoid missing communication with MCA
            while self.mca_alive:
                try:
                    if (self.mca_pause_alive):
                        self.mca_status = None

                    while self.mca_pause_alive:
                        sleep(0.2)

                    self.udp_sock.sendall(bytes.fromhex(KEEP_ALIVE))
                    rcv_data, udp_server = self.udp_sock.recvfrom(128)

                    self.mca_status = rcv_data

                except socket.timeout as e:
                    self.mca_status = e
                except OSError:
                    break
                sleep(2)


        self.threadToKeepAlive = Thread(target=keepAmptekAlive)
        self.threadToKeepAlive.daemon = True
        self.threadToKeepAlive.start()


    def getDeadTime(self):
        self.mca_pause_alive = True

        # wait keep-alive stop sending commands
        while (self.mca_status == bytes.fromhex(ACK_OK)):
            sleep(0.2)

        # send a clear Command
        self.udp_sock.sendall(bytes.fromhex(CLEAR_SPECTRUM))
        rcv_data, udp_server = self.udp_sock.recvfrom(128)

        # send a start of counting
        self.udp_sock.sendall(bytes.fromhex(ENABLE_MCA))
        rcv_data, udp_server = self.udp_sock.recvfrom(128)

        ## it is necessary to wai for MCA integration (configured to 1 sec.)
        emptyResponse = True

        while (emptyResponse or rcv_data == bytes.fromhex(ACK_OK)):
            # send a request of information
            self.udp_sock.sendall(bytes.fromhex(REQUEST_PACKET))
            rcv_data, udp_server = self.udp_sock.recvfrom(128)

            # Check the first 8 bytes from the answer
            rcv_data_array = numpy.array(list(rcv_data)[0:5])
            emptyResponse = numpy.all(rcv_data_array == 0)

            sleep(0.2)

        # save received data into an array
        rcv_data_array = list(rcv_data)

        #####____LOGIC to DeadTime___######
        #####__FastCount_or_InputCount####
        input_LSB = float(rcv_data_array[6])
        input_B2  = float(rcv_data_array[7])
        input_B3  = float(rcv_data_array[8])
        input_MSB = float(rcv_data_array[9])

        inputCount = input_LSB + (input_B2 + (input_B3 * 255)) * 255

        #####__SlowCount_or_TotalCount####
        total_LSB = float(rcv_data_array[10])
        total_B2  = float(rcv_data_array[11])
        total_B3  = float(rcv_data_array[12])
        total_MSB = float(rcv_data_array[13])

        totalCount = total_LSB + (total_B2 + (total_B3 * 255)) * 255

        deadTime = 0

        try:
            deadTime = round(float((float(inputCount) - float(totalCount)) / float(inputCount)) * 100, 2)
        except Exception as ex:
            print('Exception when calculating dead-time! Error: {0}'.format(ex))

        # send an end of counting
        self.udp_sock.sendall(bytes.fromhex(DISABLE_MCA))
        rcv_data, udp_server = self.udp_sock.recvfrom(128)

        self.mca_pause_alive = False

        return deadTime

    def getSpectrum(self):
        returnInfo = ""

        # Inform thread of keep alive to wait...
        self.mca_pause_alive = True

        # wait keep-alive stop sending commands
        while (self.mca_status == bytes.fromhex(ACK_OK)):
            sleep(0.2)

        try:
            # Send a clear command
            self.udp_sock.sendall(bytes.fromhex(CLEAR_SPECTRUM))
            rcv_data, udp_server = self.udp_sock.recvfrom(128)

            # Send a start of counting
            self.udp_sock.sendall(bytes.fromhex(ENABLE_MCA))
            rcv_data, udp_server = self.udp_sock.recvfrom(128)

            ## It is necessary to wait for MCA integration (configured to 1 sec.)
            emptyResponse = True

            while (emptyResponse or rcv_data == bytes.fromhex(ACK_OK)):
                # Send a request of information
                self.udp_sock.sendall(bytes.fromhex(REQUEST_SPECTRUM))
                rcv_data, udp_server = self.udp_sock.recvfrom(128)

                # Check the first 8 bytes from the answer
                rcv_data_array = numpy.array(list(rcv_data)[0:5])
                emptyResponse = numpy.all(rcv_data_array == 0)

                sleep(0.2)

            returnInfo = rcv_data
        except Exception as ex:
            returnInfo = str(ex)

        # Send an end of counting
        self.udp_sock.sendall(bytes.fromhex(DISABLE_MCA))
        rcv_data, udp_server = self.udp_sock.recvfrom(128)

        # Inform keep alive to continue...
        self.mca_pause_alive = False

        return returnInfo


    def getScaCounters(self):
        returnInfo = ""

        # Inform thread of keep alive to wait...
        self.mca_pause_alive = True

        # Update that we are counting...
        self.mca_counting = True

        # wait keep-alive stop sending commands
        while (self.mca_status == bytes.fromhex(ACK_OK)):
            sleep(0.2)

        try:
            # Send a clear command
            self.udp_sock.sendall(bytes.fromhex(CLEAR_SPECTRUM))
            rcv_data, udp_server = self.udp_sock.recvfrom(128)

            # Send a start of counting
            self.udp_sock.sendall(bytes.fromhex(ENABLE_MCA))
            rcv_data, udp_server = self.udp_sock.recvfrom(128)

            ## It is necessary to wait for MCA integration (configured to 1 sec.)
            emptyResponse = True

            while (emptyResponse or rcv_data == bytes.fromhex(ACK_OK)):
                # Send a request of information
                self.udp_sock.sendall(bytes.fromhex(REQUEST_SCA_COUNTERS))
                rcv_data, udp_server = self.udp_sock.recvfrom(128)

                # Check the first 8 bytes from the answer
                rcv_data_array = numpy.array(list(rcv_data)[0:5])
                emptyResponse = numpy.all(rcv_data_array == 0)

                sleep(0.2)

            # SCA counters returns 16 values (with LSB, Byte2, Byte3 and MSB in 4 bytes for each)...
            rcv_data_array = list(rcv_data)
            returnArray = []

            for counter in range(16):
                lsb = float(rcv_data_array[6 + (counter * 4)])
                b2  = float(rcv_data_array[7 + (counter * 4)])
                b3  = float(rcv_data_array[8 + (counter * 4)])
                msb = float(rcv_data_array[9 + (counter * 4)])

                tempValue = lsb + (b2 + (b3 * 255)) * 255

                returnArray.append(tempValue)

            returnInfo = returnArray
        except Exception as ex:
            returnInfo = str(ex)

        # Send an end of counting
        self.udp_sock.sendall(bytes.fromhex(DISABLE_MCA))
        rcv_data, udp_server = self.udp_sock.recvfrom(128)

        # Inform keep alive to continue...
        self.mca_pause_alive = False

        # Update that we stopped counting...
        self.mca_counting = False

        # Update SCA values, in the case we got them...
        if ((type(returnInfo) == list) and (len(returnInfo) == 16)):
            self.sca_values = returnInfo

        # Reset thread of counting
        self.threadToCount = None

        return returnInfo


    def getStatus(self):
        return self.mca_status


    def closeConnection(self):
        self.mca_alive = False

        try:
            self.udp_sock.close()
        except Exception:
            pass

        self.mca_status = 'disconnected'


    def startCount(self):
        try:
            if (self.threadToCount is None):
                self.threadToCount = Thread(target=self.getScaCounters)
                self.threadToCount.daemon = True
                self.threadToCount.start()
        except:
            pass

    def getValue(self, channel):
        try:
            return self.sca_values[channel -1]
        except:
            return -1


"""
Class to handle Amptek SCA (Single Channel Analyzer) of a specific MCA
"""
class AmptekSCA(StandardDevice, ICountable):

    def __init__(self, mca, mnemonic, channel):
        StandardDevice.__init__(self, mnemonic)

        self.mca      = mca
        self.mnemonic = mnemonic
        self.channel  = channel


    def setPresetValue(self, channel, value):
        # Amptek MCA is configured through a specific software
        pass


    def setCountTime(self, time):
        # Amptek MCA is configured through a specific software
        pass


    def getCountTime(self):
        # Amptek MCA is configured through a specific software
        # Used time to accummulate is 1 second
        return 1


    def getValue(self, **kwargs):
        if(kwargs):
            return self.mca.getValue(channel=kwargs['channel'])

        return self.mca.getValue(channel=1)


    def startCount(self):
        self.mca.startCount()


    def stopCount(self):
        # TBD
        pass


    def canMonitor(self):
        # TBD
        return False


    def canStopCount(self):
        # TBD
        return False


    def isCounting(self):
        return self.mca.isCounting()


    def wait(self):
        while(self.mca.isCounting()):
            sleep(0.1)
