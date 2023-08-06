#!/usr/bin/env python
# -*- coding: utf-8 -*-

# system modules
import argparse
import sys

# third-party modules
import numpy as np

# custom modules
import f_core as fc
import output_tracker as ot

# command line parsing
parser = argparse.ArgumentParser(description='Creates binned 1d and 2d data read from stdin.')
parser.add_argument('mode', choices=('1d', '2d'))

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--num_bins', type=int, nargs='+', help='Number of bins to use.')
group.add_argument('--bins', type=str, nargs='+', help='Bins to use.')

parser.add_argument('--min_val', type=float, nargs='+', help='Value of the lower binning border.')
parser.add_argument('--max_val', type=float, nargs='+', help='Value of the upper binning border.')

parser.add_argument('--comment_string', type=str, help='If a line begins with this string, it will be skipped', default='#')
parser.add_argument('--density', help='Whether to print density instead of absolue occurences.', action='store_true')
parser.add_argument('--die_on_error', help='Whether to be strict with input data.', action='store_true')
parser.add_argument('--format_complain', help='Whether to report empty or ill-formatted lines.', action='store_true')
parser.add_argument('--range_complain', help='Whether to report out-of-range values.', action='store_true')
parser.add_argument('--convert_complain', help='Whether to report non-numeric values.', action='store_true')
parser.add_argument('--output_mode', help='How to represent the histogram data.', choices=('matrix', 'xyz', 'xyzm'), default='matrix')

def _check_borders(dimensions, min_val, max_val, fixed_bins, output):
	"""
	Checks validity of specified borders. In particular, borders are required in case only a number of bins has been specified.

	Parameters
	----------
	dimensions : Integer
		Dimenionality of the input data. Either 1 or 2.
	min_val : Iterable, None
		List of floats denoting the minimal values of the valid data range. If `None`, the range is unspecified.
	max_val : Iterable, None
		List of floats denoting the maximal values of the valid data range. If `None`, the range is unspecified.
	fixed_bins : Boolean
		Whether information on the bin positions is already available.
	output : :class:`output_tracker` instance
	  Error reporting.
	"""
	if fixed_bins:
		if min_val is not None or max_val is not None:
			output.print_info('Got fixed bins.')
			output.print_warn(fc.messages.BOUNDS_IGNORED)
			return

	if len(min_val) != dimensions or len(max_val) != dimensions:
		output.print_error(fc.messages.BOUNDS_DIMENSION)

	for min_v, max_v in zip(min_val, max_val):
		if min_v > max_v:
			output.print_info('Got bounds %f and %f.' % (min_v, max_v))
			output.print_error(fc.messages.BOUNDS_REVERSED)
		if min_v == max_v:
			output.print_info('Got bounds %f and %f.' % (min_v, max_v))
			output.print_error(fc.messages.BOUNDS_EQUAL)

def _bin_list_1d(min_val, max_val, bins, num_bins, output):
	if bins is not None:
		if sorted(bins) != bins:
			output.print_warn(fc.messages.BINS_SORTED)
		if len(bins) < 1:
			output.print_error(fc.messages.BIN_COUNT_LEQ_Z)
		return np.array(sorted(bins))

	if num_bins[0] < 1:
		output.print_error(fc.messages.BIN_COUNT_LEQ_Z)
	return np.linspace(min_val[0], max_val[0], num=num_bins[0]+1)

def _bin_list_2d(min_val, max_val, bins, num_bins, output):
	if bins is not None:
		parts = bins.split(';')
		if len(parts) != 2:
			output.print_error(fc.messages.BINS_2D_SPEC)

		x, y = parts
		try:
			x = map(float, x.split(','))
			y = map(float, y.split(','))
		except:
			output.print_info('Got %s.' % bins)
			output.print_error(fc.messages.CONVERT_FAILED)

		if x != sorted(x) or y != sorted(y):
			output.print_warn(fc.messages.BINS_SORTED)

		x = sorted(x)
		y = sorted(y)
	else:
		x = np.linspace(min_val[0], max_val[0], num=num_bins[0]+1)
		y = np.linspace(min_val[1], max_val[1], num=num_bins[-1]+1)

	if len(x) < 1 or len(y) < 1:
		output.print_error(fc.messages.BIN_COUNT_LEQ_Z)

	return (x, y)

def main():
	"""
	Main wrapper.
	"""
	# parse command line
	args = parser.parse_args()
	output = ot.output_tracker()

	output.print_info('Checking options.').add_level()
	fixed_bins = (args.bins is not None)
	mode = args.mode
	if mode == '1d':
		_check_borders(1, args.min_val, args.max_val, fixed_bins, output)
	if mode == '2d':
		_check_borders(2, args.min_val, args.max_val, fixed_bins, output)
	output.del_level()

	# build bin list
	output.print_info('Building bin list.').add_level()
	if mode == '1d':
		bins = _bin_list_1d(args.min_val, args.max_val, args.bins, args.num_bins, output)
		data = [0] * (len(bins)-1)
	if mode == '2d':
		bins_x, bins_y = _bin_list_2d(args.min_val, args.max_val, args.bins, args.num_bins, output)
		t = [0] * (len(bins_y)-1)
		data = [t[:] for _ in range(len(bins_x)-1)]
	output.del_level()

	# read stdin
	output.print_info('Parsing data.').add_level()
	dimension = int(mode[0])
	collected = 0
	for line in sys.stdin:
		if line.startswith(args.comment_string):
			continue

		parts = line.strip().split()
		if len(parts) != dimension:
			if args.format_complain:
				output.print_info('Got line %s' % line.strip())
				if args.die_on_error:
					output.print_error(fc.messages.EMPTY_LINE)
				else:
					output.print_warn(fc.messages.EMPTY_LINE)
			continue

		try:
			parts = map(float, parts)
		except:
			if args.convert_complain:
				output.print_info('Got line %s' % line.strip())
				if args.die_on_error:
					output.print_error(fc.messages.CONVERT_FAILED)
				else:
					output.print_warn(fc.messages.CONVERT_FAILED)
			continue

		out_of_range = False
		if mode == '1d':
			if parts[0] < bins[0] or parts[0] > bins[-1]:
				out_of_range = True
		if mode == '2d':
			if parts[0] < bins_x[0] or parts[0] > bins_x[-1]:
				out_of_range = True
			if parts[1] < bins_y[0] or parts[1] > bins_y[-1]:
				out_of_range = True
		if out_of_range:
			if args.range_complain:
				output.print_info('Got line %s' % line.strip())
				if args.die_on_error:
					output.print_error(fc.messages.OUT_OF_BOUNDS)
				else:
					output.print_warn(fc.messages.OUT_OF_BOUNDS)
			continue

		if mode == '1d':
			idx = np.searchsorted(bins, parts[0], side='left')
			data[idx-1] += 1
		if mode == '2d':
			idx_x = np.searchsorted(bins_x, parts[0], side='left')
			idx_y = np.searchsorted(bins_y, parts[1], side='left')
			data[idx_x-1][idx_y-1] += 1

		collected += 1

	output.del_level()

	scaling = 1 if collected == 0 else 1/float(collected)
	if args.output_mode == 'matrix':
		if mode == '2d':
			for a in data:
				for b in a:
					print b*scaling,
				print
		if mode == '1d':
			for a in data:
				print a*scaling

	if args.output_mode.startswith('xyz'):
		if mode == '1d':
			for ia, a in enumerate(data):
				xval = (bins[ia+1]+bins[ia])/2
				print xval, a
		if mode == '2d':
			for ia, a in enumerate(data):
				if args.output_mode[-1] == 'm':
					xval = (bins_x[ia+1]+bins_x[ia])/2
				else:
					xval = bins_x[ia]
				for ib, b in enumerate(a):
					if args.output_mode[-1] == 'm':
						yval = (bins_y[ib+1]+bins_y[ib])/2
					else:
						yval = bins_y[ib]
					print xval, yval, b*scaling
				if args.output_mode[-1] != 'm':
					print xval, bins_y[-1], a[-1]*scaling
				print 
			if args.output_mode[-1] != 'm':
				for idx, i in enumerate(data[-1]):
					print bins_x[-1], i, data[-1][idx]*scaling
				print bins_x[-1], bins_y[-1], data[-1][-1]*scaling

if __name__ == '__main__':
	main()