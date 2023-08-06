Common information
==================

.. _atomselections:

Atom selections
---------------

You may either select atoms using a subset of the CHARMM selection commands or by specifying (zero-based) atom ids. Please refer to the complete list of :ref:`mda:selection-commands-label`.

For the atom ids, which are defined as the order of occurrence of the atom in the topology file, there are several options. You can give a list of numbers or ranges separated by commas or spaces or a mixture of both. Repeated indices are ignored. This arguments would be perfectly valid:

.. code:: sh

	id 1,2,3, 6-8,1-5

You may also use python style range selections `start:stop:step`. In this case, `stop` will not be included. The following selections are identical.

.. code:: sh

	id 1:10:2
	id 1,3,5,7,9
	id 1-3, ^2, 5, 7-9, ^8

Spaces in this slice syntax are not allowed. To exclude atoms from the selection, prefix their ids with a caret. For example, these two specifications are identical.

.. code:: sh

	id 1-10,^2-5,4
	id 1,4,6-10

The list is built in order. Therefore, the last occurrence has precedence.

.. note:: 
	When mixing id selection commands with regular MDAnalysis selection commands, spaces are not allowed.

For those commands that accept the :option:`--indexfile` option, you may also use named groups from GROMACS-style index files. If you want to select the union of multiple groups, you can give a comma-separated list that is not allowed to contain spaces. If your index file looks like

.. code:: sh

	[ group_A ]
	1, 2, 4
	[ group_B ]
	1, 2, 3

then all of the following selection commands would yield identical results

.. code:: sh
	
	groups group_A,group_B
	groups group_A or groups group_B
	id 1-4,^3,1-3
	id 1-4

f_core
------

Common functions of the finley toolkit.

.. automodule:: f_core
   :members:
   :private-members:
   :special-members:
   :undoc-members:
