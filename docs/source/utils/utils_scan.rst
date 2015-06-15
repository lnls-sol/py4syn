
==============
Scan Functions
==============
So far Py4Syn can handle three scan types:

- Scan
   - All devices must have the same number of steps and they will step toguether. You can specify as many devices as you want, there's no limitation with this.
   - The only restriction is that the used devices must implement the IScannable interface. For more information about IScannable Interface please check :class:`py4syn.epics.IScannable`.


- Mesh   
   - No concern about devices number of steps. You can specify as many devices as you want.
   - The only restriction is that the used device must implement the IScannable interface. For more information about IScannable Interface please check :class:`py4syn.epics.IScannable`.

- Time
   - No devices, scan runs over time. User specify the counting time and delay time in seconds, both default to 1.
   

Handling the Data
=================
At Py4Syn all the scan data is stored in a memory dictionary in order to ensure great speed.
Data inside the **SCAN_DATA** dictionary is organized as follows:

+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Index               | Content                                                                                                                                                                 |
+=====================+=========================================================================================================================================================================+
| 'points'            | Array of points, [0, 1, 2, 3...N]                                                                                                                                       |
+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 'scan_object'       | Reference to the Scan object                                                                                                                                            |
+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| devices mnemonic    | For each device used in the scan an entry to store this device value across the scan is created, e.g. SCAN_DATA['tth'] represents the array of tth positions            |
+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| counters mnemonic   | For each counter registered an entry to store this device value across the scan is created, e.g. SCAN_DATA['mon'] represents the array of mon values                    |
+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 'scan_start'        | Timestamp of scan start                                                                                                                                                 |
+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 'scan_end'          | Timestamp of scan end                                                                                                                                                   |
+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 'scan_duration'     | Scan duration. ('scan_end' - 'scan_start')                                                                                                                              |
+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Any other user data | Any value you want, but beware that this values must be created using the :meth:`py4syn.utils.scan.createUserDefinedDataField` method in order to be saved in the file. |
+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Callbacks
=========

There are 7 callbacks available:

- **Pre Scan Callback**
   - This callback is executed at the beginning of the scan

- **Pre Point Callback**
   - This callback is executed before the point (before motors movement, or any other device setup)
   
- **Pre Operation Callback**
   - This callback is executed before the operation, before launching the counters
   
- **Operation Callback**
   - This is the main callback, it's executed while the counters are running

- **Post Operation Callback**
   - This callback is executed after the operation, after the counters stop and before the plot and screen update
    
- **Post Point Callback**
   - This callback is executed right after the operation callback and before a new movement
   
- **Post Scan Callback**
   -  This callback is executed at the end of the scan

If one wants to define specific callbacks it's possible by following the recipe below:

.. code-block:: python

   # Creating my function that will be executed in the choosen callback
   # This function needs to receive a parameter **kwargs
   def myCallback(**kwargs):
      scanObject = kwargs['scan']
      indexArray = kwargs['idx']  
      positionArray = kwargs['pos']
      print('Message from my callback')
   
   # This shows how to move back to the default callback from py4syn
   setPreScanCallback(defaultPreScanCallback)
      
   # Set my function to the operation callback
   setOperationCallback(mycallback)

   # Run the scan with the new configurations
   scan('m1', 0, 180, 10, 1)

.. attention:: 
   By overwriting an existing callback you assume that you will handle all the operations that you have overwritten. Also, user is responsible by the dead-time generated by the custom callbacks. 
   
Special variables in the Scan module
====================================
In the Scan module there are some **GLOBAL** variables that can be read and configured. To access this variables you can either use the scan module or the appropriate getter and setter methods.

+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| Variable                | Content                                                                                                              | Getter                     | Setter                     |
+=========================+======================================================================================================================+============================+============================+
| SCAN_DATA               | Ordered Dictionary that contains all scan related data                                                               | getScanData()              |                            |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| SCAN_CMD                | String with the last scan command executed                                                                           | getScanCommand()           |                            |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| SCAN_COMMENT            | String with a comment to be added to the scan file                                                                   | getScanComment()           | setScanComment()           |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| SCAN_PLOTTER            | Scan Object to be used when plotting data                                                                            | getScanPlotter()           | setScanPlotter()           |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| SCAN_PLOTTER_AXIS       | Axis index to be used in the plotter                                                                                 | getScanPlotterAxis()       | setScanPlotterAxis()       |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| FILENAME                | String that represents the filename to be used, if None stores only in memory. See `setOutput` for more information. | getOutput()                | setOutput()                |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| XFIELD                  | String that represents the Mnemonic of the X axis. See `setX` for more information.                                  | getX()                     | setX()                     |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| YFIELD                  | String that represents the Mnemonic of the Y axis. See `setY` for more information.                                  | getY()                     | setY()                     |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| FWHM                    | Double that represents the FWHM value.                                                                               | getFwhm()                  |                            |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| FWHM_AT                 | Double that represents the FWHM position.                                                                            | getFwhmAt()                |                            |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| COM                     | Double that represents the COM (Center of Mass) value.                                                               | getCom()                   |                            |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| PEAK                    | Double that represents the Peak value.                                                                               | getPeak()                  |                            |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| PEAK_AT                 | Double that represents the Peak position.                                                                            | getPeakAt()                |                            |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| MIN                     | Double that represents the Minimum value.                                                                            | getMin()                   |                            |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| MIN_AT                  | Double that represents the Minimum value position.                                                                   | getMinAt()                 |                            |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| FITTED_DATA             | Array that represents the best fit values.                                                                           | getFittedData()            |                            |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| FIT_RESULT              | ModelFit with fit result information.                                                                                | getFitResult()             |                            |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| FIT_SCAN                | Boolean that represents if we should or not fit the scan data at end. Default is `True`                              | getFitScan()               | setFitScan()               |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| PRINT_SCAN              | Boolean that represents if we should or not print to the terminal the scan information. Default is `True`            | getPrintScan()             | setPrintScan()             |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| PLOT_GRAPH              | Boolean that represents if we should or not create the real-time plot. Default is `True`                             | getPlotGraph()             | setPlotGraph()             |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| PRE_SCAN_CALLBACK       | Function pointer for the Pre Scan Callback. Default is `defaultPreScanCallback`.                                     | getPreScanCallback()       | setPreScanCallback()       |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| PRE_POINT_CALLBACK      | Function pointer for the Pre Point Callback. Default is `None`.                                                      | getPrePointCallback()      | setPrePointCallback()      |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| PRE_OPERATION_CALLBACK  | Function pointer for the Pre Operation Callback. Default is `None`.                                                  | getPreOperationCallback()  | setPreOperationCallback()  |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| OPERATION_CALLBACK      | Function pointer for the Operation Callback. Default is `defaultOperationCallback`.                                  | getOperationCallback()     | setOperationCallback()     |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| POST_OPERATION_CALLBACK | Function pointer for the Post Operation Callback. Default is `None`.                                                 | getPostOperationCallback() | setPostOperationCallback() |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| POST_POINT_CALLBACK     | Function pointer for the Post Point Callback. Default is `None`.                                                     | getPostPointCallback()     | setPostPointCallback()     |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+
| POST_SCAN_CALLBACK      | Function pointer for the Post Scan Callback. Default is `defaultPostScanCallback`                                    | getPostScanCallback()      | setPostScanCallback()      |
+-------------------------+----------------------------------------------------------------------------------------------------------------------+----------------------------+----------------------------+

Functions from the Scan module
==============================
.. automodule:: py4syn.utils.scan
   :synopsis: Utility to help Scan process for Scannable Devices.
   :members: