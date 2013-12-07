import datetime

import numpy as np
from spacepy import datamodel as dm

import FIREdata
import packet
from page import page

class hires(FIREdata.data):
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
        dat['Epoch'].attrs['VALIDMIN'] = datetime.datetime(1990,1,1)
        dat['Epoch'].attrs['VALIDMAX'] = datetime.datetime(2029,12,31,23,59,59,999000)
        dat['Epoch'].attrs['VAR_TYPE'] = 'support_data'
        dat['Epoch'].attrs['TIME_BASE'] = '0 AD'
        dat['Epoch'].attrs['MONOTON'] = 'INCREASE'
        dat['Epoch'].attrs['VAR_NOTES'] = 'Epoch at each hi-res measurement'
        dat['hr0'] = dm.dmarray(counts[:,0:6])
        dat['hr0'].attrs['CATDESC'] = 'Detector 0 hi-res'
        dat['hr0'].attrs['ELEMENT_LABELS'] = "hr0-0", "hr0-1", "hr0-2", "hr0-3", "hr0-4", "hr0-5",  
        dat['hr0'].attrs['ELEMENT_NAMES'] =  "hr0-0", "hr0-1", "hr0-2", "hr0-3", "hr0-4", "hr0-5",  
        dat['hr0'].attrs['FILLVAL'] = -1e-31
        dat['hr0'].attrs['LABLAXIS'] = 'Detector 0 hi-res'
        dat['hr0'].attrs['SCALETYP'] = 'log'
        dat['hr0'].attrs['UNITS'] = 'counts'
        dat['hr0'].attrs['VALIDMIN'] = 0
        dat['hr0'].attrs['VALIDMAX'] = 2**16-1
        dat['hr0'].attrs['VAR_TYPE'] = 'data'
        dat['hr0'].attrs['VAR_NOTES'] = 'hr0 for each channel'
        dat['hr0'].attrs['DEPENDNAME_0'] = 'Epoch'
        dat['hr1'] = dm.dmarray(counts[:,6:])
        dat['hr1'].attrs['CATDESC'] = 'Detector 1 hi-res'
        dat['hr1'].attrs['ELEMENT_LABELS'] = "hr1-0", "hr1-1", "hr1-2", "hr1-3", "hr1-4", "hr1-5",  
        dat['hr1'].attrs['ELEMENT_NAMES'] =  "hr1-0", "hr1-1", "hr1-2", "hr1-3", "hr1-4", "hr1-5",  
        dat['hr1'].attrs['FILLVAL'] = -1e-31
        dat['hr1'].attrs['LABLAXIS'] = 'Detector 1 hi-res'
        dat['hr1'].attrs['SCALETYP'] = 'log'
        dat['hr1'].attrs['UNITS'] = 'counts'
        dat['hr1'].attrs['VALIDMIN'] = 0
        dat['hr1'].attrs['VALIDMAX'] = 2**16-1
        dat['hr1'].attrs['VAR_TYPE'] = 'data'
        dat['hr1'].attrs['VAR_NOTES'] = 'hr1 for each channel'
        dat['hr1'].attrs['DEPENDNAME_0'] = 'Epoch'
        self.data = dat

    @classmethod
    def read(self, filename):
        b = packet.BIRDpackets(filename)
        print('    Read {0} packets'.format(len(b)))
        pages = page.fromPackets(b)
        print('    Read {0} pages'.format(len(pages)))
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
    print ' '.join(dat[0:24+8])
    for ii in range(24+8, len(dat), 24+2):
        print ' '.join(dat[ii:ii+24+2])

class hiresPage(FIREdata.dataPage):
    """
    a page of hires data
    """
    def __init__(self, inpage):
        self._datalen = 24
        self._majorTimelen = 8
        self._minorTimelen = 2

        dat = inpage.split(' ')
        dat = [int(v, 16) for v in dat]

        self.t0 = FIREdata.dat2time(inpage[0:25])
        # now the data length is 24
        self.major_data(dat[0:self._datalen+self._majorTimelen])
        start = self._datalen+self._majorTimelen
        for ii in range(start, len(dat), self._datalen+self._minorTimelen): # the index of the start of each FIRE data
            stop = ii+self._datalen+self._minorTimelen  # 24 bytes of data and 2 for a minor time stamp
            self.minor_data(dat[ii:stop])
        # sort the data
        self = sorted(self, key = lambda x: x[0])

    def minor_data(self, inval):
        """
        read in and add minor data to the class
        """
        if len(inval) < self._datalen+self._minorTimelen:
            return
        if (np.asarray(inval) == 0).all(): # is this line fill?
            return
        dt = self[-1][0]
        us = 1000*(inval[0]*2**8 + inval[1])
        if  us < self[-1][0].microsecond:
            dt += datetime.timedelta(seconds=1)
        if us == 1000000:
            dt += datetime.timedelta(seconds=1)
        elif us > 1000000:
            return
        else:
            dt = dt.replace(microsecond=us)
        d1 = np.asarray(inval[self._minorTimelen::2])
        d2 = np.asarray(inval[self._minorTimelen+1::2])
        self.append([dt, d2*2**8+d1])

    def major_data(self, inval):
        """
        read in and add major data to the class
        """
        if (np.asarray(inval) == 0).all(): # is this line fill?
            return
        dt = FIREdata.dat2time(inval[0:8])
        d1 = np.asarray(inval[self._majorTimelen::2])
        d2 = np.asarray(inval[self._majorTimelen+1::2])
        self.append([dt, d2*2**8+d1])

