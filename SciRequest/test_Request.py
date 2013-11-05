# -*- coding: utf-8 -*-

"""
Test suite for packet
"""
import datetime
import tempfile
import os
import shutil
import unittest
import warnings

import Request

# class name go in here
__all__ = ['EntryTests', 'RequestTests']

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
        secondsPerPage = 2.3893333333333335
        self.assertEqual(typeDict, Request.typeDict)
        self.assertAlmostEqual(secondsPerPage, Request.secondsPerPage)

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

    def test_init_exceptions(self):
        """Entry.__init__ checks input"""
        self.assertRaises(ValueError, Request.Entry, 'bad', 'bad', 'bad', 'bad', 'bad')
        self.assertRaises(ValueError, Request.Entry, 1, 'bad', 'bad', 'bad', 'bad')
        self.assertRaises(ValueError, Request.Entry, 1, 'CONTEXT', 'bad', 'bad', 'bad')
        self.assertRaises(ValueError, Request.Entry, 1, 'CONTEXT', datetime.datetime(2013, 12, 2, 1), 'bad', 'bad')
        self.assertRaises(ValueError, Request.Entry, 1, 'CONTEXT', datetime.datetime(2013, 12, 2, 1), 12, 'bad')
#        self.assertRaises(ValueError, Request.Entry, 1, 'CONTEXT', datetime.datetime(2013, 12, 2, 1), 12, 10)

    def test_calcDownlink(self):
        entry = Request.Entry(1, 'CONTEXT', datetime.datetime(2013, 12, 2, 1), 2300, 10)
        self.assertAlmostEqual(entry.downlinktime, 3.1366818873668194, 4)

    def test_longdownlink(self):
        warnings.simplefilter('error')
        self.assertRaises(UserWarning, Request.Entry, 1, 'HIRES', datetime.datetime(2013, 12, 2, 1), 1210, 10)
        warnings.simplefilter('ignore')
        entry = Request.Entry(1, 'HIRES', datetime.datetime(2013, 12, 2, 1), 2300, 10)
        self.assertAlmostEqual(entry.downlinktime, 59.251408351026186, 4)
        self.assertAlmostEqual(entry.duration, 73, 4)

        entry = Request.Entry(1, 'CONTEXT', datetime.datetime(2013, 12, 2, 1), 1752*75, 10)
        self.assertAlmostEqual(entry.downlinktime, 59.9992694063927, 4)
        self.assertAlmostEqual(entry.duration, 43995, 4)

        entry = Request.Entry(1, 'MICRO_BURST', datetime.datetime(2013, 12, 2, 1), 584*73, 10)
        self.assertAlmostEqual(entry.downlinktime, 59.9992694063927, 4)
        self.assertAlmostEqual(entry.duration, 14665, 4)

        entry = Request.Entry(1, 'CONFIG', datetime.datetime(2013, 12, 2, 1), 54.48*75, 10)
        self.assertAlmostEqual(entry.downlinktime, 59.99647577092512, 4)
        self.assertAlmostEqual(entry.duration, 1368, 4)

        entry = Request.Entry(1, 'DATA_TIMES', datetime.datetime(2013, 12, 2, 1), 2000*75, 10)
        self.assertAlmostEqual(entry.downlinktime, 59.99974400000001, 4)
        self.assertAlmostEqual(entry.duration, 50223, 4)

    def test_str(self):
        entry = Request.Entry(1, 'MICRO_BURST', datetime.datetime(2013, 12, 2, 1), 345, 10)
        self.assertEqual(entry.__str__(), 'MICRO_BURST, 2013, 12, 2, 1, 0, 0, 345, NONE')


# tests are grouped into classes this way
class RequestTests(unittest.TestCase):
    # magic name run before each test
    def setUp(self):
        super(RequestTests, self).setUp()
        tmpdir =  tempfile.mkdtemp(suffix='_FIRE_Request', prefix='tmp')
        self.tmpdir = tmpdir

    def tearDown(self):
        super(RequestTests, self).tearDown()
        try:
            shutil.rmtree(self.tmpdir)
        except:
            pass

    def test_init(self):
        # defaults
        a = Request.Request()
        self.assertEqual(datetime.datetime.utcnow().date(), a.date)
        self.assertEqual('.', a.directory)
        a = Request.Request(date=datetime.datetime.utcnow())
        self.assertEqual(datetime.datetime.utcnow().date(), a.date)
        self.assertAlmostEqual(0.0, a.downlinkTime)

    def test_addEntry(self):
        a = Request.Request(date=datetime.date(1977, 3, 7))
        entry = Request.Entry(1, 'MICRO_BURST', datetime.datetime(2013, 12, 2, 1), 345, 10)
        a.addEntry(entry)
        self.assertAlmostEqual(1.4115068493150686, a.downlinkTime, 4)
        self.assertRaises(ValueError, a.addEntry, 'badval')
        self.assertEqual(len(a), 1)
        self.assertAlmostEqual(1.4115068493150686, a.downlinkTime, 4)
        warnings.simplefilter('error')
        self.assertRaises(UserWarning, a.addEntry, entry)
        warnings.simplefilter('ignore')

    def test_sortEntry(self):
        a = Request.Request(date=datetime.date(1977, 3, 7))
        entry1 = Request.Entry(1, 'MICRO_BURST', datetime.datetime(2013, 12, 2, 1), 345, 10)
        a.addEntry(entry1)
        entry2 = Request.Entry(1, 'MICRO_BURST', datetime.datetime(2013, 12, 3, 1), 345, 20)
        a.addEntry(entry2)
        a.sortEntries()
        self.assertEqual(len(a), 2)
        self.assertEqual(a[0], entry2)
        self.assertEqual(a[1], entry1)
        self.assertAlmostEqual(2.8230136986301373, a.downlinkTime, 4)

    def test_makeFilename(self):
        a = Request.Request(date=datetime.date(1977, 3, 7))
        self.assertEqual('FU_1_REQ_19770307_v00.csv', a._makeFilename(1))
        self.assertEqual('FU_2_REQ_19770307_v00.csv', a._makeFilename(2))
        self.assertEqual('FU_2_REQ_19770307_v02.csv', a._makeFilename(2, 2))
        self.assertRaises(ValueError, a._makeFilename, 'bad')

    def test_makeHeader(self):
        a = Request.Request(date=datetime.date(1977, 3, 7))
        self.assertEqual('# FIRE Science Priority Queue request file\n# FIREBIRD UNIT 1\n# Type, year, month, day, hour, minute, second, duration, JAS file name\n', a._makeHeader(1))
        self.assertRaises(ValueError, a._makeHeader, 'bad')
        self.assertEqual('# FIRE Science Priority Queue request file\n# FIREBIRD UNIT 2\n# Type, year, month, day, hour, minute, second, duration, JAS file name\n', a._makeHeader(2))

    def test_extractVersion(self):
        self.assertEqual(0, Request.Request._extractVersion('FU_1_REQ_19770307_v00.csv'))
        self.assertEqual(3, Request.Request._extractVersion('FU_1_REQ_19770307_v03.csv'))

    def test_toFile(self):
        a = Request.Request(date=datetime.date(1977, 3, 7), directory=self.tmpdir)
        a.toFile()
        self.assertFalse(os.path.isfile(os.path.join(self.tmpdir, 'FU_1_REQ_19770307_v00.csv')))
        entry1 = Request.Entry(1, 'MICRO_BURST', datetime.datetime(2013, 12, 2, 1), 345, 10)
        a.addEntry(entry1)
        entry2 = Request.Entry(1, 'MICRO_BURST', datetime.datetime(2013, 12, 3, 1), 345, 20)
        a.addEntry(entry2)
        a.toFile()
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, 'FU_1_REQ_19770307_v00.csv')))
        self.assertFalse(os.path.isfile(os.path.join(self.tmpdir, 'FU_2_REQ_19770307_v00.csv')))
        a.toFile()
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, 'FU_1_REQ_19770307_v01.csv')))
        entry3 = Request.Entry(2, 'MICRO_BURST', datetime.datetime(2013, 12, 3, 1), 345, 20)
        a.addEntry(entry3)
        a.toFile()
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, 'FU_2_REQ_19770307_v00.csv')))


# this bit o magic runs all the tests in the file
if __name__ == "__main__":
    unittest.main()
#
