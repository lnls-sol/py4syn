"""
EPICS Digital I/O

Python Class for EPICS Digital I/O control.

:platform: Unix
:synopsis: Python Class for Digital I/O control using EPICS.

.. moduleauthor:: Laís Pessine do Carmo <lais.carmo@lnls.br>
	.. note:: 12/04/2016 [lais.carmo]  First version released.
	.. note:: 15/04/2016 [lais.carmo]  Internal methods as '__private'; __getPortNumbers() added.

"""

from epics import PV

class ErrorPortSequence(Exception):
	"""
	Exception raised when the given port sequence is invalid.
	"""
	def __init__(self, port_sequences):
		self.arg = port_sequences
	def __str__(self):
		return "ERROR: Port sequence parameter '" + str(self.args) + "' is not valid. \nTIP: ';' and '-' can be used to define a port sequence. Example: '0-3;5;10-15'"

class ErrorPortType(Exception):
	"""
	Exception raised when the given port type is not 'INPUT' neither 'OUTPUT'.
	"""
	def __init__(self):
		pass
	def __str__(self):
		return str("Port type must be 'INPUT' or 'OUTPUT'.")

class ErrorIndexNotFound(Exception):
	"""
	Exception raised when the port index in not found'.
	"""
	def __init__(self, port_index):
		self.arg = port_index
	def __str__(self):
		return str("Port index " + str(self.arg) + " not found.")
		
class ErrorInputAssignment(Exception):
	"""
	Exception raised when it is tried to assign a value to port of type 'INPUT'.
	"""
	def __init__(self):
		pass
	def __str__(self):
		return str("Cannot assign a value to an INPUT port (read only).")

		
class DigitalIO(object):
	"""
	Class for Digital I/O using EPICS.

	Example:
    --------
    >>> from py4syn.epics.DigitalIOClass import DigitalIO
    >>> ports_out = DigitalIO('SOL3:DIO:bo', 'OUTPUT', '0-3;7')
    >>> ports_out.list()
	... SOL3:DIO:bo0
	... SOL3:DIO:bo1
	... SOL3:DIO:bo2
	... SOL3:DIO:bo3
	... SOL3:DIO:bo7
    >>> ports_out.getValue(3)
	...	0
	>>> ports_out.putValue(3,1)
	>>> ports_out.getValue(3)
	... 1
	>>> ports_out.addPorts('5-6')
	>>> ports_out.list()
	... SOL3:DIO:bo0
	... SOL3:DIO:bo1
	... SOL3:DIO:bo2
	... SOL3:DIO:bo3
	... SOL3:DIO:bo5
	... SOL3:DIO:bo6
	... SOL3:DIO:bo7
	>>> ports_out.deletePorts('3')
	>>> ports_out.list()
	... SOL3:DIO:bo0
	... SOL3:DIO:bo1
	... SOL3:DIO:bo2
	... SOL3:DIO:bo5
	... SOL3:DIO:bo6
	... SOL3:DIO:bo7
	>>> ports_out.getName(2)
	... 'SOL3:DIO:bo2'

	"""

	def __init__(self, digitalIO_prefix, port_type, port_sequence):
		"""
        **Constructor**

        Parameters
        ----------
        digitalIO_prefix : `string`
            Prefix of the ports.

        port_type : `string`
            'INPUT' or 'OUTPUT'.

        port_sequence : `string`
            Index of the ports. Example: '0-3;7' means ports from 0 to 3 and 7.
        """

		self.digitalIO_prefix = None
		
		if port_type == 'INPUT' or port_type == 'OUTPUT':
			self.port_type = port_type
		else:
			raise ErrorPortType()
		
		self.port_name_dict = {}
		self.port_pv_dict = {}

		self.digitalIO_prefix = digitalIO_prefix
		self.addPorts(port_sequence)

	def getValue(self, port_index):
		"""
        Returns the current value of a port PV.

        Parameters
        ----------
		port_index : `int`
            Index of the port.
        """

		port_index = int(port_index)
		
		if port_index not in self.port_name_dict.keys():
			raise ErrorIndexNotFound(port_index)

		return self.port_pv_dict[port_index].get()

	def putValue(self, port_index, new_value):
		"""
        Set a new value for a port PV.

        Parameters
        ----------
		port_index : `int`
            Index of the port.

        new_value
        	New value of the port PV.
        """

		port_index = int(port_index)
		
		if port_index not in self.port_name_dict.keys():
			raise ErrorIndexNotFound(port_index)
		
		if self.port_type == 'OUTPUT':
			self.port_pv_dict[port_index].put(new_value);
		else:
			raise ErrorInputAssignment()

	def list(self):
		"""
        Lists name of all ports in use.
        """

		for k in self.port_name_dict.keys():
			print(self.port_name_dict[k])

	def getName(self, port_index):
		"""
        Returns the name of a port PV.

        Parameters
        ----------
		port_index : `int`
            Index of the port.
        """

		port_index = int(port_index)

		if port_index not in self.port_name_dict.keys():
			raise ErrorIndexNotFound(port_index)

		return self.port_name_dict[port_index]

	def __getPortNumbers(self, port_sequences):
		"""
		Receive a sequece of ports and return an integer array with all port numbers.

		Parameters
		----------
		port_sequences : `string`
		    Sequences of port indexes.

		Returns
		----------
		port_sequence_array : `int`
		    Array of all port numbers.
		"""

		try:
			port_sequences = str(port_sequences)
			port_sequence = port_sequences.split(';')
			port_sequence_array = []

			for p in port_sequence:
				if len(p.split('-')) >= 1:
					port_init = p.split('-')[0]
					port_final = port_init	
				if len(p.split('-')) == 2:
					port_final = p.split('-')[1]

				for x in range(int(port_init),int(port_final)+1):
					port_sequence_array.append(x) 

			return port_sequence_array

		except:
			raise ErrorPortSequence(port_sequences)


	def __setPortNames(self, port_sequences):
		"""
        Set a dictionary with all port names (based on given prefix and port indexes).

        Parameters
        ----------
		port_sequences : `string`
            Index of the ports.
        """
		try:
			port_numbers = self.__getPortNumbers(port_sequences)

			for pn in port_numbers:
				self.port_name_dict[pn] = self.digitalIO_prefix + str(pn)
		except:
			raise ErrorPortSequence(port_sequences)

	def __setPortPVs(self):
		"""
        Set a dictionary with all port PVs (based on prefix and port indexes).
        """
		for x in self.port_name_dict.keys():
			if x not in self.port_pv_dict.keys():
				port_name = self.port_name_dict[x]
				port_pv = PV(port_name)
				self.port_pv_dict[x] = port_pv

	def addPorts(self, port_sequences):
		"""
        Add ports to name and PVs dictionaries.

        Parameters
        ----------
		port_sequences : `string`
            Index of the ports to be added.
        """
		self.__setPortNames(port_sequences)
		self.__setPortPVs()

	def deletePorts(self, port_sequences):
		"""
        Delete ports from name and PVs dictionaries.

        Parameters
        ----------
		port_sequences : `string`
            Index of the ports to be deleted.
        """
		try:
			port_sequences = str(port_sequences)
			port_numbers = self.__getPortNumbers(port_sequences)
			
			for pn in port_numbers:
				if pn in self.port_name_dict.keys():
					del self.port_name_dict[pn]
				if pn in self.port_pv_dict.keys():
					del self.port_pv_dict[pn]
		except:
			raise ErrorPortSequence(port_sequences)