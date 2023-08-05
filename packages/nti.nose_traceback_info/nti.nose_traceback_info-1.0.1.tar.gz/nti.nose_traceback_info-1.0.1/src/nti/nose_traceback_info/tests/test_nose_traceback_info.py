#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""


$Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904


import sys
from unittest import TestCase, TestSuite

from nti.nose_traceback_info import NoseTracebackInfoPlugin
from nose.plugins import PluginTester
from nose.proxy import ResultProxy

class TestNoseTracebackInfoPlugin(PluginTester,TestCase):

	activate = '--with-traceback-info'
	plugins = [NoseTracebackInfoPlugin()]
	ignoreFiles = True

	def test_format_failure(self):
		formatted = str(self.output)
		__traceback_info__ = formatted

		lines = formatted.split(b'\n' if isinstance(formatted,bytes) else u'\n')

		self.assertEqual( lines[-8].strip(), 'ValueError' )
		self.assertEqual( lines[-9].strip()[0:27], '- __traceback_info__: Child' )

	def makeSuite(self):
		# Only Nose's built-in suites use plugins
		# properly for formatting errors. But those aren't
		# used by the PluginTester and aren't easily used by it.
		# So we write a single-purpose suite. In order to use
		# the right plugins to call, we have to hack into the superclass
		# to get the right config
		caller = sys._getframe(1)
		config = caller.f_locals['conf']
		class TC(TestCase):
			def runTest(self):
				# Include an already-decoded unicode apostrophe
				# to test that decoding works correctly
				__traceback_info__ = 'Child\xe2\x80\x99s'
				raise ValueError
		class Suite(TestSuite):
			def run(self, result, debug=False):
				result = ResultProxy(result, self._tests[0], config)
				return super(Suite,self).run(result,debug=debug)
		return Suite([TC()])

class TestNoseTracebackInfoDirectly(TestCase):

	def _check(self):
		plugin = NoseTracebackInfoPlugin()
		_, tb, _ = plugin.formatFailure( None, sys.exc_info() )
		if isinstance(str(''),bytes): # py2
			assert isinstance(tb,bytes)
		else:
			assert isinstance(tb, str)

	def test_unicode_decoding(self):
		# bytestring
		try:
			# \U0001f4a9 is pile-of-poo
			# '\xff\xfe=\xd8\xa9\xdc' is its utf-16
			# encoding
			__traceback_info__ = b'Childs \xff\xfe=\xd8\xa9\xdc'
			raise ValueError
		except ValueError:
			self._check()

		# Unicode
		try:
			__traceback_info__ = u'Childs \U0001f4a9'
			raise ValueError
		except ValueError:
			self._check()
