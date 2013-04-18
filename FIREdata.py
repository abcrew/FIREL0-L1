
import datetime
import itertools
import time

import numpy as np

class hires(object):
    """
    a single hi res entry
    """
    def __init__(self):
        self.dt = None
        self.counts = np.zeros(12, dtype=uint16)

    @classmethod
    def makeHighRes(self, instr, t0, milli):
        h = hires()

def printHiresPage(inpage):
    """
    print out a hires page for debugging
    """
    # the first one is 8 bytes then 24
    dat = inpage.split(' ')
    print ' '.join(dat[0:24+8+2])
    for ii in range(24+8+2, len(dat), 24+2+2):
        print ' '.join(dat[ii:ii+24+2+2])

class hiresPage(object):
    """
    a page of hires data
    """
    def __init__(self, inpage):
        dat = inpage.split(' ')
        dat = [int(v, 16) for v in dat]

        t0tmp = inpage[0:23].split(' ')
        t1tmp = [int(v, 16) for v in t0tmp[:-2]]
        t1tmp.append(int(t0tmp[-2]+t0tmp[-1], 16))
        t0 = datetime.datetime(2000 + t1tmp[0], t1tmp[1], t1tmp[2],
                               t1tmp[3], t1tmp[4], t1tmp[5], 1000*t1tmp[6])
        self.t0 = t0
        # now the data length is 24
        self.data = []
        self.major_data(dat[0:24+8])
        start = 24+8+2
        for ii in range(start, len(dat), 24+2+2): # the index of the start of each FIRE data
            stop = ii+24+2+2  # 24 bytes of data and 2 for a minor time stamp
            self.minor_data(dat[ii:stop])

    def minor_data(self, inval):
        print inval
        if len(inval) < 24+2+2:
            return
        dt = self.data[-1][0]
        us = 1000*(inval[0]*256 + inval[1])
        if  us < self.data[-1][0].microsecond:
            dt += datetime.timedelta(seconds=1)
        dt = dt.replace(microsecond=us)
        d1 = np.asarray(inval[2::2])
        d2 = np.asarray(inval[3::2])
        self.data.append([dt, d1*265+d2])
            
            
    def major_data(self, inval):
        dt = datetime.datetime(2000 + inval[0], inval[1], inval[2],
                               inval[3], inval[4], inval[5], 1000*(inval[6]*256 + inval[7]))
        d1 = np.asarray(inval[8::2])
        d2 = np.asarray(inval[9::2])
        self.data.append([dt, d1*265+d2])

                               
    

class page(str):
    """
    class to represent a page of data for any of the types
    """
    @classmethod
    def fromPackets(self, packets):
        """
        given a BIRDpackets class create a list of pages
        """
        _seqnum = [p.seqnum for p in packets]
        _seqidx = [p.seqidx for p in packets]
        _pktnum = [p.pktnum for p in packets]
        # how many pages are in the file?
        # count through the seqidx and see if it repeats
        npages = 0
        tmp = 0
        pages = []
        pg = ''
        for ii, (si, sn, pn) in enumerate(itertools.izip( _seqnum, _seqidx, _pktnum)):
            if pn == '01' and pg: # start of a new page
                pages.append(pg)
                pg = ''
            elif pn == '01':
                pg = ''
            if pg:
                pg += ' '
            pg += ' '.join(packets[ii].data)
        pages.append(pg)
        return [page(p) for p in pages]

