#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extracts positional data from MD trajectories. The output can be filtered simultaneously by frame selections and CHARMM-style atom selections.

Examples
--------

Extracts frame 100, 200, and 300 from membrane.dcd.

.. code:: sh
   
   f_extract.py membrane.psf membrane.dcd output.dcd --frames 100:301:100

Extracts the complete trajectories of all atoms that are at most five Angstroms away from the origin in frame 10 (the eleventh frame) while wrapping atom coordinates periodically back to the simulation box.

.. code:: sh
  
   f_extract.py membrane.psf membrane.dcd output.dcd \\
		--charmm 'point 0.0 0.0 0.0 5.0' \\
		--selection_frame 10 \\
		--periodic

Extracts the last frame of a trajectory.

.. code:: sh

   f_extract.py membrane.psf membrane.dcd output.dcd --frames -1

Shows usage.

.. code:: sh

   f_extract.py -h

Supported formats
-----------------

All file formats of :ref:`MDAnalysis <supported coordinate formats>` are supported. Input files may be compressed using gzip or bzip2.

.. note:: File formats are recognized by file extension. Therefore, you have to stick to the standard file extensions.

.. note:: Some output formats may only support writing a single frame.

.. warning:: Only rectangular simulation boxes are currently supported.

Command line interface
----------------------

.. program:: f_extract.py

.. option:: topology

   The topology file to work with. 

.. option:: coordinates

   The coordinate file to work with.

.. option:: output

   Output file to write to.

.. option:: --frames

   The zero-based frame selection that allows for slicing. The general syntax is 'start:stop:step' which would select all frames from `start` to `stop` (excluding `stop`) while skipping `step` frames inbetween. Selecting single frames by specifying a single number is possible. Negative indices count backwards from the end of the trajectory.

.. option:: --charmm

   Please refer to the :ref:`section <atomselections>` on atom selections.

.. option:: --selection_frame

   Input frame to select on (zero-based). Only interesting for geometric criteria.

.. option:: --progress

   Progress report every time this many frames have been written.

.. option:: --force

   Whether to overwrite existing output files.

.. option:: --periodic

   Whether to wrap atoms for spatial selection criteria back to the original cell.

Open Issues
-----------

.. todo:: Single frame PDB output not functional.

.. todo:: Progress output: wrap last line.

.. todo:: Allow for comma-separated list of frames.

Internal functions
------------------
"""

# system modules
import argparse
import os
import os.path as path

# custom modules
import f_core as fc
import output_tracker as ot

# command line parsing
parser = argparse.ArgumentParser(description='Extracts positional data from MD trajectories.')
parser.add_argument('topology', type=str, help='The topology to work with.')
parser.add_argument('coordinates', type=str, help='The coordinates to work with.')
parser.add_argument('output', type=str, help='The coordinate file to write to.')
parser.add_argument('--frames', type=str, help='Frame selection.', default='all')
parser.add_argument('--charmm', type=str, help='CHARMM selection syntax.', default=None)
parser.add_argument('--selection_frame', type=int, help='Input frame to select on (zero-based).', default=0)
parser.add_argument('--progress', type=int, help='Progress report every time this many frames have been written.', default=100)
parser.add_argument('--force', help='Whether to overwrite existing files.', action='store_true')
parser.add_argument('--periodic', help='Whether to wrap atoms for spatial selection criteria back to the original cell.', action='store_true')

def main():
	"""
	Wrapper function.
	"""
	output = ot.output_tracker()
	mda = fc._require_mda(output)
	args = parser.parse_args()

	# messages
	messages = fc.messages

	# read input
	output.print_info('Reading source files.').add_level()
	output.print_info('Opening file %s.' % args.topology)
	output.print_info('Opening file %s.' % args.coordinates)

	# create Universe
	fc.mda_set_periodic(args.periodic, output)
	u = fc.mda_load_universe(args.topology, args.coordinates, output)
	output.print_info('Coordinate file holds %d frames.' % len(u.trajectory)).del_level()

	# parse frame selection
	f_sel = fc.parse_frame_selection(args.frames, output)

	# calculate number of frames
	numframes = fc.mda_get_framecount(universe, selection, output)
	if numframes is None:
		numframes = 0

	output.print_info('Starting extraction.').add_level()
	if not args.force and path.exists(args.output):
		output.print_error(messages.OUTPUT_EXISTS)

	curframe = 1
	if args.selection_frame < 0:
		args.selection_frame + len(u.trajectory)
	if args.selection_frame > len(u.trajectory):
		output.print_info('Selection frame is %d' % args.selection_frame)
		output.print_error(messages.INVALID_FRAME_SEL)

	initial_selection = fc.mda_select(u, args.charmm, output, args.selection_frame)
	output.print_info('Selected %d atoms.' % len(atom_nums))

	try:
		writer = mda.Writer(args.output, len(atom_nums))
	except Exception, e:
		output.print_info('MDAnalysis: %s' % str(e))
		output.print_error(messages.OUTPUT_FAILED)

	def print_stat(curframe, numframes, outfile, overwrite=True):
		statinfo = os.stat(outfile)
		output.print_info('Completed frame %8d/%8d. File size %6dMB.' % (curframe, numframes, statinfo.st_size/1024/2024), overwrite=overwrite)

	outfile = args.output
	for ts in u.trajectory[f_sel]:
		if curframe % args.progress == 0:
			print_stat(curframe, numframes, outfile, overwrite=True)
		curframe += 1
		writer.write(initial_selection.ts)
	writer.close()

	print_stat(numframes, numframes, outfile, overwrite=False)
	output.print_info('Finished extraction.')

if __name__ == '__main__':
	main()