
import datetime
import time
import os

import dateutil.parser as dup

from CCITT_CRC16 import CRCfromString

def parseDTpacket(inval):
    """
    get the datetime from the front of a isoformat packet GRT
    """
    spl = inval.split(' - ')
    if len(spl) > 1:
        return dup.parse(inval.split(' - ')[0])
    else:
        return dup.parse(inval)

def parseL0time(inval):
    """
    take the L0 GRT in the files and make a datetime.time object
    """
    spl = inval.split(':') # 1:42:25:560
    hour = int(spl[0])
    minute = int(spl[1])
    second = int(spl[2])
    microsecond = int(spl[3])*1000
    dt = datetime.time(hour, minute, second, microsecond)
    return dt

def parseL0name(inval):
    """
    take a L0 filename and return a datetime.date object
    """
    date_split = inval.split('-')
    date = datetime.date(int(date_split[0]), int(date_split[1]), int(date_split[2]))
    return date

def parseline(inval, filename=None):
    """
    given a line of the L0 file convert it to a better ISO format that has datetime
    not just the time
    """
    # parse the time
    time_ = inval.split(' - ')
    dt = parseL0time(time_[0])
    # if there is a filename specifed add that date in, otherwise leave it off
    if filename is not None:
        date = parseL0name(filename)
        ans = datetime.datetime.combine(date, dt)
        return ans.isoformat() + ' - ' + time_[1]
    else:
        ans = dt.strftime("%H:%M:%S.%f") + ' - ' + time_[1]
    return ans


class BIRDpacket(object):
    def __init__(self, strin, filename=None):
        """
        given a line in a string input it as a packet

        filename is given to make a datetime of the GRT time
        """
        if 'T' in strin: # you have a full datetime in the file
            self.grt = parseDTpacket(strin)
        elif filename is not None:
            dt = datetime.datetime.combine(parseL0name(filename), datetime.time(0,0,0))
            hour, minute, second, millisecond = strin.split(' - ')[0].split(':')
            self.grt = datetime.datetime(dt.year, dt.month, dt.day, int(hour),
                                   int(minute), int(second), int(millisecond)*100)
        else:
            raise(ValueError("Invalid input, either need an isoformat time or a filename"))
        self.raw = strin.split(' - ')[1]
        splitdat = self.raw.split()
        self.srcid = splitdat[1:3]
        self.destid = splitdat[3:5]
        self.cmd_tlm = splitdat[5]
        self.funid = splitdat[6]
        self.seqnum =  splitdat[7] # number of pages in request
        self.seqidx =  splitdat[8] # counts up to self.seqnum 
        self.pktnum =  splitdat[9] # packet within page, goes up to 0x13 for each page (last could end early)
        self.datalen = splitdat[10] # can be sorted for the last packet in a page
        self.data = splitdat[11:11+int(self.datalen,16)]
        self.crc = splitdat[11+int(self.datalen, 16):11+int(self.datalen, 16)+2]
        self.valid_crc = self._crc_valid()

    def __eq__(self, other):
        attrs = ['data', 'srcid', 'destid']
        for a in attrs:
            if getattr(self, a) != getattr(other, a):
                return False
        return True
        
    def _crc_valid(self):
        """
        if the calcuated CRC matches what is in the packet True, False otherwise
        """
        calc_crc = CRCfromString(' '.join(self.raw.split(' ')[1:-3])).upper()
        if calc_crc[2:4].upper() == self.crc[0].upper() and \
           calc_crc[4:6].upper() == self.crc[1].upper():
            return True
        else:
            return False

    def __str__(self):
        return('BIRDpacket: GRT: {0} Len:{1} Seqidx:{2} Seqnum:{3} Pktnum:{4}'.format(self.grt.isoformat(),
                                                                                      int(self.datalen, 16),
                                                                                      self.seqidx,
                                                                                      self.seqnum,
                                                                                      self.pktnum))

    __repr__ = __str__


class BIRDpackets(list):
    """
    make a list of all the BIRDpacket instances in a file
    """
    def __init__(self, infile):
        """
        given a filename parse into many BIRDpacket instances
        """
        super(BIRDpackets, self).__init__()
        with open(infile, 'r') as fp:
            dat = fp.readlines()
        dat = [v.strip() for v in dat]
        self.filename = infile
        # make this class a list of BIRDpacket objects
        self.extend([BIRDpacket(v, self.filename) for v in dat])
            
    def __str__(self):
        return("{0} packets: {1} bad CRC".format(len(self), int(sum([v.valid_crc for v in self if not v.valid_crc]))))

    __repr__ = __str__
