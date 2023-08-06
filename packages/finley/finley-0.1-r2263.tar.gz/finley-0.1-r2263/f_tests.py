#!/usr/bin/env python
# -*- coding: utf-8 -*-

# system modules
import sys
import unittest

# custom modules
import f_core as fc
import output_tracker as ot

class RestTestResult(unittest.TestResult):
	def __init__(self):
		unittest.TestResult.__init__(self)
		self.output = ''

	def getDescription(self, test):
		return ''

	def startTest(self, test):
		unittest.TestResult.startTest(self, test)

	def addSuccess(self, test):
		unittest.TestResult.addSuccess(self, test) 
		self.output += ':test-ok:`%s`\n' % test.shortDescription()

	def addFailure(self, test, err):
		unittest.TestResult.addFailure(self, test, err) 
		self.output += ':test-failed:`%s`\n' % test.shortDescription()

	def addError(self, test, err):
		unittest.TestResult.addError(self, test, err)
		self.output += ':test-failed:`%s`\n' % test.shortDescription()

class RestFormatter(unittest.TextTestRunner):
	
	def _makeResult(self):
		return RestTestResult()

	def run(self, suite, doc):
		s = doc.split('\n')[0].strip()
		s += '\n' + '-'*len(s) + '\n'

		result = self._makeResult()
		suite(result)
		s += result.output
		failed, errored = map(len, (result.failures, result.errors))

		s += '\n'
		return (failed+errored, result.testsRun, s)

class TestRanges(unittest.TestCase):
	""" Range selection tests """
	def setUp(self):
		self.output = ot.null_output()

	def test_single(self):
		""" Single number is parsed. """
		self.assertEqual(fc._parse_ids('2', self.output), [2])

	def test_comma(self):
		""" Comma separated numbers are parsed. """
		self.assertEqual(fc._parse_ids('2,3', self.output), [2, 3])

	def test_space(self):
		""" Space separated numbers are parsed. """
		self.assertEqual(fc._parse_ids('2 3', self.output), [2, 3])

	def test_commaspace(self):
		""" Accepts a comma followed by a space as delimiter. """
		self.assertEqual(fc._parse_ids('2, 3', self.output), [2, 3])
		
	def test_commaspacemix(self):
		""" Accepts a mix of commas and spaces as delimiter. """
		self.assertEqual(fc._parse_ids('2,3 4', self.output), [2, 3, 4])
	
	def test_range(self):
		""" Range is parsed. """
		self.assertEqual(fc._parse_ids('2-4', self.output), [2, 3, 4])

	def test_exclusion(self):
		""" Exclusion is parsed. """
		self.assertEqual(fc._parse_ids('2-4,^3', self.output), [2, 4])

	def test_single_exclusion(self):
		""" Single exclusion is valid. """
		self.assertEqual(fc._parse_ids('^2-4', self.output), [])

	def test_precedence(self):
		""" Precedence is observed. """
		self.assertEqual(fc._parse_ids('2-4,^3, 3', self.output), [2, 3, 4])

	def test_sorted(self):
		""" Result is sorted. """
		self.assertEqual(fc._parse_ids('22-24,2-4', self.output), [2, 3, 4, 22, 23, 24])

	def test_unique(self):
		""" Results are unique. """
		self.assertEqual(fc._parse_ids('2-4, 2, 3, 4', self.output), [2, 3, 4])

	def test_python_range(self):
		""" Python ranges are parsed. """
		self.assertEqual(fc._parse_ids('2:4', self.output), [2, 3])

	def test_mixed_range(self):
		""" Mixed ranges are parsed. """
		self.assertEqual(fc._parse_ids('2:4,5-6', self.output), [2, 3, 5, 6])

	def test_range_stride(self):
		""" Python stride syntax is accepted. """
		self.assertEqual(fc._parse_ids('2:5:2', self.output), [2, 4])

	def test_nonnumeric(self):
		""" Raises exception on non-numeric characters for dash syntax. """
		self.assertRaises(Exception, fc._parse_ids, ('2-a', self.output))

	def test_nonnumeric(self):
		""" Raises exception on non-numeric characters for python syntax. """
		self.assertRaises(Exception, fc._parse_ids, ('2:a', self.output))

	def test_nonnumeric(self):
		""" Raises exception on open ranges. """
		self.assertRaises(Exception, fc._parse_ids, ('2-', self.output))

	def test_nonnumeric(self):
		""" Raises exception on open python ranges. """
		self.assertRaises(Exception, fc._parse_ids, ('2::4', self.output))

	def test_unique(self):
		""" Raises exception on invalid ranges. """
		self.assertRaises(Exception, fc._parse_ids, ('2:3', self.output))

if __name__ == '__main__':
	if len(sys.argv) != 2:
		r = RestFormatter()
		modified = True
	else:
		r = unittest.TextTestRunner()
		modified = False

	failed = 0
	total = 0
	output = ''
	for testcase in (TestRanges, ):
		suite = unittest.TestSuite()
		tests = [_ for _ in dir(testcase) if _.startswith('test_')]
		if len(tests) == 0:
			continue
		for test in tests:
			suite.addTest(testcase(test))
		if modified:
			f, t, s = r.run(suite, testcase.__doc__)
			failed += f
			total += t
			output += s
		else:
			r.run(suite)

	if modified:
		print """
Test results
============

Failed tests: %d of %s
	""" % (failed, total)
		print output

		print """
Invocation
----------

Run the test script on command line to get detailed error descriptions. Without the `debug` parameter, you will get reST output.

.. code:: sh

	f_tests.py debug

Documentation
-------------

.. automodule:: f_tests
   :members:
   :private-members:
   :special-members:
   :undoc-members:

	"""