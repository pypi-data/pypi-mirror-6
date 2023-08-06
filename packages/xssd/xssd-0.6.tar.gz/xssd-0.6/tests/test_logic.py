#!/usr/bin/python

from base_tests import BaseFileTest
from xssd.errors import *

class BooleanTest(BaseFileTest):
    """This tests boolean exists logic"""
    definition = {
      'root': [{ 'name': 'data', 'type': 'article', 'maxOccurs': 4 }],

      'complexTypes': { 'article': [ [
        # The double array turns the logic from AND to OR
        { 'name': 'title', 'type': 'string' },
        [ # The third array turns it back to AND
          { 'name': 'name',   'type': 'string' },
          { 'name': 'author', 'type': 'string' },
        ],[
          { 'name': 'name',   'type': 'string' },
          { 'name': 'editor', 'type': 'string' },
          [ # The forth goes back to OR
            { 'name': 'author', 'type': 'string' },
            { 'name': 'title', 'type': 'string' },
          ]
        ] ] ],
      },
    }

    def test_combination(self):
        """Single Item Structure"""
        data = {'data': [ { 'title': 'Correct News' } ] }
        self.positive_test(data, None)

    def test_name_author(self):
        """Double Item Structure"""
        data = {'data': [ { 'name' : 'Correct News', 'author': 'This guy I Know' } ] }
        self.positive_test(data, None)

    def test_name_editor1(self):
        """Third Iterator First"""
        data = {'data': [ { 'name' : 'Correct News', 'editor': 'Blah', 'author': 'This guy I Know' } ] }
        self.positive_test(data, None)

    def test_name_editor2(self):
        """Third Iterator Second"""
        data = {'data': [ { 'name' : 'Correct News', 'editor': 'Blah', 'title': 'Fore Bare' } ] }
        self.positive_test(data, None)

    def test_first_fail(self):
        """Missing Title"""
        data = {'data': [ { 'author': 'This guy' } ] }
        errors = { 'data': [ {
            'title'  : INVALID_REQUIRED,
            'name'   : INVALID_REQUIRED,
            'editor' : INVALID_REQUIRED,
            'author' : NO_ERROR,
        } ] }
        self.negative_test(data, errors)

    def test_second_fail(self):
        """Missing Name"""
        data = {'data': [ { 'name': 'This guy' } ] }
        errors = { 'data': [ {
            'title'  : INVALID_REQUIRED,
            'name'   : NO_ERROR,
            'editor' : INVALID_REQUIRED,
            'author' : INVALID_REQUIRED,
        } ] }
        self.negative_test(data, errors)

    def test_third_fail(self):
        """Missing Editor Choice"""
        data = {'data': [ { 'name': 'This guy', 'editor': 'foo',  } ] }
        errors = { 'data': [ { 
            'title'  : INVALID_REQUIRED,
            'name'   : NO_ERROR,
            'editor' : NO_ERROR,
            'author' : INVALID_REQUIRED,
        } ] }
        self.negative_test(data, errors)

