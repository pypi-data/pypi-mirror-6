#!/usr/bin/env python
# -*- coding: utf-8 -*-

# system modules
import codecs
import copy
import datetime
import logging
try:
	logging.captureWarnings(True)
except:
	pass # < python 2.7
import math
import re

# custom modules
import atom
import colorexcept
import output_tracker as ot

# third-party modules
try:
	import MDAnalysis as mda
	HAS_MDA = True
except ImportError:
	HAS_MDA = False
import numpy as np
import numpy.linalg as npl

class messages(object):
	"""
		Error and warning messages. Used to make error codes unique throughout all tools of the finley toolkit.
	"""
	IMPORT_FAILED 		= (1, 'Unable to import topology and coordinate files.')
	NO_SLICE 			= (2, 'Slice indices have to be either integers or have to be of zero-length.')
	SLICE_START_RANGE 	= (3, 'Slice start selects frames that are not part of the source trajectory.')
	SLICE_STOP_RANGE 	= (4, 'Slice stop selects frames that are not part of the source trajectory.')
	NO_FRAME 			= (5, 'No frame selected.')
	OUTPUT_EXISTS 		= (6, 'Output file already exists.')
	CHARMM_SELECTION 	= (7, 'Unable to parse CHARMM selection.')
	OUTPUT_FAILED		= (8, 'Unable to write to output file.')
	INVALID_FRAME_SEL 	= (9, 'Frame not within trajectory.')
	MANUAL_SEEK			= (10, 'Performing stepwise seek in file for frame selection.')
	SEEK_PAST_FILE		= (11, 'End of file occurred during seeking. File may be corrupted.')
	MDA_DEP				= (12, 'MDAnalysis is required for this routine. You may continue after its installation.')
	UNKNOWN_LENGTH		= (13, 'Unable to estimate the total length of a trajectory.')
	EMPTY_SELECTION		= (14, 'No atoms selected.')
	INT_CONVERSION 		= (15, 'Could not convert data to integer.')
	SELECT_FAILED 		= (16, 'Unable to select requested atoms.')
	NEGATIVE_ATOM_NUM 	= (17, 'No negative atom numbers supported.')
	RANGE_ATOM_NUM 		= (18, 'Atom number is out of range.')
	NO_DUPLICATE 		= (19, 'All atom numbers in the selection have to be unique.')
	ORIGIN_LENGTH 		= (20, 'Origin has to be tuple of length three.')
	INVALID_ORIGIN 		= (21, 'Cannot parse specified origin.')
	NO_CMD				= (22, 'You have to specify at least one command to get any output.')
	TERNARY_CMD			= (23, 'All commands require at most two colon-separated sections, got more.')
	NOT_CONSUMED		= (24, 'RPN stack not fully consumed. Perhaps you left out an operator.')
	UNKNOWN_CMD			= (25, 'Unknown command.')
	REVERSE_BOUNDS		= (26, 'Reverse bounds for range.')
	STACK_POP			= (27, 'Stack does not hold enough elements for this operator.')
	STACK_DIMENSION		= (28, 'Elements on stack have wrong dimension for this operator.')
	DIM_MISMATCH		= (29, 'Elements have mismatching dimensions.')
	DASH_RANGE_NONNEG	= (30, 'Negative indices not supported for dash range syntax.')
	DASH_RANGE_SYNTAX	= (31, 'Syntax error for dash range selection.')
	NO_NULL_VECTOR		= (32, 'Null vectors are not allowed for this operation.')
	BOUNDS_REVERSED 	= (33, 'Lower limit is higher than the upper one.')
	BOUNDS_EQUAL		= (34, 'Lower and upper limits are identical.')
	BIN_COUNT_LEQ_Z		= (35, 'Number of bins has to be at least one.')
	EMPTY_LINE			= (36, 'Empty or ill-formatted input line.')
	CONVERT_FAILED		= (37, 'Got non-numeric data.')
	OUT_OF_BOUNDS		= (38, 'Data out of bounds.')
	BOUNDS_DIMENSION	= (39, 'Bound specification has to have the same dimension as the input data.')
	BOUNDS_IGNORED		= (40, 'Bound specification ignored.')
	BINS_2D_SPEC		= (41, 'Bins for the x axis and the y axis for 2D data have to be separated by a semicolon.')
	BINS_SORTED			= (42, 'Bins were not sorted.')
	UNDEF_PLANE			= (43, 'At least three points in space required for plane definition.')
	NOT_EXIST			= (44, 'File does not exist or is not readable.')
	IDX_SYNTAX_ERROR	= (45, 'GROMACS-style index file has syntax errors.')
	IDX_EMPTY_GROUP		= (46, 'GROMACS-style index file has empty index group name.')
	IDX_GROUP_SPACE		= (47, 'GROMACS-style index file has index group name containing whitespace.')
	IDX_MINVAL			= (48, 'GROMACS-style index files do not allow for indices lower than 1.')
	IDX_GROUP_OVERRIDE	= (49, 'Multiple definition of index group.')
	NEGATIVE_LENGTH		= (50, 'Unable to accept negative length specification.')


def _parse_indexfile(lines, groups, output):
	"""
	Graceful parser for GROMACS-style index files. In GROMACS, atom numbering is one-based. This routine works only on one-based indices.

	Parameters
	----------
	lines : List of strings
		Input lines of the file
	groups : Dictionary
		Group data like the return format of this function.
	output : :class:`output_tracker` instance
		Error reporting.

	Returns
	-------
	Dictionary
		Keys are case-sensitive group names as strings. Values are lists of integers. 
	"""
	groupname = None
	groupnumbers = set()

	def _append_group(groupname, groups, output, groupnumbers):
		if groupname in groups:
			output.print_error(messages.IDX_GROUP_OVERRIDE)
		groups[groupname] = groupnumbers
		return None, set()

	for line in lines:
		line = line.strip()
		if len(line) == 0:
			continue

		if line.startswith('['):
			if groupname is not None:
				groupname, groupnumbers = _append_group(groupname, groups, output, groupnumbers)
			if not line[-1] == ']':
				output.print_error(messages.IDX_SYNTAX_ERROR)
			groupname = line[1:-1].strip()
			if len(groupname) == 0:
				output.print_error(messages.IDX_EMPTY_GROUP)
			if ' ' in groupname or '\t' in groupname:
				output.print_error(messages.IDX_GROUP_SPACE)
		else:
			if groupname is None:
				output.print_error(messages.IDX_SYNTAX_ERROR)
			parts = line.split()
			try:
				parts = map(int, parts)
			except:
				output.print_info('Parsing line: %s' % line)
				output.print_error(messages.INT_CONVERSION)
			for part in parts:
				if part < 1:
					output.print_info('Got %d' % part)
					output.print_error(messages.IDX_MINVAL)
			groupnumbers = groupnumbers.union(set(parts))

	if groupname is not None:
		_append_group(groupname, groups, output, groupnumbers)
	return groups

def parse_indexfiles(filenames, output):
	"""
	Graceful parser of GROMACS-style index files.

	Parameters
	----------
	filenames : List of strings
		Input filenames.
	output : :class:`output_tracker` instance
	  Error reporting.

	Returns
	-------
	Dictionary
		Keys are case-sensitive group names as strings. Values are lists of integers. Atom indices are one-based.
	"""
	groups = dict()
	if filenames is None:
		return groups

	for filename in filenames:
		try:
			fh = open(filename, 'r')
		except:
			output.print_info('Reading file %s' % filename)
			output.print_error(messages.NOT_EXIST)
		groups = _parse_indexfile(fh.readlines(), groups, output)

	return groups

def parse_frame_selection(frames, output):
	"""
	Takes a pythonic selection syntax as string and converts it to a :func:`slice` object.

	Parameters
	----------
	frames : String
	  Selection command for integer ranges.
	output : :class:`output_tracker` instance
	  Error reporting.

	Returns
	-------
	slice
		A :func:`slice` object.

	Examples
	--------
	>>> parse_frame_selection('1:2:10', output)
	slice(1, 2, 10)

	>>> parse_frame_selection('', output)
	slice(None, None, None)

	>>> parse_frame_selection('-1', output)
	slice(-1, None, 1)

	>>> parse_frame_selection('::10', output)
	slice(None, None, 10)
	"""
	f_sel = slice(None)
	if frames == '':
		return f_sel
	frames = frames.strip()
	if ':' in frames:
		parts = frames.split(':')
		try:
			parts = map(lambda x: None if x.strip() == '' else int(x), parts)
		except:
			output.print_info('Given frame slice was %s' % frames)
			output.print_error(messages.NO_SLICE)
		f_sel = slice(*parts)
	else:
		try:
			num = int(frames)
		except:
			output.print_info('Given frame slice was %s' % frames)
			output.print_error(messages.NO_SLICE)
		if num >= 0:
			f_sel = slice(num, num+1)
		elif num == -1:
			f_sel = slice(-1, None, 1)
		else:
			f_sel = slice(num, num+1, 1)

	return f_sel

def _require_mda(output):
	"""
	Makes sure that MDAnalysis is loaded and prints an error message otherwise.

	Raises
	------
	Exception
		If MDAnalysis is unavailable. 

	Returns
	-------
	module
		MDAnalysis module instance.
	"""
	if not HAS_MDA:
		output.print_error(messages.MDA_DEP)

	return mda

def mda_goto(universe, target_frame, output):
	"""
	Seeks to a specific frame in the trajectory.

	Parameters
	----------
	universe : :class:`mda:MDAnalysis.core.AtomGroup.Universe`
	  The universe which trajectory is to be analyzed.
	target_frame : integer
	  Zero-based index of the frame to select.
	output : :class:`output_tracker` instance
	  Error reporting.

	Returns
	-------
	integer:
	  Zero-based index of the frame that was selected when this function was called.
	"""
	_require_mda(output)

	# MDAnalysis uses one based frame numbers
	target_frame += 1
	initial_frame = universe.trajectory.frame

	if target_frame == initial_frame:
		return

	try:
		if target_frame >= len(universe.trajectory):
			output.print_error(messages.INVALID_FRAME_SEL)
	except:
		# implementing __len__ for MDAnalysis trajectories is optional
		pass

	try:
		universe.trajectory[target_frame]
	except:
		# seek not implemented in MDAnalysis
		output.print_warn(messages.MANUAL_SEEK)
		if target_frame < current_frame:
			universe.trajectory.rewind()

		try:
			while universe.trajectory.frame < target_frame:
				universe.trajectory.next()
		except IOError:
			output.print_error(messages.SEEK_PAST_FILE)

	return initial_frame - 1

def _parse_dash_range(command, output):
	"""
	Parses range specification based on dash-separated limits.

	Parameters
	----------
	command : String
		The selection to parse.
	output : :class:`output_tracker` instance
	  Error reporting.

	Returns
	-------
	Iterable :
		List of integers.

	Examples
	--------
	>>> _parse_dash_range('2-3')
	[2, 3]
	"""
	parts = command.split('-')
	if len(parts) != 2:
		output.print_info('Got %s.' % parts)
		output.print_error(messages.DASH_RANGE_SYNTAX)

	try:
		temp = map(int, parts)
	except:
		output.print_info('Got %s.' % command)
		output.print_error(messages.INT_CONVERSION)
	start, stop = temp
	if stop < start:
		output.print_info('Got %s.' % temp)
		output.print_error(messages.REVERSE_BOUNDS)
	if start < 0 or stop < 0:
		output.print_error(messages.DASH_RANGE_NONNEG)

	return range(start, stop+1)

def _parse_colon_range(command, output):
	"""
	Parses range specification in python syntax.

	Parameters
	----------
	command : String
		The selection to parse.
	output : :class:`output_tracker` instance
	  Error reporting.

	Returns
	-------
	Iterable :
		List of integers.	

	Examples
	--------
	>>> _parse_colon_range('2:5:2')
	[2, 4]
	"""
	parts = command.split(':')
	if len(parts) not in (2, 3):
		output.print_info('Got %s.' % command)
		output.print_error(messages.COLON_RANGE_SYNTAX)

	try:
		temp = map(int, parts)
	except:
		output.print_info('Got %s.' % command)
		output.print_error(messages.INT_CONVERSION)

	return range(*temp)

def _parse_ids(command, output):
	"""
	Parses id selections including mixed range specifications, exclusions and precedence.

	Ranges can be given either by dash separated limits (includes the upper bound) or by python-like colon separated limits (does not include the upper limit). Stride syntax supported for the latter. Open ranges are not allowed.

	Parameters
	----------
	command : String
		The selection to parse
	output : :class:`output_tracker` instance
	  Error reporting.

	Returns
	-------
	Iterable :
		Sorted list of integers.

	Examples
	--------
	>>> _parse_ids('3-6')
	[3, 4, 5, 6]
	>>> _parse_ids('3-6,^4-5')
	[3, 6]
	>>> _parse_ids('2-3,4:7:2')
	[2, 3, 4, 6]
	"""
	# build list from range selections
	command = command.strip()
	cmds = command.replace(' ', ',').split(',')

	# filter repeated separators
	cmds = [_ for _ in cmds if len(_) != 0]

	# loop over commands
	ids = set()
	for cmd in cmds:
		exclude = cmd.startswith('^')
		if exclude:
			cmd = cmd[1:]

		if '-' in cmd:
			cmd_ids = _parse_dash_range(cmd, output)
		elif ':' in cmd:
			cmd_ids = _parse_colon_range(cmd, output)
		else:
			try:
				cmd_ids = set([int(cmd)])
			except:
				output.print_info('Got %s.' % cmd)
				output.print_error(messages.INT_CONVERSION)

		if exclude:
			ids = ids.difference(cmd_ids)
		else:
			ids = ids.union(cmd_ids)

	return list(ids)

def mda_select(universe, selection, output, selection_frame=None):
	"""
	Selects an atom group by CHARMM selection or :ref:`atom selection <atomselections>` syntax.

	Parameters
	----------
	universe : :class:`mda:MDAnalysis.core.AtomGroup.Universe`
	  The universe which trajectory is to be analyzed.
	selection : String
	  The CHARMM-style selection request.
	output : :class:`output_tracker` instance
	  Error reporting.
	selection_frame : Integer, optional
	  If set, the selection command will be performed using the coordinates of this frame.

	Returns
	-------
	MDAnalysis.atomGroup
	  Atom group which is valid for all frames of the loaded trajectory of the given universe.

	Raises
	------
	Exception
		If MDAnalysis is unavailable.
	"""
	_require_mda(output)

	if selection is None:
		initial_selection = universe.atoms 
	elif selection.startswith('id '):
		ids = _parse_ids(selection[3:], output)
		try:
			ag = universe.atoms[ids]
		except Exception, e:
			output.print_info('MDAnalysis: %s' % str(e))
			output.print_error(messages.SELECT_FAILED)
	else:
		if selection_frame is not None:
			previous = mda_goto(universe, selection_frame, output)
		try:
			initial_selection = universe.selectAtoms(selection)
		except Exception, e:
			raise
			output.print_info('MDAnalysis: %s' % str(e))
			output.print_error(messages.CHARMM_SELECTION)
		if selection_frame is not None:
			mda_goto(universe, previous, output)
	return initial_selection

class IdSelection(mda.core.Selection.Selection):
	"""
	Parser for id selection.
	"""
	def __init__(self, ids):
		"""
		Accepts the data to be parsed.

		Parameters
		----------
		ids : String
			Ids. See :ref:`atomselections`.
		"""
		self._data = ids

	def _apply(self, group):
		"""
		Parses the data given.

		Parameters
		----------
		group : :class:`MDAnalysis.core.AtomGroup`
			Atoms to select from.

		Returns
		-------
		Set 
			Selected Atoms.

		Raises
		------
		ValueError
			If the selection was unparseable.
		"""
		output = ot.null_output()			
		try:
			ids = _parse_ids(self._data, output)
		except:
			raise ValueError('Unable to parse ID selection %s' % ids)
		atoms = set()
		for e in ids:
			atoms.insert(groups.atoms[e])
		return atoms

class GroupSelection(mda.core.Selection.Selection):
	"""
	Parser for named group selection.
	"""
	def __init__(self, groups):
		"""
		Accepts the data to be parsed.

		Parameters
		----------
		groups : String
			Comma-separated group names without any spaces.
		"""
		self._data = groups

	def _apply(self, group):
		"""
		Parses the data given.

		Parameters
		----------
		group : :class:`MDAnalysis.core.AtomGroup`
			Atoms to select from.

		Returns
		-------
		Set 
			Selected Atoms.

		Raises
		------
		TypeError
			If the atom group has not been initially selected from an :class:`UniverseWrapper` instance.
		ValueError
			If any group is unknown or no group was given.
		"""
		try:
			available_groups = group.universe.get_index_groups()
		except:
			raise TypeError('group selection requires the usage of UniverseWrapper instead of Universe.')

		groupnames = self._data.split(',')
		available_names = set(available_groups.keys())
		requested_names = set(groupnames)
		if len(requested_names-available_names) > 0:
			raise ValueError('Unknown group(s): %s' % ', '.join(list(requested_names-available_names)))
		if len(requested_names) == 0:
			raise ValueError('At least one group has to be specified.')

		indices = [set(available_groups[_]) for _ in requested_names]
		indices = reduce(lambda x, y: x.union(y), indices)
		return set([_ for _ in group.atoms if _.number in indices])

class UniverseWrapper(mda.core.AtomGroup.Universe):
	"""
	Allows for additional information to be connected to an MDAnalysis :class:`~MDAnalysis.core.AtomGroup.Universe`.
	"""
	#: Named groups. Keys: Strings of group names, Values: List of one-based atom indices
	_index_groups = dict()

	def get_index_groups(self):
		"""
		Retrieves named atom groups.

		Returns
		-------
		Dictionary
			Keys are group names, Values are iterables of one-based atom indices.
		"""
		return self._index_groups

	def add_index_groups(self, groups):
		"""
		Adds multiple named atom groups to the topology definition.

		Parameters
		----------
		groups : Dictionary
			Keys are group names, Values are iterables of one-based atom indices.
		"""
		for group, indices in groups.iteritems():
			try:
				self._index_groups[str(group)] = [int(_) for _ in indices]
			except:
				# No output_tracker connection here for better transferability.
				raise ValueError('Invalid group dictionary entries.')

	def remove_index_groups(self, groups, require_existing=False):
		"""
		Removes multiple named atom groups from the topology definition.

		Parameters
		----------
		groups : Iterable
			Group names to remove.
		require_existing : Boolean
			Whether to raise an exception if any of the specified groups has not been defined so far.
		"""
		for group in groups:
			try:
				del self._index_groups[str(group)]
			except:
				if require_existing:
					raise ValueError('Group %s does not exist.' % group)

class ExtendedSelectionParser(mda.core.Selection.SelectionParser):
	"""
	Extends the MDAnalysis selection parser.

	.. note:: 
		Has to be an old-style class for compatibility to MDAnalysis.
	"""

	#: Selection token for atom ids
	ID = 'id'
	#: Selection token for named groups
	GROUP = 'group'

	def __init__(self):
		"""
		Adds the newly defined keywords to the keywords :class:`mda.core.Selection.SelectionParser` supports.
		"""
		self.classdict[self.ID] = IdSelection
		self.classdict[self.GROUP] = GroupSelection

	def _SelectionParser__parse_subexp(self):
		"""
		Intercepts parsing of subexpressions and deals with the newly defined selection commands.
		"""
		op = self._SelectionParser__peek_token()

		# idea copied from mda.core.Selection.SelectionParser.__parse_subexp
		if op in (self.ID, self.GROUP):
			op = self._SelectionParser__consume_token()
			data = self._SelectionParser__consume_token()
			if data in (self.LPAREN, self.RPAREN, self.AND, self.OR, self.NOT, self.SEGID, self.RESID, self.RESNAME, self.NAME, self.TYPE):
				self._SelectionParser__error("Identifier")
			return self.classdict[op](data)
		else:
			return mda.core.Selection.SelectionParser._SelectionParser__parse_subexp(self)

def mda_patch_parser(enable=True):
	"""
	Patches the loaded MDAnalysis selection parser to incorporate `group` and `id` keywords.

	Parameters
	----------
	enable : Boolean
		Whether to activate the extended parser. If `False`, the original state will be recovered.
	"""
	if enable:
		mda.core.Selection.Parser = ExtendedSelectionParser()
	else:
		mda.core.Selection.Parser = mda.core.Selection.SelectionParser()

def mda_select_id(universe, selection, output):
	"""
	Extends the MDAnalysis CHARMM selection parser by a keyword for selection by id. 

	Atom ids are one-based (as usual for MDAnalysis).

	Parameters
	----------
	universe : :class:`mda:MDAnalysis.core.AtomGroup.Universe`
	  The universe which trajectory is to be analyzed.
	selection : String
	  The CHARMM-style selection request.
	output : :class:`output_tracker` instance
	  Error reporting.

	Returns
	-------
	MDAnalysis.atomGroup
	  Atom group which is valid for all frames of the loaded trajectory of the given universe.
	"""
	if selection.startswith('id '):
		ids = _parse_ids(selection[3:], output)
		try:
			ag = universe.atoms[ids]
		except Exception, e:
			output.print_info('MDAnalysis: %s' % str(e))
			output.print_error(fc.messages.SELECT_FAILED)
	else:
		if len(selection.strip()) == 0:
			selection = 'all'
		ag = mda_select(universe, selection, output)

	return ag

def mda_set_periodic(value, output):
	"""
	Sets the flag whether to respect periodic boundary conditions in MDAnalysis calculations.

	Parameters
	----------
	value : Boolean
	  Flag value

	Raises
	------
	Exception
		If MDAnalysis is unavailable.
	"""
	_require_mda(output)

	mda.core.flags['use_periodic_selections'] = value
	mda.core.flags['use_KDTree_routines'] = (not value)

def mda_load_universe(topology, coordinates, output):
	"""
	Creates a MDAnalysis.Universe from a trajectory with error checks.

	Parameters
	----------
	topology : String
	  Topology file name. Supported file formats: see MDAnalysis. May be compressed with gzip or bzip2.
	coordinates : String
	  Coordinate file name. Supported file formats: see MDAnalysis. May be compressed with gzip or bzip2.
	output : :class:`output_tracker` instance
	  Error reporting.

	Returns
	-------
	universe
	  The created :class:`UniverseWrapper` which is essentially identical to :class:`mda:MDAnalysis.core.AtomGroup.Universe`.

	Raises
	------
	Exception
		If MDAnalysis is unavailable.
	Exception
		If the import failed.
	"""
	_require_mda(output)

	try:
		u = UniverseWrapper(topology, coordinates)
	except Exception, e:
		output.print_info('MDAnalysis: %s' % str(e))
		output.print_error(messages.IMPORT_FAILED)

	return u

def mda_get_framecount(universe, selection, output, complain_empty=False):
	"""
	Calculates the number of frames selected by a slice for MDAnalysis trajectories.

	Parameters
	----------
	universe : :class:`mda:MDAnalysis.core.AtomGroup.Universe`
	  The universe which trajectory is to be analyzed.
	selection : slice
	  A frame selection.
	output : :class:`output_tracker` instance
	  Error reporting.
	complain_empty: Boolean, optional
	  Whether to report a fatal error on empty selection.

	Returns
	-------
	Integer
	  The number of frames.

	Raises
	------
	Exception
		If MDAnalysis is unavailable.
	Exception
		If the slice is of length zero and `complain_empty` is True.
	"""
	_require_mda(output)

	# implementing __len__ for MDAnalysis trajectories is optional
	try:
		length = len(universe.trajectory)
	except:
		output.print_warn(messages.UNKNOWN_LENGTH)
		return None

	start = 0 if selection.start is None else selection.start if selection.start >= 0 else length + selection.start
	stop = length if selection.stop is None else selection.stop if selection.stop >= 0 else length + selection.stop
	step = 1 if selection.step is None else abs(selection.step)
	numframes = max((stop-start)/step, 0)
	if numframes == 0 and complain_empty:
		output.print_error(messages.NO_FRAME)
	if abs(start) > length:
		output.print_error(messages.SLICE_START_RANGE)
	if abs(stop) > length:
		output.print_error(messages.SLICE_STOP_RANGE)

	return numframes

def dot_product(a, b, output):
	""" Calculates the dot product of two vectors of arbitrary dimensionality.

	Parameters
	----------
	a, b : iterable, numeric
		Vectors. 
	output : :class:`output_tracker` instance
	  Error reporting.

	Returns
	-------
	The dot product.

	Raises
	------
	Exception:
		When the vectors have different dimensions.
	"""
	a = np.array(a)
	b = np.array(b)

	if len(a) != len(b):
		output.print_error(messages.DIM_MISMATCH)

	return np.array(a).dot(np.array(b))

def angle(a, b, output):
	"""
	Calculates the angle between two vectors of arbitrary dimensionality.

	Parameters
	----------
	a, b : iterable, numeric
		Vectors.
	output : :class:`output_tracker` instance
	  Error reporting.

	Returns
	-------
	The angle in radians.

	Raises
	------
	Exception:
		When the vectors have different dimensions.
	Exception:
		When at least one of the vectors is the null vector.
	"""
	a = np.array(a)
	b = np.array(b)
	if npl.norm(a) == 0 or npl.norm(b) == 0:
		output.print_error(messages.NO_NULL_VECTOR)

	return math.acos(dot_product(a, b, output) / (npl.norm(a)*npl.norm(b)))

class PSFFile(object):#doc-contains: _angles, _atoms, _bonds, _dihedrals, _impropers, _lines, _output, _parsed
	"""
	Holds information about a single protein structure format file. Implements a fluent interface.
	"""
	def __init__(self, stream, output=None):
		"""
		Prepares data structures.

		.. todo:: 
			Check for attribute documentation.

		Parameters
		----------
		stream : List of strings or file object.
			Input data.
		output : :class:`output_tracker` or `None`
			Error reporting. If parameter value is `None`, error reporting is disabled.
		"""
		#: Reference to the currently used :class:`~output_tracker.output_tracker` instance.
		self._output = None
		if output is None:
			self._output = ot.null_output()
		else:
			self._output = output

		#: List of strings. ASCII lines in the input file.
		self._lines = []
		if type(stream) == list:
			self._lines = stream
		else:
			self._lines = stream.readlines()
		if len(self._lines) == 0 or not type(self._lines[0]) is str:
			self._output.print_error(ot.errors.EMPTY_INPUT)

		#: Internal flag whether the data in :attr:`_lines` has been parsed already to allow for lazy parsing.
		self._parsed = False
		#: List of sets containing the indices of the :class:`~toto.atom.atom` instances in :attr:`_atoms` that form a bond.
		self._bonds = [] 
		#: List of :class:`~toto.atom.atom` instances. Ordering is relevant for :attr:`_angles`, :attr:`_bonds`, :attr:`_dihedrals`, and :attr:`_impropers`.
		self._atoms = [] 
		#: List of sets containing the indices of the :class:`~toto.atom.atom` instances in :attr:`_atoms` that form an angle.
		self._angles = [] 
		#: List of sets containing the indices of the :class:`~toto.atom.atom` instances in :attr:`_atoms` that form a dihedral.
		self._dihedrals = []
		#: List of sets containing the indices of the :class:`~toto.atom.atom` instances in :attr:`_atoms` that form an improper dihedral.
		self._impropers = []

	def __deepcopy__(self, memo):
		"""
        Creates a completely independent instance of :class:`psffile` that essentially is identical to the current one.

        Parameters
        ----------
        memo : Dictionary
        	Dictionary of objects already copied.

        Returns
        -------
        :class:`psffile`
        	The copy.
		"""
		c = psffile(self._lines, self._output)
		c._parsed = self._parsed
		c._bonds = self._bonds[:]
		c._atoms = [copy.deepcopy(_) for _ in self._atoms]
		c._angles = self._angles[:]
		c._dihedrals = self._dihedrals[:]
		c._impropers = self._impropers[:]
		return c

	def parse(self):
		"""
		Cached parsing of the given source lines.

		Returns
		-------
		self
			Allows for fluent interface.
		"""
		if self._parsed:
			return self

		self._parse_atoms()._parse_bonds()._parse_angles()._parse_dihedrals()._parse_impropers()
		self._parsed = True
		return self

	def get_total_charge(self):
		"""
        Calculates the total charge of all atoms.

        Returns
        -------
        Float
        	Charge in electron charges.
		"""
		return sum([_.get_charge() for _ in self._atoms])

	def get_total_mass(self):
		"""
        Calculates the total mass of all atoms.

        Returns
        -------
        Float
        	Mass in amu.
		"""
		return sum([_.get_mass() for _ in self._atoms])

	def _scan_section(self, header):
		"""
        Reads all lines for a given section of a PSF file.
		
		.. note:: 
        	This routine performs no checks whatsoever on this header entry.

        Parameters
        ----------
        header : String
        	The header section to search for.

        Returns
        -------
        Tuple
        	Tuple of the number of entries that should be in the file and a list of strings holding all input lines for this section. Please note that empty entries can occurr in case no lines for this section could be found.
		"""
		started = False
		section = []
		header = '!' + header
		expected_num = None
		for line in self._lines:
			if header in line:
				started = True
				if expected_num is not None:
					self._output.print_error(ot.errors.DOUBLE_PSF_SECTION)
				try:
					expected_num = int(line.strip().split(header)[0])
				except:
					self._output.print_error(ot.errors.PSF_LINE_NO_CONV)
				continue
			if started and line.strip() == '':
				started = False

			if started:
				section.append(line)

		return (expected_num, section)

	def _parse_bonds(self):
		"""
        Extracts all data from :attr:`_lines` that is related to bonds.

        Returns
        -------
        self
        	Allows for fluent interface.
		"""
		enum, bondspec = self._scan_section('NBOND')
		bondspec = ' '.join([_.strip() for _ in bondspec])

		bondspec = bondspec.split()
		if len(bondspec) % 2 != 0:
			self._output.print_error(ot.errors.BONDSPEC)
		try:
			bondspec = map(int, bondspec)
			bondspec = map(lambda x: x-1, bondspec)
		except:
			self._output.print_error(ot.errors.BOND_CONV)
		f = bondspec[0::2]
		t = bondspec[1::2]

		self._bonds = zip(f, t)
		if len(self._bonds) != enum:
			self._output.print_error(ot.errors.PSF_BOND_NUMBER)

		return self

	def _parse_atoms(self):
		"""
        Extracts all data from :attr:`_lines` that is related to atoms.

        Returns
        -------
        self
        	Allows for fluent interface.
		"""
		enum, atomspec = self._scan_section('NATOM')
		# TODO: check for enum=None which means no NATOM section
		if len(atomspec) != enum:
			self._output.print_info('Expected %d atoms from header, got %d lines.' % (enum, len(atomspec)))
			self._output.print_error(ot.errors.PSF_ATOM_NUMBER)

		self._atoms = [atom.from_psf_line(_) for _ in atomspec]
		atom_numbers = [_.get_psf_number() for _ in self._atoms]
		if len(self._atoms) == 0:
			self._output.print_error(ot.errors.PSF_NO_ATOMS)

		if len(set(atom_numbers)) != len(atom_numbers):
			self._output.print_error(ot.errors.PSF_ATOM_UNIQUE)

		if not min(atom_numbers) == 1 and max(atom_numbers) == len(atom_numbers) + 1:
			self._output.print_error(ot.errors.PSF_CONTIGUOUS)
		return self

	def _parse_angles(self):
		"""
		Extracts all data from :attr:`_lines` that is related to angles.

        Returns
        -------
        self
        	Allows for fluent interface.
		"""
		enum, anglespec = self._scan_section('NTHETA')
		anglespec = ' '.join([_.strip() for _ in anglespec])

		angles = anglespec.split()
		if len(angles) % 3 != 0:
			self._output.print_error(ot.errors.ANGLESPEC)
		try:
			angles = map(int, angles)
			angles = map(lambda x: x-1, angles)
		except:
			self._output.print_error(ot.errors.ANGLE_CONV)
		f = angles[0::3]
		v = angles[1::3]
		t = angles[2::3]

		self._angles = zip(f, v, t)
		if len(self._angles) != enum:
			self._output.print_error(ot.errors.PSF_ANGLE_NUMBER)
		return self

	def _parse_dihedrals(self):
		"""
        Extracts all data from :attr:`_lines` that is related to dihedrals.

        Returns
        -------
        self
			Allows for fluent interface.
		"""
		enum, dhspec = self._scan_section('NPHI')
		dhspec = ' '.join([_.strip() for _ in dhspec])

		dihedrals = dhspec.split()
		if len(dihedrals) % 4 != 0:
			self._output.print_error(ot.errors.DIHEDRALSPEC)
		try:
			dihedrals = map(int, dihedrals)
			dihedrals = map(lambda x: x-1, dihedrals)
		except:
			self._output.print_error(ot.errors.DIHEDRAL_CONV)
		f 	= dihedrals[0::4]
		v1 	= dihedrals[1::4]
		v2 	= dihedrals[2::4]
		t 	= dihedrals[3::4]

		self._dihedrals = zip(f, v1, v2, t)
		if len(self._dihedrals) != enum:
			self._output.print_error(ot.errors.PSF_DIHEDRAL_NUMBER)
		return self

	def _parse_impropers(self):
		"""
        Extracts all data from :attr:`_lines` that is related to improper dihedrals.

        Returns
        -------
        self
			Allows for fluent interface.
		"""
		enum, impspec = self._scan_section('NIMPHI')
		impspec = ' '.join([_.strip() for _ in impspec])

		impropers = impspec.split()
		if len(impropers) % 4 != 0:
			self._output.print_error(ot.errors.IMPROPERSPEC)
		try:
			impropers = map(int, impropers)
			impropers = map(lambda x: x-1, impropers)
		except:
			self._output.print_error(ot.errors.IMPROPER_CONV)
		f 	= impropers[0::4]
		v1 	= impropers[1::4]
		v2 	= impropers[2::4]
		t 	= impropers[3::4]

		self._impropers = zip(f, v1, v2, t)
		if len(self._impropers) != enum:
			self._output.print_error(ot.errors.PSF_IMPROPER_NUMBER)
		return self

	def delete_atom(self, idx):
		"""
		Removes all data related to a specific atom from the internal representation.

		Parameters
		----------
		idx : Integer
        	The list index of the :class:`~toto.atom.atom` instances in :attr:`_atoms`.

        Returns
        -------
        self
			Allows for fluent interface.
		"""
		for atm in self._atoms[idx+1:]:
			atm.set_psf_number(atm.get_psf_number()-1)
		del self._atoms[idx]

		for group in [self._bonds, self._angles, self._dihedrals, self._impropers]:
			for gnr, entry in enumerate(group):
				if idx in entry:
					group[gnr] = None
					continue
				ecopy = [_-1 if _ > idx else _ for _ in entry]
				entry = tuple(ecopy)
				group[gnr] = entry
		self._bonds = [_ for _ in self._bonds if not _ is None]
		self._angles = [_ for _ in self._angles if not _ is None]
		self._dihedrals = [_ for _ in self._dihedrals if not _ is None]
		self._impropers = [_ for _ in self._impropers if not _ is None]
		return self

	def _delete_residues_except(self, residue):
		"""
        Removes all entries that are related to all but a single residue.

        Parameters
        ----------
        residue : String
        	Residue name of the only residue that is to be kept.

        Returns
        -------
        self :
        	Allows for fluent interface.
		"""
		tbd = [idx for idx, _ in enumerate(self._atoms) if _.get_residue() != residue]
		tbd.reverse()
		for a in tbd:
			self.delete_atom(a)
		return self

	def extract_residue(self, residue):
		"""
        Builds a new :class:`psffile` instance only containing a single residue.

        Parameters
        ----------
        residue : String
        	Residue name.

        Returns
        -------
        :class:`psffile`
        	A completely independent instance.
		"""
		check = [_ for _ in self._atoms if _.get_residue() == residue]
		if len(check) == 0:
			self._output.print_error(ot.errors.NO_SUCH_RESIDUE)

		n = copy.deepcopy(self)
		n._delete_residues_except(residue)
		return n

	def get_psf_string(self):
		"""
        Builds a string representation of the whole file.

        Returns
        -------
        String
        	Whole file a single string. Lines are separated by newline characters.
		"""
		ret = 'PSF\n\n       1 !NTITLE\n REMARKS generated on ' + str(datetime.datetime.now()) + '\n\n'
		ret += '%8d !NATOM\n' % len(self._atoms)
		for a in self._atoms:
			ret += '{0:8} {1:4} {2:<4} {3:4} {4:4} {5:>4} {6:> 10.6f} {7:>15.6f}  {8:8}\n'.format(
				a.get_psf_number(),
				a.get_segment_name(),
				a.get_residue_id(),
				a.get_residue(),
				a.get_name(),
				a.get_atom_type(),
				a.get_charge(),
				a.get_mass(),
				int(a.is_constrained()))

		for label, data in [('NBOND', self._bonds), ('NTHETA', self._angles), ('NPHI', self._dihedrals), ('NIMPHI', self._impropers)]:
			ret += '\n%8d !%s:\n' % (len(data), label)
			dlist = [''.join(['{0:8}'.format(_+1) for _ in elements]) for elements in data]
			#dlist = [list(_) for _ in data]
			#dlist = ['{0:8}'.format(_+1) for _ in sum(dlist, [])]
			tline = ''
			for element in dlist:
				if len(tline) > 60:
					ret += tline + '\n'
					tline = ''
				tline += element
			ret += tline + '\n'

		ret += '\n       0 !NDON:\n\n       0 !NACC:\n\n       0 !NNB:\n\n'
		return ret

	def is_compatible(self, atomlist):
		"""
        Checks whether there is a unique one-to-one mapping of all atoms in the internal data structures. 

        For the definition of compatible, see :meth:`~toto.atom.atom.compatible_to`.

        Parameters
        ----------
        atomlist : List of :class:`~toto.atom.atom` instances
        	The atoms to compare to. The ordering of the atoms is of relevance to the result as the PSF indices are projected onto this list.

        Returns
        -------
        Boolean
        	True only if no inconsistencies occurred during the check.
		"""
		if len(self._atoms) != len(atomlist):
			return False

		for a1, a2 in zip(self._atoms, atomlist):
			if not a1.compatible_to(a2):
				return False

		return True

	def is_bonded(self, f, t):
		"""
        Checks whether a bond between two :class:`~toto.atom.atom` instances is defined in this instance.

        Ordering does not matter.

        Parameters
        ----------
        f : :class:`~toto.atom.atom`
        	First atom of the bond.
        t : :class:`~toto.atom.atom`
        	Last atom of the bond.
        	
        Returns
        -------
        Boolean
		"""
		return (f, t) in self._bonds or (t, f) in self._bonds

	def is_dihedral(self, f, v1, v2, t):
		"""
		Checks whether a torsional angle between four :class:`~toto.atom.atom` instances is defined in this instance.

        Ordering does matter. Either `f`-`v1`-`v2`-`t` or `t`-`v2`-`v1`-`f` have to exist in case this function evaluates to True.

        Parameters
        ----------
        f : :class:`~toto.atom.atom`
        	First atom of the angle.
        v1 : :class:`~toto.atom.atom`
        	Middle atom of the angle.
        v2 : :class:`~toto.atom.atom`
        	Middle atom of the angle.
        t : :class:`~toto.atom.atom`
        	Last atom of the angle.
        	
        Returns
        -------
        Boolean
		"""
		return (f, v1, v2, t) in self._dihedrals or (t, v2, v1, f) in self._dihedrals

	def is_improper(self, f, v1, v2, t):
		"""
		Checks whether an improper torsional angle between four :class:`~toto.atom.atom` instances is defined in this instance.

        Ordering does matter. Either `f`-`v1`-`v2`-`t` or `t`-`v2`-`v1`-`f` have to exist in case this function evaluates to True.

        Parameters
        ----------
        f : :class:`~toto.atom.atom`
        	First atom of the angle.
        v1 : :class:`~toto.atom.atom`
        	Middle atom of the angle.
        v2 : :class:`~toto.atom.atom`
        	Middle atom of the angle.
        t : :class:`~toto.atom.atom`
        	Last atom of the angle.
        	
        Returns
        -------
        Boolean
		"""
		return (f, v1, v2, t) in self._impropers or (t, v2, v1, f) in self._impropers

	def is_angle(self, f, v, t):
		"""
        Checks whether an angle between three :class:`~toto.atom.atom` instances is defined in this instance.

        Ordering does matter. Either `f`-`v`-`t` or `t`-`v`-`f` have to exist in case this function evaluates to True.

        Parameters
        ----------
        f : :class:`~toto.atom.atom`
        	First atom of the angle.
        v : :class:`~toto.atom.atom`
        	Middle atom of the angle.
        t : :class:`~toto.atom.atom`
        	Last atom of the angle.
        	
        Returns
        -------
        Boolean
		"""
		return (f, v, t) in self._angles or (t, v, f) in self._angles

	def set_charge(self, atom_type, charge):
		"""
        Changes the internal value of the charge of a certain atom type.

        Parameters
        ----------
        atom_type : String
        	Atom type selection of the relevant atoms.
        charge : Float
        	New charge in electron charges.

        Returns
        -------
        self
        	Allows for fluent interface.
		"""
		for a in self._atoms:
			if a.get_atom_type() == atom_type:
				a.set_charge(charge)

		return self

	def get_atom(self, idx):
		"""
		Access method for a single atom.

		Parameters
		----------
		idx : Integer
			Zero-based index of the atom to retrieve.

		Returns
		-------
		:class:`~toto.atom.atom`
			The atom instance.

			.. note::
				Please keep in mind that this atom instance is still related to the :class:`psffile` instance you got it from. In case you want to modify the atom properties but leave the PSF file unchanged, you have to call :meth:`~todo.atom.atom.__deepcopy__`.
		"""
		return self._atoms[idx]

	def get_atom_count(self):
		"""
		Returns the number of atoms that are described in this PSF file.
		"""
		return len(self._atoms)

	def iteratoms(self):
		"""
		Generator for iterating over the atoms of this PSF file.
		"""
		for _ in self._atoms:
			yield _

class PDBFile(object): #isdoc #doc-contains: _psf, _lines, _parsed, _atoms, _valid, _residues, _output
	"""
	Holds information about a single protein database file.
	"""

	def __init__(self, stream, output = None):
		"""
		Prepares internal data structures.

		Parameters
		----------
		stream : List of strings, file object
			Input file as list of the input lines or a file object.
		output : :class:`output_tracker` or `None`
			Error reporting. If parameter value is `None`, error reporting is disabled.
		"""
		#: Reference to either :class:`~output_tracker.output_tracker` or :class:`~output_tracker.null_output`. In the latter case only error messsages are printed. Is to be set by :meth:`__init__`.
		self._output = None
		if output is None:
			self._output = ot.null_output()
		else:
			self._output = output

		#: List of strings. Contains all data from the source file stream. Should be considered read-only.
		self._lines = None
		if type(stream) == list:
			self._lines = stream
		else:
			self._lines = stream.readlines()
		if len(self._lines) == 0 or not type(self._lines[0]) is str:
			self._output.print_error(ot.errors.EMPTY_INPUT)

		self._strip_bom()

		#: Dictionary used for consistency checks during strict parsing. The residue names as strings are used as keys. Each entry contains another dictionary holding the :class:`~toto.atom.atom` instances as values using their (supposedly) unique atom name as key.
		self._residues = dict()
		#: Holds the result of internal linter. A value of `None` denotes that no syntax check has been perfomed, yet. Otherwise this attribute holds a boolean value. Some of the access methods use a separate parsing method that is less strict.
		self._valid = None
		#: List of :class:`~toto.atom.atom` instances. Is kept in sync with the atom list of :attr:`_psf`. May be empty. 
		self._atoms = []
		#: A reference to :class:~toto.pdbfile.psffile`. If no PSF file is loaded, this reference is `None`.
		self._psf = None
		#: Boolean. Used for caching. Is `True` when the source data in :attr:`_lines` has been parsed.
		self._parsed = False

	def purge_metadata(except_first=False):
		"""
		Removes all lines from the internal representation that do not contain atom definitions. 

		Practically, this means removing all lines that do not contain a ATOM or HETATM definition.

		Parameters
		----------
		except_first : Boolean
			Whether to keep the first contiguous set of non-atom lines that precedes any atom definition.

		Returns
		-------
		self :
			Allows for fluent interface.
		"""
		offset = 0
		atom_lines = [idx for idx, _ in enumerate(self._lines) if _.startswith('ATOM') or _.startswith('HETATM')]
		if except_first:
			offset = min(atom_lines)
		self._lines = self._lines[0:offset] + [self._lines[_] for _ in atom_lines]

		return self

	def find_atoms(self, residue_name=None, atom_name=None):
		"""
        Creates a list of the atoms in this PDB file only containing the atoms with a certain residue name or atom name.

        Parameters
        ----------
        residue_name : String
        	The residue name to filter for. `None` matches all atoms.
        atom_name : String
        	The atom name to filter for. `None` matches all atoms.

        Returns
        -------
        List of :class:`~toto.atom.atom` 
        	Instances that fulfill all specified criteria.
		"""
		res = self._atoms[:]

		if not residue_name is None:
			res = [_ for _ in res if _.get_residue() == residue_name]

		if not atom_name is None:
			res = [_ for _ in res if _.get_name() == atom_name]

		return list(res)

	def get_bond(self, bond):
		"""
        Extracts the atoms that form a specific bond.
		
		.. todo:: 
			Check whether the two atoms are in fact bonded. 

        Parameters
        ----------
        bond : String
        	Format: `RESIDUE_NAME.ATOM_NAME-RESIDUE_NAME.ATOM_NAME`. The residue name may be omitted in case the atom name is unique to the whole file.
      
      	Returns
      	-------
      	List of :class:`~toto.atom.atom`.
      		Length two. Instances that match the request.
		"""
		parts = bond.split('-')
		if len(parts) != 2:
			self._output.print_error(ot.errors.PARSE_ERROR)

		atoms = []
		for part in parts:
			e = part.split('.')
			if len(e) == 1:
				residue_name = None
				atom_name = e[0]
			if len(e) == 2:
				residue_name, atom_name = e
			if len(e) > 2:
				self._output.print_error(ot.errors.PARSE_ERROR)
			r = self.find_atoms(residue_name, atom_name)
			if len(r) == 0:
				self._output.print_info('Looking for %s' % part)
				self._output.print_error(ot.errors.UNKNOWN_ATOM_NAME)
			if len(r) > 1:
				self._output.print_info('Looking for %s' % part)
				self._output.print_error(ot.errors.AMBIGUOUS_ATOM_NAME)
			atoms.append(r[0])
		return atoms

	def get_pdb_string(self, renumber=False, clean=False):
		"""
        Creates a new PDB string representation that could be written to a file.

        .. todo:: 
        	Currently, this ignores changes in atom count and bond topology.

        Parameters
        ----------
        renumber : Boolean
        	In case any of the atoms are removed, the atom number should be changes such that all atoms are numbered starting from one and in a contiguous fashion. As this alters the references in the specific file and potentially makes the new PDB file incompatible with other external resources, this behavior is deactivated by default.

        Returns
        -------
        String
        	Lines separated by newline characters.
		"""
		res = ''
		idx = 0
		for line in self._lines:
			if line.startswith('ATOM') or line.startswith('HETATM'):
				label = line[12:16].strip()
				a = self._atoms[idx].get_positions()
				if renumber:
					atom_number = str(idx+1)
				else:
					atom_number = line[6:11]
				idx += 1
				line = '{0}{1:5}{2}{3:8.3f}{4:8.3f}{5:8.3f}{6}'.format(line[0:6], atom_number, line[11:30], a[0], a[1], a[2], line[54:])
				res += line
			else:
				if clean is False:
					res += line
		if clean is True:
			res += 'END'
		return res

	def get_psf_string(self):
		"""
        Interface method for creation of a string representation of the PSF file that is related to the given PDB file. Essentially calls :meth:`PSFFile.get_psf_string`.

        Returns
        -------
        String
        	Lines separated by newline characters.
		"""
		if self._psf is None:
			self._output.print_error(ot.errors.PSF_REQUIRED)

		return self._psf.get_psf_string()

	def get_total_charge(self):
		"""
        Calculates the total charge of all atoms.

        Returns
        -------
        Float
        	Charge in electron charges.
		"""
		if self._psf is None:
			self._output.print_error(ot.errors.PSF_REQUIRED)
			
		return self._psf.get_total_charge()

	def get_total_mass(self):
		"""
        Calculate the total mass of all atoms.

        Returns
        -------
        Float
        	Mass in amu.
		"""
		return self._psf.get_total_mass()

	def set_charge(self, atom_type, charge):
		"""
        Changes the internal value of the charge of a certain atom type.

        Parameters
        ----------
        atom_type : String
        	The atom type to filter for.
        charge : Float
        	New value in electron charges.

        Returns
        -------
        self
        	Allows for fluent interface.
		"""
		if self._psf is None:
			self._output.print_error(ot.errors.PSF_REQUIRED)
			
		self._psf.set_charge(atom_type, charge)
		return self

	def get_atom_count(self, atom_type=None):
		"""
        Counts the atoms with a specific atom type. 

        If `atom_type` is `None`, the total atom number is returned. For atom type filtering, a PSF file has to be loaded. The total number of all atoms can be determined without having a matching PSF file.

        Parameters
        ----------
        atom_type : String or None
        	The atom type to filter for.

        Returns
        -------
        Integer
        	Atom type occurrence.
		"""
		if atom_type is None:
			return len(self._atoms)

		if self._psf is None:
			self._output.print_error(ot.errors.PSF_REQUIRED)

		return len([_ for _ in self._psf._atoms if _.get_atom_type() == atom_type])

	def get_all_atom_types(self):
		"""
        Extracts a list of all atom types without any duplicates.

        Returns
        -------
        Set
        	Unique enumeration of all atom types.
		"""
		if self._psf is None:
			self._output.print_error(ot.errors.PSF_REQUIRED)

		return set([_.get_atom_type() for _ in self._psf._atoms])

	def __deepcopy__(self, memo):
		"""
        Helper method for copying a whole PDB file including any depending PSF.

        Parameters
        ----------
        memo : dictionary
        	Contains all objects that have been copied already.

        Returns
        -------
        :class:`PDBFile`
      		A new and completely independent instance.
		"""
		c = pdbfile(self._lines, self._output)
		c._residues = copy.deepcopy(self._residues)
		c._valid = self._valid
		c._residues = copy.deepcopy(self._residues)
		c._atoms = [copy.deepcopy(_) for _ in self._atoms]
		c._parsed = self._parsed
		c._psf = copy.deepcopy(self._psf)
		return c

	def _delete_residues_except(self, residue):
		"""
		Removes all entries that are related to all but a single residue.

		Parameters
		----------
		residue : String
			Residue name of the only residue that is to be kept.

		Returns
		-------
		self
			Allows for fluent interface.
		"""
		# remove invalid lines
		nl = []
		for line in self._lines:
			if not line.startswith('ATOM ') and not line.startswith('HETATM'):
				nl.append(line)
			else:
				if line[17:20].strip() == residue:
					nl.append(line)
		self._lines = nl

		# remove invalid atoms
		for idx, atm in enumerate(self._atoms):
			if atm.get_residue() != residue:
				self._atoms[idx] = None
		self._atoms = [_ for _ in self._atoms if _ is not None]

		self._psf = self._psf.extract_residue(residue)

	def extract_residue(self, residue):
		"""
        Builds a new :class:`PDBFile` instance only containing a single residue.
      
      	Parameters
      	----------
      	residue : String
      		Residue name of the only residue that is to be kept.

      	Returns
      	-------
      	:class:`PDBFile`
      		An independent instance.
		"""
		if not residue in self.get_residues():
			self._output.print_error(ot.errors.NO_SUCH_RESIDUE)

		n = copy.deepcopy(self)
		n._delete_residues_except(residue)
		return n

	def parse(self):
		"""
        Reads the input lines in :attr:`_lines`.

        Returns
        -------
        self
        	Allows for fluent interface.
		"""
		if self._parsed:
			return self
		lines = self._get_atom_lines()
		try:
			for line in lines:
				self._atoms.append(atom.from_pdb_line(line))
		except Exception, e:
			self._output.print_info('Parsing line %s' % line.strip())
			self._output.print_info(str(e))
			self._output.print_error(ot.errors.PARSE_ERROR)
		self._parsed = True
		return self

	def read_psf(self, stream):
		"""
		Creates a new :class:`psffile` from the data given in `stream`. The new internal :class:`psffile` instance is connected to the same :class:`~output_tracker.output_tracker` as `self`. Parsing applies relaxed standards.

		Parameters
		----------
		stream : List of strings, file object.
			Input lines in either format.

		Returns
		-------
		self
			Allows for fluent interface.
		"""
		self.parse()
		self._psf = psffile(stream, self._output)
		self._psf.parse()
		#if not self._psf.is_compatible(self._atoms):
		#	self._output.print_error(ot.errors.PSF_MISMATCH)

	def get_atom(self, index):
		"""
        Access method.

        Parameters
        ----------
        index : Integer
			Zero based index of the selected atom in :attr:`_atoms`.

		Returns
		-------
		:class:`~toto.atom.atom`
			Requested instance.
		"""
		try:
			return self._atoms[index]
		except:
			self._output.print_info('Retrieving atom with index %d' % index)
			self._output.print_error(ot.errors.UNKNOWN_INDEX)

	def get_index(self, name, residue=None):
		"""
        Extracts the index of a certain atom by atom name and residue.

        Parameters
        ----------
        name : String
        	Atom name
        residue : String
        	Residue name

        Returns
        -------
        Integer
        	Zero based index of the selected atom in :attr:`_atoms`.
		"""
		if residue is None:
			parts = name.split('.')
			if len(parts) == 2:
				residue, name = parts

		c = [(idx, a) for idx, a in enumerate(self._atoms) if a.get_name() == name]
		if len(c) == 0:
			self._output.print_error(ot.errors.UNKNOWN_ATOM_NAME)
		if residue is not None:
			c = [(idx, a) for idx, a in c if a.get_residue() == residue]
		if len(c) == 0:
			self._output.print_error(ot.errors.WRONG_RESIDUE)
		if len(c) > 1:
			self._output.print_error(ot.errors.AMBIGUOUS_ATOM_NAME)
		return c[0][0]

	def get_bond_vector(self, f, t, crucial=False):
		"""
        Calculates the direction of a bond. 

        Parameters
        ----------
        f : Integer
        	First atom index.
        t : Integer
        	Last atom index.
        crucial : Boolean
        	If `False`, calling this function with two nonbonded atoms will only raise a warning. If `True`, an error will occur in this case.

        Returns
        -------
        Tuple of floats
        	Bond vector in three dimensions.
		"""
		atom_f = self._atoms[f]
		atom_t = self._atoms[t]
		if not self._psf.is_bonded(f, t):
			if crucial:
				self._output.print_error(ot.errors.NO_SUCH_BOND)
			else:
				self._output.print_warn(ot.errors.NO_SUCH_BOND)

		return tuple(atom_f.get_vector_to(atom_t))

	def set_center_atom(self, a, residues=None):
		"""
        Moves all atoms such that a specific atom is in the origin of the internal coordinate system.

        Parameters
        ----------
        a : String, Integer, :class:`~toto.atom.atom` instance or list of floats. If string, the value is assumed to be a unique atom name. If integer, the value denotes the zero based index of the atom in :attr:`_atoms`. In case a list of floats is given as input, the vector defined by these three values is assumed to be the correct translation to perform.
        residues : Iterable of strings.
        	Contains the residue names that are movable. If `None`, all atoms are selected for translation.

        Returns
        -------
        self
        	Allows for fluent interface.
		"""
		dt = None
		if type(a) == str:
			a = self._atoms[self.get_index(a)]
		if type(a) == int:
			a = self._atoms[a]
		if isinstance(a, atom.atom):
			dt = map(lambda x: -x, a._pos)
		if type(a) == list:
			if len(a) != 3:
				self._output.print_error(ot.errors.NO_CARTESIAN_VECTOR)
			dt = a
		if dt is None:
			self._output.print_error(ot.errors.UNKNOWN_VECTOR)

		for a in self._atoms:
			if residues is None or a.get_residue() in residues:
				a.translate(dt)
		return self

	def rotate(self, n, angle, residues=None):
		"""
		Rotates all atoms.

		Parameters
		----------
		n : Iterable of floats
      		The normal vector of the rotation. 
      	angle : Float
      		The angle to rotate by in radians.
      	residues : Iterable of strings, None
      		Rotate only atoms that are part of the given residues. If `None`, all residues are rotated.

      	Returns
      	-------
      	self
      		Allows for fluent interface.
		"""
		if residues is None:
			map(lambda x: x.rotate(n, angle), self._atoms)
		else:
			map(lambda x: x.rotate(n, angle), [_ for _ in self._atoms if _.get_residue() in residues])
		return self

	def _get_atom_lines(self):
		"""
        Extracts all lines that form an atom description from the given source lines in :attr:`_lines`.

        Returns
        -------
        List
        	Strings containing atom definitions in plain PDB format. Lines contain terminal newline characters.
		"""
		relevant = [_ for _ in self._lines if _.startswith('HETATM')]
		relevant += [_ for _ in self._lines if _.startswith('ATOM ')]
		return relevant

	def get_residues(self):
		"""
        Lists all residue names given in the input lines held in :attr:`_lines`. Parsing applies relaxed standards.

  		Returns
  		-------
  		Set
  			Unique collection of residue names.
		"""
		# separate parsing with relaxed standards
		residues = [_[17:20].strip() for _ in self._get_atom_lines()]
		return set(residues)

	def _strip_bom(self):
		"""
        Removes any BOM from the beginning of the input file data in :attr:`_lines`.

        Returns
        -------
        self
        	Allows for fluent interface.
		"""
		for bom in (codecs.BOM, codecs.BOM_BE, codecs.BOM_LE, codecs.BOM_UTF8, codecs.BOM_UTF16, codecs.BOM_UTF16_BE, codecs.BOM_UTF16_LE, codecs.BOM_UTF32, codecs.BOM_UTF32_BE, codecs.BOM_UTF32_LE):
			if self._lines[0].startswith(bom):
				self._lines[0] = self._lines[0][len(bom):]

		return self

	def _add_residue(self, key):
		"""
        Internal helper updating the data structures to accomodate for another residue.

        Parameters
        ----------
        key : String
        	Residue name. May be replaced by anything that has a residue name as string representation.

        Returns
        -------
        self
        	Allows for fluent interface.
		"""
		if not key in self._residues:
			self._residues[str(key)] = dict()

	def _add_atom_name(self, residue, atom_name, line):
		"""
		Internal helper updating the data structures to accomodate for another atom.

		Returns
		-------
      	String or `None`
      		The previous definition line with the same atom name and the same residue. If no such line has been stored yet, the function returns `None`.
		"""
		self._add_residue(residue)
		if atom_name in self._residues[residue]:
			return self._residues[residue][atom_name]
		else:
			self._residues[residue][atom_name] = line
			return None

	def _is_left_justified(self, str):
		"""
        Checks whether a string is left-justified.

        Parameters
        ----------
        str : String
        	Input to check.

        Returns
        -------
        Boolean
		"""
		if len(str.strip()) == 0:
			return True
		return (str[0] != ' ')

	def _is_right_justified(self, str):
		"""
        Checks whether a string is right-justified.

        Parameters
        ----------
        str : String
        	Input to check.

        Returns
        -------
        Boolean
		"""
		return self._is_left_justified(str[::-1])

	def check_all(self):
		"""
        Checks the input lines in :attr:`_lines` for syntactic errors.

        Returns
        -------
        Boolean
        	True if everything is correct.
		"""
		if self._valid is None:
			if self._check_keywords():
				self._valid = self._check_HETATM()
			else:
				self._valid = False
		return self._valid

	def _found_error(self, idx, msg, got):
		"""
        Helper function for error handling.

        Parameters
        ----------
        idx : Integer
        	One based line number.
        msg : String
        	Hint on what is wrong with this line.
        got : String
        	Hint on what was expected by the parser in this line.

        Returns
        -------
        False
		"""
		self._output.print_warn(ot.errors.PARSE_ERROR).add_level()
		msg = 'line %d: %s' % (idx, msg)
		if not got is None:
			msg += ', got >%s<' % got
		self._output.print_info(msg).del_level()
		return False

	def _check_keywords(self):
		"""
        Checks all keywords in the input data in :attr:`_lines` for validity.

        Returns
        -------
        Boolean
        	True if everything is correct.
		"""
		success = True
		for idx, line in enumerate(self._lines):
			if len(line) != 81:
				success = self._found_error(idx+1, 'expected 80 characters in line', None)
			if line[0:6] not in [
				'HEADER', 'OBSLTE', 'TITLE ', 'SPLT  ', 'CAVEAT',
				'COMPND', 'SOURCE', 'KEYWDS', 'EXPDTA', 'NUMMDL',
				'MDLTYP', 'AUTHOR', 'REVDAT', 'SPRSDE', 'JRNL  ',
				'REMARK', 'DBREF ', 'DBREF1', 'DBREF2', 'SEQADV',
				'SEQRES', 'MODRES', 'HET   ', 'FORMUL', 'HETNAM',
				'HETSYN', 'HELIX ', 'SHEET ', 'SSBOND', 'LINK  ',
				'CISPEP', 'SITE  ', 'CRYST1', 'MODEL ', 'ATOM  ',
				'ANISOU', 'TER   ', 'HETATM', 'ENDMDL', 'CONECT', 
				'MASTER','END   '] and not line[0:5] in ['ORIGX', 'SCALE', 'MTRIX']:
				success = self._found_error(idx+1, 'unknown keyword', line[0:6])
				print line.strip()[0:4]

		return success

	def _check_HETATM(self):
		"""
        Strict lint of all HETATM lines in the input data in :attr:`_lines`. 

        Prints messages on invalid lines via :attr:`_output`.

        Returns
        -------
        Boolean
      		True if everything is correct.
		"""
		success = True
		relevant = [(idx, line) for idx, line in enumerate(self._lines) if line.startswith('HETATM')]

		for idx, line in relevant:
			if not line[6] is ' ':
				success = self._found_error(idx+1, 'expected space at character 7', line[6])
			for match in re.finditer('[^0-9 ]+', line[6:11]):
				success = self._found_error(idx+1, 'only integer atomic serial numbers allowed', line[6:11])
			atom_name = line[12:16]
			residue = line[17:20]
			match = self._add_atom_name(residue, atom_name, idx+1)
			if not match is None:
				success = self._found_error(idx+1, 'non unique atom names (previous definition at line %d)' % match, None)
			try:
				coord_x = float(line[30:38])
			except ValueError:
				success = self._found_error(idx+1, 'conversion to float for x coordinate failed', line[30:38])
			try:
				coord_y = float(line[38:46])
			except ValueError:
				success = self._found_error(idx+1, 'conversion to float for y coordinate failed', line[38:46])
			try:
				coord_y = float(line[46:54])
			except ValueError:
				success = self._found_error(idx+1, 'conversion to float for z coordinate failed', line[46:54])
			try:
				coord_y = float(line[54:60])
			except ValueError:
				success = self._found_error(idx+1, 'conversion to float for occupancy failed', line[54:60])
			try:
				coord_y = float(line[60:66])
			except ValueError:
				success = self._found_error(idx+1, 'conversion to float for temperature factor failed', line[60:66])
			if not self._is_left_justified(line[72:76]):
				success = self._found_error(idx+1, 'Segment identifier not left left-justified', line[72:76])
			if not self._is_right_justified(line[76:78]):
				success = self._found_error(idx+1, 'Element symbol is not left right-justified', line[76:78])
			try:
				charge = int(line[78])
			except ValueError:
				success = self._found_error(idx+1, 'Non-integer charge', line[78])
			if line[79] not in ['+', '-']:
				success = self._found_error(idx+1, 'Invalid charge sign', line[79])

		return success

	def to_pdb_file(self, filename):
		"""
       	Write string representation of the parsed PDB information to file.

       	.. todo::
       		Error checking on file opening.

       	Parameters
       	----------
       	filename : String
       		The target filename.

       	Returns
       	-------
       	self
       		Allows for fluent interface.
		"""
		fh = open(filename, 'w')
		fh.write(self.get_pdb_string(renumber=True))
		return self

	def to_psf_file(self, filename):
		"""
        Write string representation of the parsed PSF information to file.

       	.. todo::
       		Error checking on file opening.

        Parameters
        ----------
        filename : String
        	The target filename.

        Returns
        -------
        self
        	Allows for fluent interface.
		"""
		fh = open(filename, 'w')
		fh.write(self.get_psf_string())
		return self

	def translate_residue(self, residue_name, vector):
		"""
        Shifts all atoms for a specific residue after consistency checks.

        Parameters
        ----------
        residue_name : String
        	The residue that should be translated.
        vector : Iterable of floats
        	Iterable of length 3.

        Returns
        -------
        self
        	Allows for fluent interface.
		"""
		if residue_name not in self.get_residues():
			self._output.print_info('Requested to move residue %s' % residue_name).add_level()
			self._output.print_error(ot.errors.NO_SUCH_RESIDUE)
		for a in self._atoms:
			if a.get_residue() == residue_name:
				a.translate(vector)
		return self

	def translate(self, vector):
		"""
        Shifts all atoms.

        Parameters
        ----------
        vector : Iterable of floats
        	Iterable of length 3.

        Returns
        -------
        self
        	Allows for fluent interface.
		"""
		for a in self._atoms:
			a.translate(vector)
		return self

def join_pdb(one, another, purge_metadata=False):
	"""
	Joins two PDB files while maintaining topology information from associated PSF files.

	Parameters
	----------
	one : :class:`PDBFile`
		Instance to be merged that will occurr first in the resulting file.
	another : :class:`PDBFile`
		Instance to be merged that will come second in the output file.
	purge_metadata : Boolean
		Whether to remove any entries from the output file that does not describe an atom position except the ones that precede any atom definition. Usually, this purges any metadata from `another`.

	Raises
	------
	ValueError :
		If any of the associated topologies contain unrecoverable errors.

	Returns
	-------
	:class:`PDBFile`
		Combined file with corrected PSF topology data.
	"""
	if not one._valid and another._valid:
		raise ValueError('Unable to join: invalid input files.')

	if not one._parsed:
		one.parser()
	if not another._parsed:
		another.parse()

	lines = [_ for _ in one._lines if not _.startswith('END')] + another._lines
	c = pdbfile(lines, one._output)
	c._residues = copy.deepcopy(one._residues)
	c._residues.update(another._residues) 
	c._valid = True
	c._atoms = [copy.deepcopy(_) for _ in one._atoms] + [copy.deepcopy(_) for _ in another._atoms]
	c._parsed = True

	# psf
	shift = len(one._atoms)
	c._psf = copy.deepcopy(one._psf)
	n_atoms = copy.deepcopy(another._psf._atoms)
	for atom in n_atoms:
		atom.set_psf_number(atom.get_psf_number()+shift)

	c._psf._atoms += n_atoms
	for a, b in another._psf._bonds:
		c._psf._bonds.append((a+shift, b+shift))
	for a, b, d in another._psf._angles:
		c._psf._angles.append((a+shift, b+shift, d+shift))
	for a, b, d, e in another._psf._dihedrals:
		c._psf._dihedrals.append((a+shift, b+shift, d+shift, e+shift))
	for a, b, d, e in another._psf._impropers:
		c._psf._impropers.append((a+shift, b+shift, d+shift, e+shift))
	
	if purge_metadata:
		c.purge_metadata(except_first=True)

	return c
