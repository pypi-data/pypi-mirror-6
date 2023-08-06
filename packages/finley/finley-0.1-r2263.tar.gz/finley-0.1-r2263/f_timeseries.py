#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extracts meta-data from MD trajectories. This tool comes with an powerful interpreter of reverse polish notation to represent complex system properties in a condensed way.

Reverse polish notation
-----------------------
A compact notation to express arbitrary mathematical operations while refraining from the extensive usage of braces is called the reverse polish notation. In general, it is a postfix syntax, that is, the operator is written after the operands. For example the first line becomes

.. code:: sh 

	(3 + 4) * (5 + 6) / 7
	3 4 + 5 6 + * 7 /

The list of the operands waiting to be consumed by an operator is called stack. Objects can be placed on the stack arbitrarily. However, this implementation requires you to end with a single entry on the stack. Each of the objects can be both a scalar and a vector.

Examples
--------

Suppose you have a molecule with three points of interest, which shall be called A, B, and C. You are interested in the angle of the vectors BA and CB with the z-axis and the angle between these two vectors. Then the following lines will give you three angles in radians per frame.

.. code:: sh

	f_timeseries.py input.psf input.dcd --periodic  \\
		--cmd 'selection A:com; selection B:com;diff;0,0,1;angle' \\
		--cmd 'selection B:com; selection C:com;diff;0,0,1;angle' \\
		--cmd 'selection A:com; selection B:com;diff;selection B:com; selection C:com;diff;angle'

Shortcuts
---------
Sometimes a command will be used frequently. Hence, there are shortcuts in this case. The following shortcuts are available. Each time, the two lines are identical.

.. code:: sh

	# prints the side lengths (x, y, z) of the unit cell
	box
	boxdimen;1,1,1,0,0,0;mask;3;pile

Supported formats
-----------------

All file formats of :ref:`MDAnalysis <supported coordinate formats>` are supported. Input files may be compressed using gzip or bzip2.

.. note:: File formats are recognized by file extension. Therefore, you have to stick to the standard file extensions.

.. warning:: Only rectangular simulation boxes are currently supported.

.. todo:: Guess input file format.

Command line interface
----------------------

.. program:: f_timeseries.py

.. option:: topology

   The topology file to work with. 

.. option:: coordinates

   The coordinate file to work with.

.. option:: --frames

   The zero-based frame selection that allows for slicing. The general syntax is 'start:stop:step' which would select all frames from `start` to `stop` (excluding `stop`) while skipping `step` frames inbetween. Selecting single frames by specifying a single number is possible. Negative indices count backwards from the end of the trajectory.

.. option:: --periodic

   Whether to wrap atoms for spatial selection criteria back to the original cell.

.. option:: --indexfile

   Files that contain named groups of atoms based on their indices. Files have to be in GROMACS ndx-Format. Can be used multiple times.

.. option:: --cmd

   String concatenating the operators using reverse polish notation together with atom selectors. This command can be issued multiple times on the command line. Every option will result in an additional entry printed in the resulting line per frame. The general notation is

   .. code:: sh 

   		selection:cmd;selection2:cmd2

   There are some operators that do not support selections. They are meant to be used this way

   .. code:: sh

   		:cmd;:cmd2

   You can put elements on the stack by yourself. They have to be numeric, but can be either a comma-separated vector or a scalar. The selection syntax is decribed separately. Please refer to the :ref:`section <atomselections>` on atom selections. The available operators are

   * `com` calculates the center of mass of the given selection. If the selection is empty, the center of mass of all atoms in the whole system is calculated. The result is a vector in cartesian coordinates. `com` does not consume any stack elements but rather adds another one.

   .. code:: sh

   		id 1-10:com

   * `dist` calculates the distance between two points in cartesian coordinates. The last two stack elements will be consumed and have to be vectors. The resulting scalar is put back on the stack. This operator does not support selections.

   .. code:: sh

   		1,1,1; 2,2,2; dist
   		id 1-10:com; id 11-20:com; dist

   * `diff` calculates the difference of the two last stack entries which only have to be of the same dimension. This operator does not support selections.

   .. code:: sh

   		3;4;diff
   		id 1-10:com; id 11-20:com; diff

   * `framenum` prints the number of the current frame in the trajectory. Selections are not supported. Please keep in mind that this frame number does not necessarily correspond with a simulation step and that the indices are zero-based.

   .. code:: sh

   		framenum

   * `boxdimen` puts the system box dimensions on the stack. The unit cell is defined by six elements: the length of the x, y, and z vector and the angles inbetween (alpha, beta, and gamma).

   .. code:: sh

   		boxdimen

   * `mask` discards some of the elements on the stack. The last element of the stack has to be a vector which is to be aligned with the end of the stack. Only stack elements with a non-zero mask entry are kept. For example, if you are intested in the x and y axis of the box dimensions only, you may use:

   .. code:: sh

   		boxdimen;1,1,0,0,0,0;mask

   * `prod` calculates the product of the last two stack elements.
   * `frac` calculated the quotient of the last two stack elements. Please note that the last stack element is the numerator.
   * `sum` adds the last two stack elements.
   * `flatten` takes a single vector from the stack and pushes its elements back.
   * `charge` calculates the charge density profile along a given vector. This command calculates the charge density of all molecules that do not belong to a residue named UNK from 0 to 60 Angstroms along the 0,0,1 vector using 100 bins. The result is pushed onto the stack as a vector that has as many elements as bins were used. 

   .. code:: sh

   		0,60;100;0,0,1;not resname UNK:charge

   * `fitplane` fits a plane to the atom coordinates of the given selection. The normalized normal vector of the plane is pushed onto the stack.

   .. code:: sh

   		type PL:fitplane

   .. note:: 

   		The algorithm used is Singular Value Decomposition. Please make sure that you only have only atoms for one plane as multiple parallel planes in the underlying structure will lead to spurious errors.

   * `pile` takes the last element on the stack and inteprets it as number of elements to transform into a vector. The resulting vector is pushed onto the stack. The following would print the simulation cell dimensions.

   .. code:: sh

   		boxdimen;1,1,1,0,0,0;mask;3;pile


Internal functions
------------------
"""

# system modules
import argparse
import math

# custom modules
import f_core as fc
import output_tracker as ot

# third-party modules
import numpy as np

# command line parsing
parser = argparse.ArgumentParser(description='Calculates collective properties from MD trajectories.')
parser.add_argument('topology', type=str, help='The topology to work with.')
parser.add_argument('coordinates', type=str, help='The coordinates to work with.')
parser.add_argument('--frames', type=str, help='Frame selection.', default='')
parser.add_argument('--periodic', help='Whether to wrap atoms for spatial selection criteria back to the original cell.', action='store_true')
parser.add_argument('--cmd', type=str, help='Command that will produce output.', action='append')
parser.add_argument('--indexfile', type=str, nargs='+', help='GROMACS style index file for named groups.')

def _operator_com(selection, universe, output):
	"""
	Reverse polish notation operator that calculates the center of mass.

	Parameters
	----------
	selection : String
		The CHARMM-style selection request. May contain atom ids, as well.
	universe : :class:`mda:MDAnalysis.core.AtomGroup.Universe` 
		The universe which trajectory is to be analyzed.
	output : :class:`output_tracker` instance
	  Error reporting.

	Returns
	-------
	numpy.array 
		Center of mass in cartesian coordinates. Length unit is Angstrom.
	"""
	ag = fc.mda_select_id(universe, selection, output)

	if len(ag) == 0:
		output.print_error(fc.messages.EMPTY_SELECTION)

	return ag.centerOfMass()

def _dump_stack(stack, output):
	"""
	Lists the current stack elements.

	Parameters
	----------
	stack : iterable
		The current stack.
	output : :class:`output_tracker` instance
	  Error reporting.	
	"""
	output.print_info('Stack elements:').add_level()
	for s in stack:
		output.print_info('%s' % str(s))
	output.del_level()

def _require_stack_length(stack, length, output):
	"""
	Takes the requested number of elements from the stack.

	Parameters
	----------
	stack : iterable
		The current stack.
	length : int
		The number of elements to take from the end of the stack.
	output : :class:`output_tracker` instance
	  Error reporting.

	Returns
	-------
	tuple
		Tuple of length two with iterables: the new stack and the popped entries.
	"""
	if len(stack) < length:
		_dump_stack(stack, output)
		output.print_info('Stack size %d' % len(stack))
		output.print_error(fc.messages.STACK_POP)

	return (stack[:-length], stack[-length:])

def _operator_dist(stack, output):
	"""
	Reverse polish notation operator that calculates the distance between the last two stack elements.

	Parameters
	----------
	stack : iterable
		The current stack.
	output : :class:`output_tracker` instance
	  Error reporting.	

	Returns
	-------
	iterable
		The new stack.
	"""
	stock, arguments = _require_stack_length(stack, 2, output)
	arg1, arg2 = arguments

	if len(arg1) != 3 or len(arg2) != 3:
		output.print_error(fc.messages.STACK_DIMENSION)

	dist = math.sqrt(sum([(a-b)**2 for a, b in zip(arg1, arg2)]))

	stock.append(dist)
	return stock

def _operator_diff(stack, output):
	"""
	Reverse polish notation operator that calculates the difference between the last two stack elements.

	Parameters
	----------
	stack : iterable
		The current stack.
	output : :class:`output_tracker` instance
	  Error reporting.	

	Returns
	-------
	iterable
		The new stack.
	"""	
	stock, arguments = _require_stack_length(stack, 2, output)
	arg1, arg2 = arguments

	if len(arg1) != len(arg2):
		output.print_error(fc.messages.DIM_MISMATCH)

	diff = [a-b for a, b in zip(arg1, arg2)]

	if len(diff) == 1:
		stock.append(diff[0])
	else:
		stock.append(diff)
	return stock

def _operator_angle(stack, output):
	"""
	Reverse polish notation operator that calculates the angle between the last two stack elements.

	The last two stack elements have to be a vector.

	Parameters
	----------
	stack : iterable
		The current stack.
	output : :class:`output_tracker` instance
	  Error reporting.	

	Returns
	-------
	iterable
		The new stack.
	"""
	stock, arguments = _require_stack_length(stack, 2, output)
	arg1, arg2 = arguments

	if len(arg1) != 3 or len(arg2) != 3:
		output.print_error(fc.messages.STACK_DIMENSION)

	phi = fc.angle(arg1, arg2, output)
	stock.append(phi)
	return stock

def _operator_boxdimen(stack, universe, framenum, output):
	"""
	Reverse polish notation operator that puts the simulation box dimensions on the stack.

	Parameters
	----------
	stack : iterable
		The current stack.
	universe : :class:`mda:MDAnalysis.core.AtomGroup.Universe` 
		The universe which trajectory is to be analyzed.
	framenum : Integer
		Current frame number. One-based.
	output : :class:`output_tracker` instance
	  Error reporting.
	"""
	stack += list(universe.trajectory[framenum-1].dimensions)
	return stack

def _operator_mask(stack, output):
	"""
	Reverse polish notation operator that filters amongst the last stack elements.

	Parameters
	----------
	stack : iterable
		The current stack.
	output : :class:`output_tracker` instance
	  Error reporting.	

	Returns
	-------
	iterable
		The new stack.
	"""
	stock, mask = _require_stack_length(stack, 1, output)
	
	l = len(mask[0])
	stock, arguments = _require_stack_length(stock, l, output)
	keep = [val for mask, val in zip(mask[0], arguments) if mask != 0]
	stock += keep
	return stock

def _operator_prod(stack, output):
	"""
	Reverse polish notation operator that calculates the product of the last two stack elements.

	Parameters
	----------
	stack : iterable
		The current stack.
	output : :class:`output_tracker` instance
	  Error reporting.	

	Returns
	-------
	iterable
		The new stack.	
	"""
	stock, arguments = _require_stack_length(stack, 2, output)
	arguments = map(np.array, arguments)

	try:
		res = arguments[0]*arguments[1]
	except:
		output.print_error(fc.messages.STACK_DIMENSION)

	stock.append(res)
	return stock

def _operator_sum(stack, output):
	"""
	Reverse polish notation operator that calculates the sum of the last two stack elements.

	Parameters
	----------
	stack : iterable
		The current stack.
	output : :class:`output_tracker` instance
	  Error reporting.	

	Returns
	-------
	iterable
		The new stack.	
	"""
	stock, arguments = _require_stack_length(stack, 2, output)
	arguments = map(np.array, arguments)

	try:
		res = arguments[0]+arguments[1]
	except:
		output.print_error(fc.messages.STACK_DIMENSION)

	stock.append(res)
	return stock

def _operator_frac(stack, output):
	"""
	Reverse polish notation operator that calculates the quotient of the last two stack elements.

	Note that the last stack element is treated as numerator.

	Parameters
	----------
	stack : iterable
		The current stack.
	output : :class:`output_tracker` instance
	  Error reporting.	

	Returns
	-------
	iterable
		The new stack.	
	"""
	stock, arguments = _require_stack_length(stack, 2, output)
	arguments = map(np.array, arguments)

	try:
		res = arguments[1]/arguments[0]
	except:
		output.print_error(fc.messages.STACK_DIMENSION)

	stock.append(res)
	return stock

def _operator_charge(stack, selection, universe, framenum, output):
	"""
	Reverse polish notation operator that calculates the charge density profile.	

	.. note:: 
		Only works correctly for charge density profiles along the z axis.

	.. todo::
		Implement vector choice.

	Parameters
	----------
	stack : iterable
		The current stack.
	selection : String
		The CHARMM-style selection request. May contain atom ids, as well.
	universe : :class:`mda:MDAnalysis.core.AtomGroup.Universe` 
		The universe which trajectory is to be analyzed.
	framenum : Integer
		Current frame number. One-based.
	output : :class:`output_tracker` instance
	  Error reporting.	

	Returns
	-------
	iterable
		The new stack.	
	"""
	stock, arguments = _require_stack_length(stack, 3, output)
	bounds, numbins, projection = arguments
	numbins = int(numbins[0])
	minval = min(bounds)
	maxval = max(bounds)
	projection = np.array(projection)

	if len(projection) != 3:
		output.print_error(fc.messages.STACK_DIMENSION)
	# TODO: test for null vector
	# TODO: more checks on input values

	ag = fc.mda_select_id(universe, selection, output)

	bindata = [0]*numbins
	binwidth = (maxval-minval)/numbins
	dimensions = universe.trajectory[framenum].dimensions

	# TODO: more general formula
	area = dimensions[0]*dimensions[1]
	for atom in ag:
		intvar = projection.dot(atom.pos)
		if intvar < minval or intvar > maxval:
			continue

		bin = int(min(intvar % numbins, numbins-1))
		bindata[bin] += abs(atom.charge)/(area*binwidth)

	stock.append(bindata)
	return stock

def _operator_fitplane(stack, selection, universe, framenum, output):
	"""
	Reverse polish notation operator that fits a plane to coordinates.

	Parameters
	----------
	stack : iterable
		The current stack.
	selection : String
		The CHARMM-style selection request. May contain atom ids, as well.
	universe : :class:`mda:MDAnalysis.core.AtomGroup.Universe` 
		The universe which trajectory is to be analyzed.
	framenum : Integer
		Current frame number. One-based.
	output : :class:`output_tracker` instance
	  Error reporting.	

	Returns
	-------
	iterable
		The new stack.	
	"""
	fc.mda_patch_parser()
	ag = fc.mda_select_id(universe, selection, output)
	if len(ag) == 0:
		output.print_error(fc.messages.EMPTY_SELECTION)
	if len(ag) < 3:
		output.print_info('Selected %d atoms.' % len(ag))
		output.print_error(fc.messages.UNDEF_PLANE)
	orig_pos = ag.get_positions(ts=universe.trajectory[framenum])
	pos = orig_pos - sum(orig_pos)/len(orig_pos)
	
	# calculate plane
	rows, cols = pos.shape
	p = np.ones((rows, 1))
	AB = np.hstack([pos, p])
	u, d, v = np.linalg.svd(AB, True)
	B = v[3,:]
	nn = np.linalg.norm(B[0:3])
	B = B / nn
	
	# output
	stack.append(B[0:3])
	return stack

def _operator_flatten(stack, output):
	"""
	Reverse polish notation operator that puts every element of an vector on the stack separately.

	Parameters
	----------
	stack : iterable
		The current stack.
	output : :class:`output_tracker` instance
		Error reporting.	

	Returns
	-------
	Iterable
		The new stack.		
	"""
	stock, arguments = _require_stack_length(stack, 1, output)

	try:
		l = len(arguments[0])
	except:
		output.print_error(fc.messages.STACK_DIMENSION)

	for e in arguments[0]:
		stock.append(e)

	return stock

def _operator_pile(stack, output):
	"""
	Reverse polish notation operator that joins elements on the stack info one single vector.

	Parameters
	----------
	stack : Iterable
		The current stack.
	output : :class:`output_tracker` instance
		Error reporting.

	Returns
	-------
	Iterable
		The new stack.
	"""

	stock, arguments = _require_stack_length(stack, 1, output)

	try:
		num_elements = int(arguments[0])
	except:
		output.print_info('Got %s.' % arguments[0])
		output.print_error(fc.messages.INT_CONVERSION)

	if num_elements < 0:
		output.print_info('Got %d.' % num_elements)
		output.print_error(fc.messages.NEGATIVE_LENGTH)

	stock, arguments = _require_stack_length(stock, num_elements, output)

	stock.append(np.array(arguments))

	return stock

def _execute(columns, command, framenum, universe, output):
	"""
	Reverse polish notation parser.

	Parameters
	----------
	columns : iterable
		Output of former :option:`--cmd` arguments.
	command : String
		Current request in reverse polish notation to execute.
	framenum : Integer
		Current frame number. One-based.
	universe : :class:`mda:MDAnalysis.core.AtomGroup.Universe` 
		The universe which trajectory is to be analyzed.
	output : :class:`output_tracker` instance
	  Error reporting.

	Returns
	-------
	iterable
		Results of all :option:`--cmd` requests processed so far.
	"""
	parts = [_.strip() for _ in command.split(';')]
	stack = []

	# shortcuts
	while 'box' in parts:
		idx = parts.index('box')
		parts = parts[0:idx] + 'boxdimen;1,1,1,0,0,0;mask;3;pile'.split(';') + parts[idx+1:]

	# commands
	for part in parts:
		temp = [_.strip() for _ in part.split(':')]
		if len(temp) == 1:
			if temp[0] == 'framenum':
				stack.append(framenum-1)
			elif temp[0] == 'dist':
				stack = _operator_dist(stack, output)
			elif temp[0] == 'diff':
				stack = _operator_diff(stack, output)
			elif temp[0] == 'angle':
				stack = _operator_angle(stack, output)
			elif temp[0] == 'prod':
				stack = _operator_prod(stack, output)
			elif temp[0] == 'sum':
				stack = _operator_sum(stack, output)
			elif temp[0] == 'frac':
				stack = _operator_frac(stack, output)
			elif temp[0] == 'flatten':
				stack = _operator_flatten(stack, output)
			elif temp[0] == 'pile':
				stack = _operator_pile(stack, output)
			elif temp[0] == 'mask':
				stack = _operator_mask(stack, output)
			elif temp[0] == 'boxdimen':
				stack = _operator_boxdimen(stack, universe, framenum, output)
			else:
				try:
					data = [float(_) for _ in temp[0].split(',')]
					if len(data) == 1 and ',' not in temp[0]:
						# scalar pushed onto the stack
						stack.append(data[0])
					else:
						# vector intended by the user
						stack.append(data)
				except:
					output.print_info('Got operator %s.' % temp[0])
					output.print_error(fc.messages.UNKNOWN_CMD)
		elif len(temp) == 2:
			selection, operator = temp
			if operator == 'com':
				stack.append(_operator_com(selection, universe, output))
			elif operator == 'charge':
				stack = _operator_charge(stack, selection, universe, framenum, output)
			elif operator == 'fitplane':
				stack = _operator_fitplane(stack, selection, universe, framenum, output)
			else:
				output.print_info('Got operator %s.' % operator)
				output.print_error(fc.messages.UNKNOWN_CMD)
		else:
			output.print_info('Got command %s' % command)
			output.print_error(fc.messages.TERNARY_CMD)

	if len(stack) != 1:
		_dump_stack(stack, output)
		output.print_info('Command:').add_level()
		output.print_info(command)
		output.del_level().print_error(fc.messages.NOT_CONSUMED)

	return columns + stack

def main():
	"""
	Main wrapper.
	"""
	# messages
	output = ot.output_tracker()
	messages = fc.messages

	# init
	mda = fc._require_mda(output)
	args = parser.parse_args()

	# read input files
	output.print_info('Reading source files.').add_level()
	output.print_info('Opening file %s.' % args.topology)
	output.print_info('Opening file %s.' % args.coordinates)

	# create Universe
	fc.mda_set_periodic(args.periodic, output)
	u = fc.mda_load_universe(args.topology, args.coordinates, output)
	output.print_info('Coordinate file holds %d frames.' % len(u.trajectory)).del_level()

	# parse selection
	f_sel = fc.parse_frame_selection(args.frames, output)
	groups = fc.parse_indexfiles(args.indexfile, output)
	u.add_index_groups(groups)

	# analyze trajectory
	try:
		l = len(args.cmd)
	except:
		output.print_error(messages.NO_CMD)
	for ts in u.trajectory[f_sel]:
		columns = []

		for cmd in args.cmd:
			columns = _execute(columns, cmd, u.trajectory.frame, u, output)

		for col in columns:
			try:
				l = len(col)
			except:
				print col,
				continue
			for e in col:
				print e,
		print

if __name__ == '__main__':
	main()
	exit(2)
