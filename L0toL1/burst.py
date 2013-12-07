import datetime

import numpy as np
from spacepy import datamodel as dm

import FIREdata
import packet
from page import page




def printBurstPage(inpage):
    """
    print out a Burst page for debugging
    """
    # the first one is 8+8 bytes then 8+8
    dat = inpage.split(' ')
    print ' '.join(dat[0:8+10])
    for ii in range(8+10, len(dat), 12):
        print ' '.join(dat[ii:ii+12])

class burstPage(FIREdata.dataPage):
    """
    a page of burst data
    """
    def __init__(self, inpage):
        self._datalen = 10
        self._majorTimelen = 8
        self._minorTimelen = 2
        dat = inpage.split(' ')
        dat = [int(v, 16) for v in dat]

        self.t0 = FIREdata.dat2time(inpage[0:25])
        # now the data length is 24
        self.major_data(dat[0:self._datalen+ self._majorTimelen])
        start = self._datalen+ self._majorTimelen
        for ii in range(start, len(dat), self._datalen+self._minorTimelen): # the index of the start of each FIRE data
            stop = ii+self._datalen+self._minorTimelen  # 24 bytes of data and 2 for a minor time stamp
            self.minor_data(dat[ii:stop])
        # sort the data
        self = sorted(self, key = lambda x: x[0])

    def minor_data(self, inval):
        """
        read in and add minor data to the class
        """
        if len(inval) < self._datalen+self._minorTimelen+2:
            return
        if (np.asarray(inval) == 0).all(): # is this line fill?
            return
        dt = self[-1][0] # this is the last time
        us = 1000*(inval[0]*2**8 + inval[1])
        if  us < self[-1][0].microsecond:
            dt += datetime.timedelta(seconds=1)
        dt = dt.replace(microsecond=us)
        dt2 = [dt-datetime.timedelta(microseconds=100e3)*i for i in range(9, -1, -1)]
        d1 = np.asarray(inval[self._minorTimelen:]) # 2 bytes of checksum
        d1 = np.asanyarray(['{:02x}'.format(v) for v in d1])
        d2 = [int(v[0], 16) for v in d1]
        d3 = [int(v[1], 16) for v in d1]
        dout = zip(d2, d3)
        for v1, v2 in zip(dt2, dout):
            self.append( (v1, v2) )

    def major_data(self, inval):
        """
        read in and add major data to the class
        """
        if (np.asarray(inval) == 0).all(): # is this line fill?
            return
        dt = FIREdata.dat2time(inval[0:8])
        # there are 10 times 100ms each before this one
        dt2 = [dt-datetime.timedelta(microseconds=100e3)*i for i in range(9, -1, -1)]
        d1 = np.asarray(inval[ self._majorTimelen:])
        d1 = np.asanyarray(['{:02x}'.format(v) for v in d1])
        d2 = [int(v[0], 16) for v in d1]
        d3 = [int(v[1], 16) for v in d1]
        dout = zip(d2, d3)
        for v1, v2 in zip(dt2, dout):
            self.append( (v1, v2) )


class burst(FIREdata.data):
    """
    a datatimes data file
    """
    def __init__(self, inlst):
        dt = zip(*inlst)[0]
        data = np.hstack(zip(*inlst)[1]).reshape((-1, 2))
        dat = dm.SpaceData()

        dat['Burst'] = dm.dmarray(data[:])
        dat['Burst'].attrs['CATDESC'] = 'Burst parameter'
        dat['Burst'].attrs['FIELDNAM'] = 'Burst'
        dat['Burst'].attrs['LABLAXIS'] = 'Burst Parameter'
        dat['Burst'].attrs['SCALETYP'] = 'linear'
        #dat['time'].attrs['UNITS'] = 'none'
        dat['Burst'].attrs['UNITS'] = ''
        dat['Burst'].attrs['VALIDMIN'] = 0
        dat['Burst'].attrs['VALIDMAX'] = 2**4-1
        dat['Burst'].attrs['VAR_TYPE'] = 'data'
        dat['Burst'].attrs['VAR_NOTES'] = 'Burst parameter compressed onboard'
        dat['Burst'].attrs['DEPEND_0'] = 'Epoch'
        dat['Burst'].attrs['FILLVAL'] = 2**8-1

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
        dat['Epoch'].attrs['VAR_NOTES'] = 'Epoch at each configuration point'

        self.data = dat

    @classmethod
    def read(self, filename):
        pages = super(burst, self).read(filename)
        h = []
        for p in pages:
            h.extend(burstPage(p))
        # sort the data
        h = sorted(h, key = lambda x: x[0])
        return burst(h)

