#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""
Test suite for packet
"""
import datetime
import tempfile
import os
import unittest

import numpy as np

import FIREdata

# class name go in here
__all__ = ['ClassTests', 'FunctionTests']

# tests are grouped into classes this way
class ClassTests(unittest.TestCase):
    # magic name run before each test
    def setUp(self):
        super(ClassTests, self).setUp()

    def tearDown(self):
        super(ClassTests, self).tearDown()



class FunctionTests(unittest.TestCase):
    # magic name run before each test
    def setUp(self):
        super(FunctionTests, self).setUp()

    def tearDown(self):
        super(FunctionTests, self).tearDown()

    # a test is a method that starts with the letters 'test'
    def test_dat2time(self):
        """dat2time has known behaviour"""
        self.assertEqual(FIREdata.dat2time('0D 04 12 12 28 38 00 55'),
                         datetime.datetime(2013, 4, 18, 18, 40, 56, 85000))
        self.assertEqual(FIREdata.dat2time('0D 04 12 12 28 38 00 55'.split(' ')),
                         datetime.datetime(2013, 4, 18, 18, 40, 56, 85000))
        self.assertEqual(FIREdata.dat2time([int(v, 16) for v in '0D 04 12 12 28 38 00 55'.split(' ')]),
                         datetime.datetime(2013, 4, 18, 18, 40, 56, 85000))
        self.assertTrue(FIREdata.dat2time([int(v, 16) for v in '0D 15 12 12 28 38 00 55'.split(' ')]) is None)




# this bit o magic runs all the tests in the file
if __name__ == "__main__":
    unittest.main()
