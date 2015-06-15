
==============
Default Writer
==============

.. module:: py4syn.writing.DefaultWriter
   :synopsis: Python class to generate PyMCA/SPEC-like file output

The default writer class is responsible for generating the Py4Syn PyMCA/SPEC-like output.

Bellow it's possible to check an example of the generated file:

.. code::

   #E 1423501786
   #D Mon Feb 09 15:09:46 2015
   #C py4syn User = hugo.slepicka
   #C0 Comment 1
   #C1 Comment 2
   #C2 Comment 3
   #S 1 python3.4 test.py
   #D Mon Feb 09 15:09:44 2015
   #N 2
   #L dev-1  signal-1
   88 0.579816377007323
   55 0.7587818137112776
   84 0.42957633904075676
   84 0.553745066476392
   87 0.14826338543188655
   75 0.968795965439634
   20 0.26124651064977344
   66 0.5235828320576064
   94 0.3908435592403231
   95 0.5678979857080083

Using the Default File Writer module
====================================

.. autoclass:: DefaultWriter
   :members: