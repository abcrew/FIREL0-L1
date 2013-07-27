#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""
Test suite for CCITT_CRC16

"""

import tempfile
import os
import unittest

import numpy as np

import CCITT_CRC16

# class name go in here
__all__ = ['FunctionTests']

# tests are grouped into classes this way
class FunctionTests(unittest.TestCase):
    # magic name run before each test
    def setUp(self):
        super(FunctionTests, self).setUp()
    def tearDown(self):
        super(FunctionTests, self).tearDown()

    def test_CalcCRC(self):
        """CalcCRC should have known output"""
        data = [[123], [1233], [456], [645], [0], [1234], [1, 2, 3]]
        ans = [11788, 15020, 47540, 8413, 57840, 2767, 44461]
        for v1, v2 in zip(data, ans):
            self.assertEqual(CCITT_CRC16.CalcCRC(v1), v2)

    def test_CRCfromString(self):
        """CRCfromString should have known results"""
        data = ['234', '232', 'ff', 'a0']
        ans = ['0x9727', '0xf7e1', '0xff00', '0x541a']
        for v1, v2 in zip(data, ans):
            self.assertEqual(CCITT_CRC16.CRCfromString(v1), v2)
        
        



# this bit o magic runs all the tests in the file
if __name__ == "__main__":
    unittest.main()
