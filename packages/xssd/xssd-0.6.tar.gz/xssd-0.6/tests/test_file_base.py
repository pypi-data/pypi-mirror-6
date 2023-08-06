#!/usr/bin/python

import unittest

from base_tests import BaseFileTest

class PythonSetsTest(BaseFileTest):
    """Test python data files"""
    definition = 'data/definition1.py'
    
    def test_file1(self):
        """Positive Python File"""
        self.positive_test('data/file1.py', None)

    def test_file2(self):
        """Negative Python File"""
        self.negative_test('data/file2.py', None)


class XmlSetsTest(BaseFileTest):
    """Test xml data files"""
    definition = 'data/definition1.xsd';

    def test_file1(self):
        """Positive XML File"""
        self.positive_test('data/file1.xml', None)

    def test_file2(self):
        """Negative XML File"""
        self.negative_test('data/file2.xml', None)

