#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""
Test suite for FIRE_L0_L1

"""

import tempfile
import os
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

    def test_determineFileType(self):
        """determineFileType should find files"""
        self.assertEqual('contextfile', FIRE_L0_L1.determineFileType('ContextData.csv'))
        self.assertEqual('configfile', FIRE_L0_L1.determineFileType('Config.csv'))
        self.assertEqual('mbpfile', FIRE_L0_L1.determineFileType('BurstData.csv'))
        self.assertEqual('hiresfile', FIRE_L0_L1.determineFileType('HiResData.csv'))
        self.assertRaises(ValueError, FIRE_L0_L1.determineFileType, 'badin')


class ClassTests(unittest.TestCase):
    # magic name run before each test
    def setUp(self):
        # make a temp file to use
        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        tmpfile.close()
        self.tmpfile = tmpfile.name

    def tearDown(self):
        # and delete the temp file
        os.remove(self.tmpfile)

    def test_ContextFile(self):
        """a context file shold read in and write out"""
        FIRE_L0_L1.ContextFile('test_data/ContextData.csv', self.tmpfile)
        self.assertTrue(os.path.isfile(self.tmpfile))
        with open(self.tmpfile, 'r') as fp:
            dat = fp.readlines()
            self.assertEqual('#{', dat[0][0:2])
            self.assertEqual('2012-12-17T22:18:43.953000 57 109', dat[-1].strip())

    def test_ConfigFile(self):
        """a context file shold read in and write out"""
        FIRE_L0_L1.ConfigFile('test_data/Config.csv', self.tmpfile)
        self.assertTrue(os.path.isfile(self.tmpfile))
        with open(self.tmpfile, 'r') as fp:
            dat = fp.readlines()
            self.assertEqual('#{', dat[0][0:2])
            self.assertEqual('2012-12-17T22:18:48.553000 4 255 165 -999 5 -999 -999 -999 -999 -999 -999 -999 4 165 81', dat[-1].strip())

    def test_MBPFile(self):
        """a mbp file shold read in and write out"""
        FIRE_L0_L1.MBPFile('test_data/BurstData.csv', self.tmpfile)
        self.assertTrue(os.path.isfile(self.tmpfile))
        with open(self.tmpfile, 'r') as fp:
            dat = fp.readlines()
            self.assertEqual('#{', dat[0][0:2])
            self.assertEqual('2012-12-17T22:18:57.053000 2 4 26 130', dat[-1].strip())


# this bit o magic runs all the tests in the file
if __name__ == "__main__":
    unittest.main()
