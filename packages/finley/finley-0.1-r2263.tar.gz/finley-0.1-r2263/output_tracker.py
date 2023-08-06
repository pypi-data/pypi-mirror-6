#!/usr/bin/env python
import sys 

class errors(object): #isdoc
	NO_MODE_AND_INPUT 			= (1, 'Mode and input file missing.')
	NO_OUTPUT 					= (2, 'No output file given.')
	OUTPUT_PRESENT 				= (3, 'Output file already present.')
	NO_Z_MATRIX 				= (4, 'No Z-matrix found.')
	UNEXPECTED_EOF 				= (5, 'Unexpected end of file.')
	INCOMPLETE_COORD 			= (6, 'Incomplete coordinate set.')
	PARSE_ERROR 				= (7, 'Parse error(s).')
	NO_CONFORMATIONS			= (8, 'No conformations found.')
	UNKNOWN_MODE        		= (9, 'Unknown operation mode.')
	MULTIPLE_KEYPRESS			= (10, 'Please stick to one key press at a time.')
	NO_SAMPLES					= (11, 'No samples to work with.')
	BEAT_MISMATCH 				= (12, 'Discarding samples due to beat count mismatch.')
	SAMPLE_NONEMPTY				= (13, 'Sample already recorded.')
	ONE_SAMPLE					= (14, 'Only one sample left.')
	PREMATURE_KEYPRESS  		= (15, 'First keypress before initialization was complete.')
	SAMPLE_EMPTY				= (16, 'Sample contains no beats.')
	USE_CACHED					= (17, 'Using cached values.')
	VIOLATED_CONSTRAINT 		= (18, 'Constraint violated.')
	CACHE_OUTDATED				= (19, 'Cached data is outdated.')
	INTERNAL_ERROR				= (20, 'Internal error.')
	UNSUPPORTED_FORMAT			= (21, 'Unsupported format.')
	POSSIBLE_ISSUE 				= (22, 'Possible issue. Please check.')
	MISSING_FRAMES				= (23, 'Unknown parameter frames.')
	MISSING_ATOMS				= (24, 'Unknown parameter frames.')
	NOT_IMPLEMENTED				= (25, 'Feature not implemented.')
	EMPTY_ATOM_LABEL			= (26, 'Empty atom label.')
	NO_PARAMETER_FILES			= (27, 'No force-field parameter files found.')
	CGENFF_OMITTED				= (28, 'Data from CGenFF found but omitted.')
	FILE_IGNORED				= (29, 'Ignoring file.')
	CHARMM_OMITTED				= (30, 'CHARMM parameter file omitted.')
	UNKNOWN_REQUEST				= (31, 'Read unknown request.')
	NO_D_MATRIX 				= (32, 'No distance matrix found.')
	NO_RESIDUE	 				= (33, 'At least one residue has to be specified.')
	TOO_MANY_RESIDUES			= (34, 'Only one residue can be analyzed at a time.')
	NO_REFERENCE_DATA			= (35, 'No reference data found.')
	NO_SCF_DATA					= (36, 'No SCF energies found.')
	NOT_CONVERGED				= (37, 'Geometric optimization did not converge.')
	GROUP_NOT_FOUND				= (38, 'Unable to select group.')
	AMBIGUOUS_KEY				= (39, 'Found multiple publications with the same citation key.')
	UNKNOWN_KEY					= (40, 'Found no publication with this citation key.')
	NO_DOI						= (41, 'No DOI entry found.')
	NO_JOURNAL					= (42, 'No journal entry found.')
	NO_ISSUE					= (43, 'No issue entry found.')
	NO_PAGES					= (44, 'No pages entry found.')
	NO_VOLUME					= (45, 'No volume entry found.')
	NO_YEAR						= (46, 'No year entry found.')
	NO_AUTHORS					= (47, 'No authors entry found.')
	BRACKET_MISMATCH			= (48, 'Different number of opening and closing brackets.')
	SYNTAX_COLON				= (49, 'Syntax error: wrong number of colons.')
	TARGET_VECTOR				= (50, 'Target vector not recognized.')
	BONDSPEC					= (51, 'Odd number of entries for bond specification.')
	BOND_CONV					= (52, 'Unable to convert bond indices to integers.')
	COMMAND						= (53, 'Error parsing command input.')
	UNKNOWN_ATOM_NAME			= (54, 'Atom name not found.')
	NO_SUCH_BOND				= (55, 'The given atoms are not connected by a bond.')
	UNKNOWN_VECTOR				= (56, 'The given vector is not a valid displacement.')
	ROTATION_I					= (57, 'The given rotation is the identity operation.')
	WRONG_RESIDUE				= (58, 'This atom name is only valid for another residue.')
	AMBIGUOUS_ATOM_NAME			= (59, 'This atom name is not unique for this residue or no residue given.')
	FIXED_RESIDUE				= (60, 'Atoms to rotate belong to a fixed residue.')
	NO_SUCH_RESIDUE				= (61, 'There is no residue with this name.')
	PSF_MISMATCH				= (62, 'The given PSF does not match the specified PDB file.')
	DOUBLE_PSF_SECTION			= (63, 'At least one section in the PSF is doubled.')
	PSF_BOND_NUMBER				= (64, 'Inconsistent number of bonds in PSF.')
	PSF_ATOM_NUMBER				= (65, 'Inconsistent number of atoms in PSF.')
	PSF_ATOM_UNIQUE				= (66, 'Non-unique atom number in PSF.')
	PSF_CONTIGUOUS				= (67, 'Atom numbers not contiguous in PSF.')
	ANGLESPEC					= (68, 'Number of entries for angles in PSF not a multiple of 3.')
	PSF_ANGLE_NUMBER			= (69, 'Inconsistent number of angles in PSF.')
	ANGLE_CONV					= (70, 'Unable to convert bond angle indices to integers.')
	DIHEDRAL_CONV				= (71, 'Unable to convert dihedral indices to integers. ')
	DIHEDRALSPEC				= (72, 'Number of entries for dihedrals in PSF not a multiple of 4.')
	PSF_DIHEDRAL_NUMBER 		= (73, 'Inconsistent number of dihedrals in PSF.')
	IMPROPERSPEC				= (74, 'Number of entries for impropers in PSF not a multiple of 4.')
	IMPROPER_CONV				= (75, 'Unable to convert improper indices to integers.')
	PSF_IMPROPER_NUMBER			= (76, 'Inconsistent number of impropers in PSF.')
	PSF_NO_ATOMS				= (77, 'PSF contains no atoms.')
	EMPTY_INPUT					= (78, 'Input contains no (readable) data.')
	PSF_REQUIRED				= (79, 'You have to load a PSF for this operation.')
	NAMD_NO_KEY_VAL				= (80, 'A line in the namd config file does not hold a key-value pair.')
	NAMD_NO_PDB					= (81, 'Namd config file does not reference any PDB files.')
	NAMD_MULTIPLE_PDB			= (82, 'Namd config file references multiple PDB files.')
	NAMD_NO_PSF					= (83, 'Namd config file does not reference any PSF.')
	NAMD_MULTIPLE_PSF			= (84, 'Namd config file references multiple PSF.')
	NAMD_NOT_CHARMM				= (85, 'Namd config file does not select CHARMM parameter format.')
	NAMD_NO_PRM					= (86, 'Namd config file does not reference any parameter files.')
	NO_NAMD_RUNFILE				= (87, 'No namd config file known.')
	NAMD_FAILED					= (88, 'Executing namd failed.')
	NAMD_CONVERGED				= (89, 'Optimization run did not converge.')
	PARSE_ENERGY				= (90, 'Failed to parse energy.')
	PDB_TOTAL_CHARGE			= (91, 'Total charge is nonzero.')
	CHARGE_PARSE				= (92, 'Unable to recognize charge request.')
	NO_SUCH_ATOM_TYPE			= (93, 'Unable to find the requested atom type.')
	NAMD_TRAJ_PARSE				= (94, 'Unable to parse namd trajectory.')
	EXPECTED_ATOM				= (95, 'Expected atom instance.')
	NAMD_NO_DCD					= (96, 'Namd config file does not reference any trajectory.')
	NAMD_MULTIPLE_DCD			= (97, 'Namd config file references multiple trajectories.')
	NAMD_NO_CONS_K_FILE			= (98, 'Namd config file does not reference a constraint forces file.')
	NAMD_MULTIPLE_CONS_K_FILE 	= (99, 'Namd config file references multiple constraint forces files.')
	NAMD_NO_CONS_FILE 			= (100, 'Namd config file does not reference a constraint file.')
	NAMD_MULTIPLE_CONS_FILE 	= (101, 'Namd config file references multiple constraint files.')
	UNKNOWN_INDEX				= (102, 'No atom with this index.')
	NO_CARTESIAN_VECTOR			= (103, 'The positional vector given is not a valid vector in cartesian coordinates.')
	NO_GAUSSIAN_OUTPUT			= (104, 'No Gaussian output files found.')
	UNKNOWN_VMD_IDENTIFIER		= (105, 'Atom identifier not found in output. Input file mismatch?')
	SELECTION_MISMATCH			= (106, 'Less atoms in output than requested.')
	VMD_FILENAME_DAMAGED		= (107, 'Unable to parse filename from VMD fftk.')
	ATOM_NUMBER_MISMATCH		= (108, 'Atom number in logfile does not match atom number in reference file.')
	GAU_NOT_ALIGNED				= (109, 'The analyzed bonds are not on the same axis. Constraint violation?')
	NAMD_NO_MINIMIZE			= (110, 'Namd config file does not contain any minimization request.')
	NAMD_MULTIPLE_MINIMIZE		= (111, 'Namd config file contains multiple minimization requests.')
	DISTANCE_CORRECTION			= (112, 'Initial align distance has to be corrected.')
	OMITTED_TAINTED_LINE		= (113, 'Omitting line containing tainted data.')
	OMITTED_DUPLICTED_POINT		= (114, 'Omitting line containing a variant of a previous datapoint.')
	LINE_NO_STRING				= (115, 'The given line is not convertible to a string.')
	NO_CHARMM_BOND_DEF			= (116, 'The given line does not contain a valid charmm bond definition.')
	KB_NO_FLOAT					= (117, 'Force constant non convertible to float.')
	B0_NO_FLOAT					= (118, 'Equilibrium distance non convertible to float.')
	DUPLICATE_ATOM_TYPE			= (119, 'Duplicate atom type.')
	EXPECTED_CHARMMFILE			= (120, 'Expected charmmfile instance.')
	AMBIGUOUS_ATOM_MERGE		= (121, 'Got ambiguous data for atom types during merge operation.')
	NO_CHARMM_ANGLE_DEF			= (122, 'The given line does not contain a valid charmm angle definition.')
	COMMENT_NO_STRING			= (123, 'Comment data not convertible to a string.')
	UB_DIST_NO_FLOAT			= (124, 'Urey-Bradley distance data not convertible to a float.')
	UB_KB_NO_FLOAT				= (125, 'Urey-Bradley force constant data not convertible to a float.')
	KB_NO_FLOAT					= (126, 'Force constant data not convertible to a float.')
	ANGLE_NO_FLOAT				= (127, 'Angle not convertible to a float.')
	DELTA_NO_FLOAT				= (128, 'Dihedral delta not convertible to a float.')
	MULTIPLICITY_NO_INT			= (129, 'Multiplicity not convertible to int.')
	NO_CHARMM_DIHEDRAL_DEF		= (130, 'The given line does not contain a valid charmm dihedral definition.')
	NO_CHARMM_IMPROPER_DEF		= (131, 'The given line does not contain a valid charmm improper definition.')
	NO_DATA_FOR_ELEMENT			= (132, 'No data found for this element name.')
	NO_DATA_FOR_ATOM_TYPE		= (133, 'No data found for this atom type.')
	CHARMMTOP_ATOM_DEF			= (134, 'Invalid ATOM definition in charmm topology file.')
	CHARMMTOP_BOND_DEF			= (135, 'Invalid BOND definition in charmm topology file.')
	CHARMMTOP_AMBIGUOUS_NAME	= (136, 'An atom name is used twice in a single residue.')
	CHARMMTOP_UNDEF_NAME		= (137, 'Charmm topology file references undefined atom name.')
	CHARMMTOP_PURELY_EXT		= (138, 'Purely external bonds not acceptable in charmm topology file.')
	RESNAME_NO_STRING			= (139, 'Residue name given is not convertible to a string.')
	EXPECTED_CHARMMRESFILE		= (140, 'Expected charmmresfile instance.')
	AMBIGUOUS_RESIDUE_MERGE		= (141, 'Got ambiguous data for residues during merge operation.')
	NO_TOPOLOGY_FILES			= (142, 'No topology data found.')
	NAMD_NO_COLVARS				= (143, 'Namd config file does not reference any collective variable file.')
	NAMD_MULTIPLE_COLVARS		= (144, 'Namd config file references multiple collective variable files.')
	DCD_NOT_FOUND				= (145, 'The specified DCD trajectory could not be read.')
	PSF_LINE_NO_CONV			= (146, 'Line count of PSF section is not an integer.')

# sanity check for error codes
codes = [x[1][0] for x in vars(errors).items() if x[0].upper() == x[0]]
if len(codes) != len(set(codes)):
	raise TypeError('Duplicate error code.')

class null_output(object): #isdoc
	def __getattribute__(self, name): #isdoc
		def print_error(error):  #isdoc
			raise Exception(error[1])

		if name == 'print_error':
			return print_error
		return lambda x=None: self

class output_tracker(object): #isdoc #doc-contains: _stdout, _indent, _indent_steps, _quiet, _colors
	def __enter__(self): #isdoc
		self._stdout = sys.stdout
		sys.stdout = self

	def __exit__(self, exc_type, exc_value, traceback): #isdoc
		sys.stdout = self._stdout

	def __init__(self): #isdoc
		self._indent = 0
		self._indent_steps = 3
		self._stdout = sys.stdout
		self._quiet = False

		# bash color codes
		self._colors = dict([
			('red', '0;31'), 
			('green', '0;32'),
			('brown', '0;33'),
			('default', '0')
			])

	def write(self, text): #isdoc
		self.print_info(text.strip('\n'))

	def flush(self): #isdoc
		pass

	def _print_multiline(self, prefix, message, color, overwrite=False):
		if len(prefix) not in  [0, 2]:
			raise ValueError('Internal Error: Wrong prefix length.')
		if prefix != '':
			prefix += ' '
		if type(message) != str:
			message = str(message)

		parts = message.split('\n')
		if len(parts) != 1:
			overwrite = False
		target = self._stdout
		if not target.isatty():
			target = sys.stderr
		if overwrite:
			target.write('\r')
		target.write('{1}\033[{3}m{0}\033[0m{2}'.format(
			prefix.upper(), 
			' ' * self._indent, 
			parts[0], 
			color
			))
		if overwrite:
			target.flush()
		else:
			target.write('\n')
		
		for part in parts[1:]:
			target.write(' {0}{1}\n'.format(' ' * (self._indent + 2), part))

	def print_error(self, code): #isdoc
		if not type(code[0]) is int:
			raise ValueError('Error code is not numeric.')
		self._print_multiline(
			'EE', 
			code[1] + (' (error code %d)' % code[0]), 
			self._colors['red']
			)
		raise Exception('Exception for traceback.')

	def print_warn(self, code): #isdoc
		if not type(code[0]) is int:
			raise ValueError('Warning code is not numeric.')
		self._print_multiline(
			'WW', 
			code[1] + (' (warning code %d)' % code[0]), 
			self._colors['brown']
			)
		return self

	def set_quiet(self, value): #isdoc
		self._quiet = value
		return self

	def get_quiet(self): #isdoc
		return self._quiet

	def print_info(self, message, parseable=None, overwrite=False):
		if not parseable is None:
			message = message % parseable

		if self._quiet:
			if not parseable is None:
				return self.print_plain(message)
			else:
				return self
		else:
			self._print_multiline('II', message, self._colors['green'], overwrite=overwrite)
			return self

	def add_level(self): #isdoc
		if not self._quiet:
			self._indent += self._indent_steps
		return self

	def del_level(self, depth=1): #isdoc
		if not self._quiet:
			self._indent -= self._indent_steps*depth
		if self._indent < 0:
			raise ValueError('Leftmost indentation level reached.')
		return self

	def print_plain(self, message): #isdoc
		self._print_multiline('', message, self._colors['default'])
		return self
