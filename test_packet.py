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

import packet

# class name go in here
__all__ = ['ClassTests', ]

# tests are grouped into classes this way
class ClassTests(unittest.TestCase):
    # magic name run before each test
    def setUp(self):
        super(ClassTests, self).setUp()
        self.data = ['12:52:52:727 - C0 00 07 00 02 00 CD 19 01 01 E4 0D 04 12 12 28 38 00 55 D4 00 35 00 11 00 13 00 15 00 AE 00 0C 00 12 00 11 00 17 00 1B 00 B0 00 61 A9 00 87 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 E9 15 00 EB 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 30 4E 01 1D 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 30 4E 01 81 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 9C 0D 01 B3 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 81 75 02 17 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 79 C7 02 49 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 85 9A C0',
'12:52:52:736 - C0 00 07 00 02 00 CD 19 01 02 E4 6D 12 02 AD 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 E9 79 02 DF 00 00 00 00 00 00 00 00 00 00 00 00 06 00 05 00 04 00 32 00 00 00 00 00 44 C3 03 43 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 95 B5 03 75 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 26 19 03 D9 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 49 00 03 00 00 00 0E 5F 00 23 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 F1 C2 00 87 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 29 1F 00 B9 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 18 70 01 1D 07 F3 C0',
'12:52:52:745 - C0 00 07 00 02 00 CD 19 01 03 E3 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 D3 7D 01 4F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 93 C1 01 B3 0A 00 0E 00 08 00 06 00 00 00 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 9C 90 01 E5 00 00 00 00 00 00 04 00 47 00 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 F0 22 02 49 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 45 21 02 7B 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 FB DB 02 DF 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 00 00 00 00 49 00 02 00 00 00 30 4E 03 11 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 00 00 00 00 4B 00 00 00 00 00 40 1C 03 75 00 00 00 D2 85 C0']
        tmp = tempfile.NamedTemporaryFile(delete=False, prefix='2013-04-10-')
        tmp.writelines('\n'.join(self.data))
        tmp.close()
        self.tmp = tmp

    def tearDown(self):
        super(ClassTests, self).tearDown()
        try:
            os.remove(self.tmp.name)
        except:
            pass

    # a test is a method that starts with the letters 'test'
    def test_BIRDpacket(self):
        """Test the string parsing of the data"""
        p = packet.BIRDpacket(self.data[0], '2013-04-11-Filename.txt')
        self.assertEqual(p.cmd_tlm, '00')
        self.assertEqual(p.crc, ['85', '9A'])
        self.assertEqual(p.data, [
 '0D', '04', '12', '12', '28', '38', '00', '55', 'D4', '00', '35', '00', '11', '00', '13', '00', '15', '00', 'AE',
 '00', '0C', '00', '12', '00', '11', '00', '17', '00', '1B', '00', 'B0', '00', '61', 'A9', '00', '87', '00', '00',
 '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00',
 '00', '00', '00', 'E9', '15', '00', 'EB', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00',
 '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '30', '4E', '01', '1D', '00', '00', '00',
 '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00',
 '00', '00', '30', '4E', '01', '81', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00',
 '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '9C', '0D', '01', 'B3', '00', '00', '00', '00',
 '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00',
 '00', '81', '75', '02', '17', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00',
 '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '79', 'C7', '02', '49', '00', '00', '00', '00', '00',
 '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'])
        self.assertEqual(p.datalen, 'E4')
        self.assertEqual(len(p.data), int('E4', 16) )
        self.assertEqual(p.destid, ['00', '02'])
        self.assertEqual(p.funid, 'CD')
        self.assertEqual(p.grt, datetime.datetime(2013, 4, 11, 12, 52, 52, 72700))
        self.assertEqual(p.seqidx, '01')
        self.assertEqual(p.seqnum, '19')
        self.assertEqual(p.srcid, ['00', '07'])
        self.assertEqual(p.valid_crc, True)

    def test_BIRDpackets(self):
        """test BIRDpackets"""
        dat = packet.BIRDpackets(self.tmp.name)
        self.assertEqual(len(dat), 3)
        self.assertTrue(hasattr(dat[0], 'cmd_tlm'))
        self.assertTrue(hasattr(dat[1], 'cmd_tlm'))
        self.assertTrue(hasattr(dat[2], 'cmd_tlm'))
        self.assertTrue(hasattr(dat[0], 'grt'))
        self.assertTrue(hasattr(dat[1], 'grt'))
        self.assertTrue(hasattr(dat[2], 'grt'))





# this bit o magic runs all the tests in the file
if __name__ == "__main__":
    unittest.main()
