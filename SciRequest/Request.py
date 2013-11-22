# -*- coding: utf-8 -*-
"""
Class defines the format of the data passed back and forth from FIREBIRD
ops to FIREBIRD science
"""
from __future__ import division

import datetime
import textwrap
import os
import warnings

warnings.simplefilter('always')

# this is type, then seconds of data per block
typeDict = {'HIRES':{'dataPerBlock':2.94},
            'CONTEXT':{'dataPerBlock':1752},
            'MICRO_BURST':{'dataPerBlock':584},
            'CONFIG':{'dataPerBlock':54.5},
            'DATA_TIMES':{'dataPerBlock':2000}} # This was a TBD and 2000 was made up
secondsPerPage = 4096*8/19200.*1.4
# the 1.4 is a lump factor to take in overhead
# 4096 is a 4k page
# 8 to bits to bytes
# 19200 is the baud rate

class Entry(object):
    """
    class to hold a single entry in a Request
    """
    def __init__(self, sc, typ, date, duration, priority, JAS=None, datatimes=None):
        if sc not in [1,2,3,4] and sc not in ['1', '2', '3', '4']:
            raise(ValueError('Spacecraft, "{0}", not understood, must be 1 or 2'.format(sc)))
        self.sc = sc
        if typ.upper() not in typeDict:
            raise(ValueError('Type, "{0}", not recognized, must be one of {1}'.format(typ.upper(), typeDict.keys())))
        self.typ = typ.upper()
        if not isinstance(date, datetime.datetime):
            raise(TypeError('Invalid datetime.datetime object for date'))
        self.date = date
        self.duration = int(duration)
        self.priority = int(priority)
        self.JAS = JAS
        self.downlinktime = None # to be filled by a calculation
        self.datatimes = datatimes
        if self.datatimes is not None:
            self._checkDataTimes()
        self._calcDownlink()
        if self.downlinktime > 60.0: # if too long
            while self.downlinktime > 60.0: # just keep reducing it until it is ok
                self.duration -= 1
                self._calcDownlink()
            warnings.warn("Downlink time was longer than allowed, duration shortened to {0}".format(self.duration))

    def _checkDataTimes(self):
        """
        given the request we are creating make sure it is inside datatimes, clip if not
        """
        pass
                
        
            
    @property
    def endDate(self):
        """
        return the end time of the request
        this is self.date+duration
        """
        return self.date + datetime.timedelta(seconds=self.duration)
            
#    def __eq__(self, other):
#        """
#        if the pieces match they are equal
#        """
#        if other.sc != self.sc:
#            return False
#        if other.typ != self.typ:
#            return False
#        if other.date != self.date:
#            return False
#        if other.duration != self.duration:
#            return False
#        if other.priority != self.priority:
#            return False
#        if other.downlinktime != self.downlinktime:
#            return False
#        if other.JAS != self.JAS:
#            return False
#        return True

    def _calcDownlink(self, rate=19200):
        """
        given what we know about the duration of each 4k block calculate how
        long the downlink for the requested data will take
        """
        ticks = self.duration/typeDict[self.typ]['dataPerBlock']
        self.downlinktime = ticks*secondsPerPage

    @staticmethod
    def _timeSplit(dt):
        """
        split a datetime into it pieces for the output
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
        if self.typ == 'DATA_TIMES':
            ans = ', '.join([Entry._toStr(self.typ),
                             '',
                             '',
                             '', 
                             '', 
                             '', 
                             '', 
                             '',                          
                             Entry._toStr(self.JAS) ])
        else:
            ans = ', '.join([Entry._toStr(self.typ),
                             Entry._toStr(self.date),
                             Entry._toStr(self.duration),
                             Entry._toStr(self.JAS) ])
        return ans

    def __repr__(self):
        """
        provide a repr
        """
        return "<{0} {1} {2} {3} {4}>".format(self.typ,
                                              self.date.isoformat(),
                                              self.duration,
                                              self.JAS,
                                              self.priority)


class Request(list):
    """
    class is a collection of Entry objects that go together to make a request
    to the mission ops
    """
    def __init__(self, date=None, directory='.'):
        super(Request, self).__init__()
        if date is None: # assume today
            date = datetime.datetime.utcnow().date()
        elif isinstance(date, datetime.datetime):
            date = date.date()
        self.date = date
        self.directory = directory

    def addEntry(self, entry):
        """
        given an Entry object add it to the Request.  They entries are requested
        in priority order, higher numbers have higher priority
        """
        # make sure it is an entry first
        if not isinstance(entry, Entry):
            raise(ValueError("Bad Entry object given"))
        if entry in self:
            warnings.warn("Entry was already in request, not added again")
        self.append( entry )

    def sortEntries(self):
        """
        sort all the entries into priority order
        """
        self[:] = sorted(self, key=lambda x: x.priority, reverse=True) # big to little
        # self = sorted(self, key=lambda x: x.priority, reverse=False) # little to big

    @property
    def downlinkTime(self):
        """
        compute the total downlink time of the request
        """
        dl = 0.0
        for v in self:
            dl += v.downlinktime
        return dl

    def __repr__(self):
        return "<Request: {0} entries: {1:.1f} downlink seconds>".format(len(self), self.downlinkTime)

    def _makeFilename(self, sc, version=0):
        """
        build a request filename for each filename based on the entries
        """
        if sc not in [1,2,3,4] and sc not in ['1', '2', '3', '4']:
            raise(ValueError('Spacecraft, "{0}", not understood, must be 1 or 2'.format(sc)))
        return "FU_{0}_SPQ_{1:04}{2:02}{3:02}_v{4:02}.csv".format(sc,
                    self.date.year, self.date.month, self.date.day,
                    version)

    def _makeHeader(self, sc):
        """
        build a header for the file
        """
        if sc not in [1,2,3,4] and sc not in ['1', '2', '3', '4']:
            raise(ValueError('Spacecraft, "{0}", not understood, must be 1, 2, 3, or 4'.format(sc)))
        header = """\
        # FIRE Science Priority Queue request file
        # FIREBIRD UNIT {0}
        # Type, year, month, day, hour, minute, second, duration, JAS file name
        """.format(sc)
        header = textwrap.dedent(header)
        return header

    @staticmethod
    def _extractVersion(filename):
        """
        grab out the version from a filename
        """
        version = filename.split('_')[-1].split('.')[0][1:]
        return int(version)

    def toFile(self):
        """
        build the file and output it
        """
        self.sortEntries()
        for sc in [1,2,3,4]:
            filename = os.path.expanduser(os.path.expandvars(os.path.join(self.directory, self._makeFilename(sc))))
            while os.path.isfile(filename):
                filename = self._makeFilename(sc, Request._extractVersion(filename)+1)
            header = self._makeHeader(sc)
            try:
                with open(os.path.expanduser(os.path.expandvars(os.path.join(self.directory, filename))), 'w') as fp:
                    fp.writelines(header)
                    outcntr = []
                    for v in self:
                        if v.sc == sc:
                            if str(v) in outcntr:
                                continue
                            fp.writelines(str(v) + '\n')
                            outcntr.append(str(v))
                    fp.writelines('\n')
                    if not len(outcntr):
                        raise(RuntimeError('No data for sc {0} in Request'.format(sc)))
                print('Wrote: {0}'.format(filename))

            except RuntimeError:
                os.remove(filename)




