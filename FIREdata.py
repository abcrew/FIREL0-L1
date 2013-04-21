
import datetime
import itertools
import time

import numpy as np
from spacepy import datamodel as dm

import packet

class hires(object):
    """
    a hi-res data file
    """
    def __init__(self, inlst):
        dt = zip(*inlst)[0]
        counts = np.hstack(zip(*inlst)[1]).reshape((-1, 12))
        dat = dm.SpaceData()
        dat['Epoch'] = dm.dmarray(dt)
        dat['Epoch'].attrs['CATDESC'] = 'Default Time'
        dat['Epoch'].attrs['FIELDNAM'] = 'Epoch'
        #dat['Epoch'].attrs['FILLVAL'] = datetime.datetime(2100,12,31,23,59,59,999000)
        dat['Epoch'].attrs['LABLAXIS'] = 'Epoch'
        dat['Epoch'].attrs['SCALETYP'] = 'linear'
        dat['Epoch'].attrs['UNITS'] = 'ms'
        dat['Epoch'].attrs['VALIDMIN'] = datetime.datetime(1990,1,1)
        dat['Epoch'].attrs['VALIDMAX'] = datetime.datetime(2029,12,31,23,59,59,999000)
        dat['Epoch'].attrs['VAR_TYPE'] = 'support_data'
        dat['Epoch'].attrs['TIME_BASE'] = '0 AD'
        dat['Epoch'].attrs['MONOTON'] = 'INCREASE'
        dat['Epoch'].attrs['VAR_NOTES'] = 'Epoch at each hi-res measurement'
        dat['hr0'] = dm.dmarray(counts[:,0:6])
        dat['hr0'].attrs['CATDESC'] = 'Detector 0 hi-res'
        dat['hr0'].attrs['FIELDNAM'] = 'hr0'
        dat['hr0'].attrs['FILLVAL'] = -1e-31
        dat['hr0'].attrs['LABLAXIS'] = 'Detector 0 hi-res'
        dat['hr0'].attrs['SCALETYP'] = 'log'
        dat['hr0'].attrs['UNITS'] = 'counts'
        dat['hr0'].attrs['VALIDMIN'] = 0
        dat['hr0'].attrs['VALIDMAX'] = 2**16-1
        dat['hr0'].attrs['VAR_TYPE'] = 'data'
        dat['hr0'].attrs['VAR_NOTES'] = 'hr0 for each channel'
        dat['hr0'].attrs['DEPEND_0'] = 'Epoch'
        dat['hr1'] = dm.dmarray(counts[:,0:6])
        dat['hr1'].attrs['CATDESC'] = 'Detector 1 hi-res'
        dat['hr1'].attrs['FIELDNAM'] = 'hr1'
        dat['hr1'].attrs['FILLVAL'] = -1e-31
        dat['hr1'].attrs['LABLAXIS'] = 'Detector 1 hi-res'
        dat['hr1'].attrs['SCALETYP'] = 'log'
        dat['hr1'].attrs['UNITS'] = 'counts'
        dat['hr1'].attrs['VALIDMIN'] = 0
        dat['hr1'].attrs['VALIDMAX'] = 2**16-1
        dat['hr1'].attrs['VAR_TYPE'] = 'data'
        dat['hr1'].attrs['VAR_NOTES'] = 'hr1 for each channel'
        dat['hr1'].attrs['DEPEND_0'] = 'Epoch'
        self.data = dat

    def writeHiRes(self, filename):
        dm.toJSONheadedASCII(filename, self.data)

    @classmethod
    def readHighRes(self, filename):
        b = packet.BIRDpackets(filename)
        pages = page.fromPackets(b)
        h = []
        for p in pages:
            h.extend(hiresPage(p))
        # sort the data
        h = sorted(h, key = lambda x: x[0])        
        return hires(h)
    

def printHiresPage(inpage):
    """
    print out a hires page for debugging
    """
    # the first one is 8 bytes then 24
    dat = inpage.split(' ')
    print ' '.join(dat[0:24+8+2])
    for ii in range(24+8+2, len(dat), 24+2+2):
        print ' '.join(dat[ii:ii+24+2+2])

class hiresPage(list):
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
        self.major_data(dat[0:24+8])
        start = 24+8+2
        for ii in range(start, len(dat), 24+2+2): # the index of the start of each FIRE data
            stop = ii+24+2+2  # 24 bytes of data and 2 for a minor time stamp
            self.minor_data(dat[ii:stop])
        # sort the data
        self = sorted(self, key = lambda x: x[0])

    def minor_data(self, inval):
        """
        read in and add minor data to the class
        """
        if len(inval) < 24+2+2:
            return
        dt = self[-1][0]
        us = 1000*(inval[0]*256 + inval[1])
        if  us < self[-1][0].microsecond:
            dt += datetime.timedelta(seconds=1)
        dt = dt.replace(microsecond=us)
        d1 = np.asarray(inval[2:-2:2])
        d2 = np.asarray(inval[3:-2:2])
        self.append([dt, d1*265+d2])
            
    def major_data(self, inval):
        """
        read in and add major data to the class
        """
        dt = datetime.datetime(2000 + inval[0], inval[1], inval[2],
                               inval[3], inval[4], inval[5], 1000*(inval[6]*256 + inval[7]))
        d1 = np.asarray(inval[8::2])
        d2 = np.asarray(inval[9::2])
        self.append([dt, d1*265+d2])

    

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

