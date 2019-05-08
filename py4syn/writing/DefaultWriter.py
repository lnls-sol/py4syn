from py4syn.writing.FileWriter import FileWriter
import time
import datetime
"""Default File Writer Class

Python Class to generate PyMCA/SPEC-like file output.

:platform: Unix
:synopsis: Python Class to generate PyMCA/SPEC-like file output.

.. moduleauthor:: Hugo Henrique Slepicka <hugo.slepicka@lnls.br>

"""
class DefaultWriter(FileWriter):
    """
    Class to be used when generating PyMCA/SPEC-like output.
    
    For more informations see :class:`py4syn.writing.FileWriter`
    """    
    def __init__(self, fileName):
        """
        **Constructor**

        Parameters
        ----------
        fileName : `string`
            The output filename
        """        
        FileWriter.__init__(self, fileName)
        self.__file = open(fileName, "a")
        
    def writeHeader(self):
        # PyMCA-like Header File
        r = "#F " + str(self.getFileName) + "\n"
        r = "#E " + str(int(time.time())) + "\n"
        r += "#D " + "{0:%a %b %d %H:%M:%S %Y}".format(datetime.datetime.now()) + "\n"
        r += "#C py4syn User = " + self.getUsername() + "\n"
        
        for i in range(len(self.getComments())):
            r += "#C"+str(i) + " " + self.getComments()[i] + "\n"
            
        r += "#S 1 " + self.getCommand() + "\n"
        r += "#D " + "{0:%a %b %d %H:%M:%S %Y}".format(self.getStartDate()) + "\n"

        r += "#M " + str(self.getDataSize()) + "\n"
        
        numberOfFields = len(self.getDevices()) + len(self.getSignals())
        r += "#N " + str(numberOfFields) + "\n"     
        
        self.__file.write(r)
        
        # insert scan devices header
        line = ''
        for d in range(len(self.getDevices())):
            line += '  ' if line != '' else ''
            line += self.getDevices()[d]

        for s in range(len(self.getSignals())):
            line += '  ' if line != '' else ''
            line += self.getSignals()[s]            
        
        self.__file.write('#L ' + line + '\n')
        self.__file.flush()
        
    def writeData(self, partial=False, idx=-1):
        if(not partial):
            # start writing data        
            try:
                for i in range(self.getDataSize()):        
                    line = self.__scanDataToLine(i)
                    self.__file.write(line + '\n')
            except:
                pass
        else:
            line = self.__scanDataToLine(idx)
            self.__file.write(line + '\n')

        self.__file.flush()

    def close(self):
        self.__file.flush()
        self.__file.close()

    def __fmt(self, n, precision):
        import math
        try:
            if(math.log10(abs(n)) < -precision):
                return '{:.{}e}'.format(n, precision)
        except:
            pass
        return '{:.{}f}'.format(n, precision)

    def __scanDataToLine(self, idx = -1):
        line = ''
        
        for i in range(len(self.getDevices())):
            line += ' ' if line != '' else ''
            try:
                dev = self.getDevices()[i]
                val = self.getDevicesData()[dev][idx]
                line += str(val)
            except:
                line += 'N/A'
            
        for i in range(len(self.getSignals())):
            line += ' ' if line != '' else ''
            try:
                sig = self.getSignals()[i]
                val = self.getSignalsData()[sig][idx]
                line += str(val)
            except:
                line += 'N/A'

        return line
