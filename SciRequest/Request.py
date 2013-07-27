# -*- coding: utf-8 -*-
"""
Class defines the format of the data passed back and forth from FIREBIRD
ops to FIREBIRD science
"""

import datetime

types = ['HIRES', 'CONTEXT', 'MICRO_BURST', 'CONTEXT', 'CONFIG', 'DATA_TIMES']

class Entry(object):
    """
    class to hold a sinlge entry in a Request
    """
    def __init__(self, typ, date, duration, JAS=None):
        if typ.upper() not in types:
            raise(ValueError('Type: {0} not recognized, must be one of {1}'.format(typ.upper(), types)))
        self.typ = typ.upper()
        self.date = date
        self.duration = int(duration)
        self.JAS = JAS
        self.downlinktime = 0.0 # to be filled with best guesses

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




