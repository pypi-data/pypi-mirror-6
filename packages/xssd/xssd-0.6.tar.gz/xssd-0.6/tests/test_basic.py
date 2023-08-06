#!/usr/bin/python

from base_tests import BaseFileTest
from xssd.errors import *
from xssd import Validator

class BasicTest(BaseFileTest):
    """Test checking basic data."""
    definition = {
      'root' : [ { 'name' : 'input', 'type' : 'news' },],
      'complexTypes' : { 'news' : [
        { 'name' : 'title',   'type' : 'string', 'maxLength' : 25 },
        { 'name' : 'content', 'type' : 'string', 'minLength' : 22 },
        { 'name' : 'author',  'type' : 'token',  'maxLength' : 54 },
        { 'name' : 'editor',  'type' : 'token',  'minOccurs' : 0 },
        { 'name' : 'created', 'type' : 'datetime' },
        { 'name' : 'edited',  'type' : 'datetime', 'maxOccurs' : 3 },
      ],},
    }

    def test_instance(self):
        """Validator From File"""
        self.assertEqual(type(self.validator), Validator)

    def test_correct(self):
        """Basic Data Pass"""
        # Odd should pass, Even should fail.
        data = { 'input' : {
          'title'   : 'Correct News',
          'content' : 'This content should always be above 20 charters in length.',
          'author'  : 'mowens',
          'created' : '2007-11-09 20:23:12',
          'edited' : '2007-11-09 20:23:12',
        }}
        errors = { 'input' : NO_ERROR }
        self.positive_test(data, errors)

    def test_negative(self):
        """Basic Data Fail"""
        data = { 'input' : {
          'title'   : 'Bad News which has a title which is way too long for this validation to work.',
          'content' : 'Too Short',
          'editor'  : [ 'token1', 'token2' ],
          'created' : '2008-11-09 20:23:12',
          'edited'  : [ '2007-11-09 20:23:12', '2007-11-09 20:23:12', '2007-11-09 20:23:12', '2007-11-09 20:23:12' ],
        }}
        errors = { 'input' : {
          'created' : NO_ERROR,
          'editor'  : INVALID_MAX_OCCURS,
          'content' : INVALID_MINLENGTH,
          'title'   : INVALID_MAXLENGTH,
          'edited'  : INVALID_MAX_OCCURS,
          'author'  : INVALID_REQUIRED,
        }}
        self.negative_test(data, errors)

