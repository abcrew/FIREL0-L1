# -*- coding: utf-8 -*-

"""
Test suite for packet
"""
import datetime
import tempfile
import os
import unittest

import numpy as np

import Request

# class name go in here
__all__ = ['EntryTests', ]

# tests are grouped into classes this way
class EntryTests(unittest.TestCase):
    # magic name run before each test
    def setUp(self):
        super(EntryTests, self).setUp()

    def tearDown(self):
        super(EntryTests, self).tearDown()

    def test_globals(self):
        """Global vars have not changed"""
        typeDict = {'HIRES':{'dataPerBlock':2.94375},
                    'CONTEXT':{'dataPerBlock':1752},
                    'MICRO_BURST':{'dataPerBlock':584},
                    'CONFIG':{'dataPerBlock':54.48},
                    'DATA_TIMES':{'dataPerBlock':2000}} # This was a TBD and 2000 was made up
        secondsPerPage = 0.29
        self.assertEqual(typeDict, Request.typeDict)
        self.assertEqual(secondsPerPage, Request.secondsPerPage)

    def test_timeSplit(self):
        ans = [2013, 1, 23, 12, 34, 0]
        self.assertEqual(ans,
                         Request.Entry._timeSplit(datetime.datetime(2013, 1, 23, 12, 34)))

    def test_toStr(self):
        ans = 'NONE'
        self.assertEqual(ans, Request.Entry._toStr(None))
        ans = '2013, 1, 23, 12, 34, 0'
        self.assertEqual(ans, Request.Entry._toStr(datetime.datetime(2013, 1, 23, 12, 34)))
        ans = '12'
        self.assertEqual(ans, Request.Entry._toStr(12))
        ans = 'bob'
        self.assertEqual(ans, Request.Entry._toStr('bob'))


# this bit o magic runs all the tests in the file
if __name__ == "__main__":
    unittest.main()
#