#!/usr/bin/python

import unittest
import sys
sys.path.insert(1, '../lib')

from xssd.errors import *

class TestErrorObject(unittest.TestCase):
    """Test the error objects created."""
    def test_no_error(self):
        """No Errors is a Sucess"""
        self.assert_(not NO_ERROR)

    def test_error(self):
        """Errors Fail"""
        self.assert_(INVALID_TYPE)

    def test_error_name(self):
        """Error Names"""
        self.assertEqual(str(INVALID_TYPE), "Invalid Node Type")

    def test_error_id(self):
        """Error Enumeration"""
        self.assertEqual(int(INVALID_TYPE), 0x01)

    def test_error_compare(self):
        """Error Compare Against own Type"""
        self.assertEqual(INVALID_TYPE, INVALID_TYPE)

    def test_error_id_compare(self):
        """Error Compare Against ID"""
        self.assertEqual(INVALID_TYPE, 0x01)

    def test_error_not_compare(self):
        """Error Doesn't Compare"""
        self.assertNotEqual(INVALID_TYPE, INVALID_MAXLENGTH)

    def test_id_not_compare(self):
        """Error Doesn't Compare Against ID"""
        self.assertNotEqual(INVALID_TYPE, 0x05)


class TestErrorsReports(unittest.TestCase):
    """Test the reporting of structural errors"""
    def setUp(self):
        self._a = ElementErrors(mode=MODE_AND)
        self._b = ElementErrors(mode=MODE_OR)

    def test_none_reported(self):
        """None Reported"""
        self.assertFalse(self._a)
        self.assertFalse(self._b)

    def test_noerrors_reported(self):
        """No Errors Reported"""
        self._a['one'] = NO_ERROR
        self._b['one'] = NO_ERROR
        self.assertFalse(self._a)
        self.assertFalse(self._b)
        self._a['two'] = NO_ERROR
        self._b['two'] = NO_ERROR
        self.assertFalse(self._a)
        self.assertFalse(self._b)

    def test_and_errors(self):
        """When Any Fail"""
        self._a['one'] = INVALID_TYPE
        self.assertTrue(self._a)
        self._a['two'] = NO_ERROR
        self.assertTrue(self._a)

    def test_remove_and_error(self):
        """When AND error removed"""
        self._a['one'] = INVALID_TYPE
        self._a['one'] = NO_ERROR
        self.assertFalse(self._a)

    def test_or_errors(self):
        """When All Fail"""
        self._b['one'] = INVALID_TYPE
        self.assertTrue(self._b)
        self._b['two'] = NO_ERROR
        self.assertFalse(self._b)
        self._b['one'] = NO_ERROR
        self.assertFalse(self._b)

    def test_remove_or_error(self):
        """When OR error removed"""
        self._b['one'] = INVALID_TYPE
        self._b['two'] = NO_ERROR
        self.assertFalse(self._b)
        self._b.pop('two')
        self.assertTrue(self._b)

    def test_error_comparison(self):
        """Test Errors Against"""
        self._a['one']   = INVALID_TYPE
        self._a['two']   = INVALID_MINLENGTH
        self._a['three'] = INVALID_MAXLENGTH
        self.assertEqual(self._a, {
            'one': INVALID_TYPE, 'two': INVALID_MINLENGTH, 'three': 0x04,
        })
        self.assertNotEqual(self._a, {
            'one': NO_ERROR, 'two': INVALID_MINLENGTH, 'three': INVALID_MAXLENGTH,
        })

    def test_sub_tests(self):
        """Report can contain reports"""
        self._a['one'] = self._b
        self.assertTrue(isinstance(self._a['one'], ElementErrors))

    def test_sub_false(self):
        """False SubReport is nonError"""
        self._a['one'] = NO_ERROR
        self._a['two'] = self._b
        self._b['one'] = NO_ERROR
        self.assertFalse(self._a)
        self.assertFalse(self._b)

    def test_sub_true(self):
        """True SubReport is Error"""
        self._b['one'] = INVALID_TYPE
        self._a['one'] = NO_ERROR
        self._a['two'] = self._b
        self.assertTrue(self._a)
        self.assertTrue(self._b)

    def test_sub_logic(self):
        """True SupReport no effect"""
        self._a['one'] = INVALID_TYPE
        self._a['two'] = self._b
        self.assertTrue(self._a)
        self.assertFalse(self._b)

