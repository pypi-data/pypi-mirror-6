#
# Copyright 2010 Martin Owens
#
# This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>
#
"""
Base classes for testing data structures.
"""

import sys
sys.path.insert(1, '../lib')

from xssd import Validator
import unittest

class BaseFileTest(unittest.TestCase):
    """Base test for testing data sets"""
    data       = []   # Data to deal with
    definition = None # Definition
    errors     = []   # Any Erros to test

    def setUp(self):
        self.validator = Validator( self.definition )

    def positive_test(self, data, against=None):
        """Positive test"""
        errors = self._resum(data, against)
        self.assertFalse( errors, 'Expected Pass (%s)' % str(errors) )

    def negative_test(self, data, against=None):
        """Negative test"""
        errors = self._resum(data, against)
        self.assertTrue( errors, 'Expected Errors (%s)' % str(errors) )

    def _resum(self, data, against=None):
        errors = self.validator.validate( data )
        if against:
            try:
                self.assertEqual( errors, against )
            except AssertionError:
                raise
                # This needs some thought to get a real diff
                from datadiff import diff
                raise AssertionError( diff(errors, against) )
        return errors


