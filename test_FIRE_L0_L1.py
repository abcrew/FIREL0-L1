#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""
Test suite for FIRE_L0_L1

"""

import unittest

import numpy as np

import FIRE_L0_L1

# class name go in here
__all__ = ['FunctionTests']

# tests are grouped into classes this way
class FunctionTests(unittest.TestCase):
    # magic name run before each test
    def setUp(self):
        super(FunctionTests, self).setUp()
    def tearDown(self):
        super(FunctionTests, self).tearDown()

    # a test is a method that starts with the letters 'test'
    def test_fillArray(self):
        """fillArray should do as we expect"""
        np.testing.assert_array_equal(np.zeros((10,2)), FIRE_L0_L1.fillArray((10,2), fillval=0))
        val = np.zeros((10,2))
        val[...] = -999
        # regression on default
        np.testing.assert_array_equal(val, FIRE_L0_L1.fillArray((10,2)))

    def test_combineBytes(self):
        """combineBytes should provide known answers"""
        self.assertEqual(0, FIRE_L0_L1.combineBytes(0,0,0,0,0))
        self.assertEqual(256, FIRE_L0_L1.combineBytes(0,1))
        self.assertEqual(65536, FIRE_L0_L1.combineBytes(0,0,1))

    def test_hexArrToInt(self):
        """hexArrToInt should work"""
        ans = np.arange(12)
        tst = np.asarray(['00', '01', '02', '03', '04', '05', '06', '07',
                          '08', '09', '0a', '0b'])
        np.testing.assert_array_equal(ans, FIRE_L0_L1.hexArrToInt(tst))


# this bit o magic runs all the tests in the file
if __name__ == "__main__":
    unittest.main()
