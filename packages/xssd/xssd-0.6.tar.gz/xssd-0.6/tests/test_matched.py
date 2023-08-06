#!/usr/bin/python

from base_tests import BaseFileTest
from xssd.errors import *

class MatchTest(BaseFileTest):
    """Test for checking the simple match."""
    definition = {
      'root' : [
        { 'name' : 'password', 'type' : 'string' },
        { 'name' : 'confirm',  'type' : 'string', 'match'    : 'password' },
        { 'name' : 'notsame',  'type' : 'string', 'notMatch' : 'confirm' },
      ],
    }

    def test_01_correct(self):
        """Items Match Correctly"""
        # Odd should pass, Even should fail.
        data = {
          'password' : 'foo',
          'confirm'  : 'foo',
          'notsame'  : 'bar',
        }
        errors = { 'password' : NO_ERROR, 'confirm' : NO_ERROR, 'notsame' : NO_ERROR }
        self.positive_test(data, errors)

    def test_02_negative(self):
        """Items Match Incorrectly"""
        data = {
          'password' : 'foo',
          'confirm'  : 'bar',
          'notsame'  : 'bar',
        }
        errors = {
          'password' : NO_ERROR,
          'confirm' : INVALID_MATCH,
          'notsame' : INVALID_MATCH,
        }
        self.negative_test(data, errors)

    def test_03_root_match(self):
        """Match from the Root"""
        self.definition['root'][1]['match'] = '/password'
        self.test_01_correct()

