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



# this bit o magic runs all the tests in the file
if __name__ == "__main__":
    unittest.main()
