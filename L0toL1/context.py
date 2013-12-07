import datetime

import numpy as np
from spacepy import datamodel as dm

import FIREdata
import packet
from page import page



def printContextPage(inpage):
    """
    print out a Context page for debugging
    """
    # the first one is 8+6 bytes then 8+8
    dat = inpage.split(' ')
    print ' '.join(dat[0:8+6])
    for ii in range(8+6, len(dat), 8+6): # all majors in context
        print ' '.join(dat[ii:ii+8+6])

class contextPage(FIREdata.dataPage):
    """
    a page of context data
    """
    def __init__(self, inpage):
        self._datalen = 6
        self._majorTimelen = 8
        self._minorTimelen = 2
        dat = inpage.split()
        dat = [int(v, 16) for v in dat]

        self.t0 = FIREdata.dat2time(inpage[0:25])
        self.major_data(dat[0:self._datalen+self._majorTimelen])
        start = self._datalen+self._majorTimelen
        for ii in range(start, len(dat), self._datalen+self._majorTimelen): # the index of the start of each FIRE data
            stop = ii+self._datalen+self._majorTimelen
            try:
                self.major_data(dat[ii:stop])
            except IndexError: # malformed data for some reason, skip it
                print("Skipping malformed context: {0}".format(dat[ii:stop]))
                pass
        # drop entries that start with None
        self = [v for v in self if v[0] is not None]
        # sort the data
        self = sorted(self, key = lambda x: x[0])


    def major_data(self, inval):
        """
        read in and add major data to the class
        """
        if (np.asarray(inval) == 0).all(): # is this line fill?
            return
        dt = FIREdata.dat2time(inval[0:8])
        d1 = np.asarray(inval[ self._majorTimelen:])
        d1 = np.asanyarray(['{:02x}'.format(v) for v in d1])
        d2 = int(d1[2] + d1[1] + d1[0], 16)
        d3 = int(d1[5] + d1[4] + d1[3], 16)
        dout = [d2, d3]
#        for v1, v2 in zip(dt, dout):
        self.append( (dt, dout) )


class context(FIREdata.data):
    """
    a context data file
    """
    def __init__(self, inlst):
        dt = zip(*inlst)[0]
        data = np.hstack(zip(*inlst)[1]).reshape((-1, 2))
        dat = dm.SpaceData()

        dat['Context'] = dm.dmarray(data[:])
        dat['Context'].attrs['CATDESC'] = 'Context data'
        dat['Context'].attrs['FIELDNAM'] = 'Context'
        dat['Context'].attrs['LABLAXIS'] = 'Context data'
        dat['Context'].attrs['SCALETYP'] = 'log'
        #dat['time'].attrs['UNITS'] = 'none'
        dat['Context'].attrs['UNITS'] = ''
        dat['Context'].attrs['VALIDMIN'] = 0
        dat['Context'].attrs['VALIDMAX'] = 2**4-1
        dat['Context'].attrs['VAR_TYPE'] = 'data'
        dat['Context'].attrs['VAR_NOTES'] = 'Context data 6s average'
        dat['Context'].attrs['DEPEND_0'] = 'Epoch'
        dat['Context'].attrs['FILLVAL'] = 2**8-1


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
        b = packet.BIRDpackets(filename)
        print('    Read {0} packets'.format(len(b)))   
        pages = page.fromPackets(b)
        print('    Read {0} pages'.format(len(pages)))
        h = []
        for p in pages:
            h.extend(contextPage(p))
        # drop entries that start with None
        h = [v for v in h if v[0] is not None]
        # sort the data
        h = sorted(h, key = lambda x: x[0])
        return context(h)


