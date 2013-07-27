# -*- coding: utf-8 -*-
"""
Class defines the format of the data passed back and forth from FIREBIRD
ops to FIREBIRD science
"""
from __future__ import division

import datetime
import warnings

warnings.simplefilter('always')

typeDict = {'HIRES':{'dataPerBlock':2.94375},
            'CONTEXT':{'dataPerBlock':1752},
            'MICRO_BURST':{'dataPerBlock':584},
            'CONFIG':{'dataPerBlock':54.48},
            'DATA_TIMES':{'dataPerBlock':2000}} # This was a TBD
secondsPerPage = 0.29

class Entry(object):
    """
    class to hold a sinlge entry in a Request
    """
    def __init__(self, typ, date, duration, JAS=None):
        if typ.upper() not in typeDict:
            raise(ValueError('Type: {0} not recognized, must be one of {1}'.format(typ.upper(), typeDict.keys())))
        self.typ = typ.upper()
        self.date = date
        self.duration = int(duration)
        self.JAS = JAS
        self.downlinktime = None # to be filled by a calculation
        self._calcDownlink()
        if self.downlinktime > 60.0: # if too long
            while self.downlinktime > 60.0: # just keep reducing it until it is ok
                self.duration -= 1
                self._calcDownlink()
            warnings.warn("Downlink time was longer than allowed, duration shortened to {0}".format(self.duration))

    def _calcDownlink(self, rate=19200):
        """
        given what we know about the duration of each 4k block calcualte how
        long the downlink for the reqested data will take
        """
        ticks = self.duration/typeDict[self.typ]['dataPerBlock']
        self.downlinktime = ticks*secondsPerPage

    @staticmethod
    def _timeSplit(dt):
        """
        split a datetime into it peices for the output
        """
        return [dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second]

    @staticmethod
    def _toStr(inval):
        """
        change objects to the correct format strings for output
        """
        if isinstance(inval, datetime.datetime):
            return ', '.join(str(v) for v in Entry._timeSplit(inval))
        elif inval is None:
            return 'NONE'
        elif isinstance(inval, (int, long)):
            return str(inval)
        else:
            return inval

    def __str__(self):
        """
        get the string representation of a Entry for file output
        """
        ans = ', '.join([Entry._toStr(self.typ),
                         Entry._toStr(self.date),
                         Entry._toStr(self.duration),
                         Entry._toStr(self.JAS) ])
        return ans

    def __repr__(self):
        """
        provide a repr
        """
        return "<{0} {1} {2} {3}>".format(self.typ, self.date, self.duration, self.JAS)




