"""Amptek MCA (MultiChannel Analyzer) class

Python class for Amptek MCA (MultiChannel Analyzer) 123 SDD device

:platform: Unix
:synopsis: Python class for Amptek MCA (MultiChannel Analyzer) 123 SDD device

.. moduleauthor:: Douglas Bezerra Beniz <douglas.beniz@lnls.br>

"""
import socket

from threading import Thread
from time import sleep

CLEAR_SPECTRUM = 'f5faf0010000fd20'
ENABLE_MCA     = 'f5faf0020000fd1f'
DISABLE_MCA    = 'f5faf0030000fd1e'
KEEP_ALIVE     = 'f5faf0200000fd01'
REQUEST_PACKET = 'f5fa01010000fe0f'

class AmptekMCA():

    udp_sock = None
    mca_alive = False
    mca_pause_alive = False
    mca_status = ''

    def __init__(self, mca_ip='10.2.48.34', udp_port=10001):
        self.openConnection(mca_ip=mca_ip, udp_port=udp_port)

    def __del__(self):
        self.mca_alive = False
        self.udp_sock.close()

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

        threadToKeepAlive = Thread(target=keepAmptekAlive)
        threadToKeepAlive.start()

    def getDeadTime(self):
        self.mca_pause_alive = True
        # send a clear Command
        self.udp_sock.sendall(bytes.fromhex(CLEAR_SPECTRUM))
        rcv_data, udp_server = self.udp_sock.recvfrom(128)

        # send a start of counting
        self.udp_sock.sendall(bytes.fromhex(ENABLE_MCA))
        rcv_data, udp_server = self.udp_sock.recvfrom(128)

        # it is necessary to wai for MCA integration (configured to 1 sec.)
        sleep(1.1)

        # send a request of information
        self.udp_sock.sendall(bytes.fromhex(REQUEST_PACKET))
        rcv_data, udp_server = self.udp_sock.recvfrom(128)

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

    def getStatus(self):
        return self.mca_status

    def closeConnection(self):
        self.mca_alive = False

        try:
            self.udp_sock.close()
        except Exception:
            pass

        self.mca_status = 'disconnected'
