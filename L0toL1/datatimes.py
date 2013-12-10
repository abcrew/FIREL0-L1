import datetime

import numpy as np
from spacepy import datamodel as dm

import FIREdata
import packet
from page import page


def printDatatimesPage(inpage):
    """
    print out a Datatimes page for debugging
    """
    # the first one is 8+8 bytes then 8+8
    dat = inpage.split(' ')
    print ' '.join(dat[0:8+8])
    for ii in range(16+8, len(dat), 16):
        print ' '.join(dat[ii:ii+16])

class datatimesPage(FIREdata.dataPage):
    """
    a page of Datatimes data
    """
    def __init__(self, inpage):
        self._datalen = 8
        self._majorTimelen = 8
        dat = FIREdata.hex2int(inpage)

        self.t0 = FIREdata.dat2time(dat[0:8])

        # now the data length is 8
        for ii in range(0, len(dat), self._datalen): # the index of the start of each FIRE data
            stop = ii+self._datalen+self._majorTimelen  
            self.major_data(dat[ii:stop])
        # cull any bad data
        ## this has None in place of data
        self = [v for v in self if None not in v]    
        # sort the data
        self = sorted(self, key = lambda x: x[0])

    def major_data(self, inval):
        """
        read in and add major data to the class
        """
        if not any(inval): # is this line fill?
            return
        try:
            dt = FIREdata.dat2time(inval[0:8])
        except ValueError:
            return
        try:
            d1 = FIREdata.dat2time(inval[ self._majorTimelen:])
        except ValueError:
            return
        self.append([dt, d1])


class datatimes(FIREdata.data):
    """
    a datatimes data file
    """
    def __init__(self, inlst):
        dt = zip(*inlst)[0]
        data = np.hstack(zip(*inlst)[1]).reshape((-1, 1))
        dat = dm.SpaceData()

        dat['Time'] = dm.dmarray(data[:,0])
        dat['Time'].attrs['CATDESC'] = 'Start or stop Time'
        dat['Time'].attrs['FIELDNAM'] = 'Time'
        dat['Time'].attrs['LABLAXIS'] = 'Start or stop Time'
        dat['Time'].attrs['SCALETYP'] = 'linear'
        #dat['Time'].attrs['UNITS'] = 'none'
        dat['Time'].attrs['VALIDMIN'] = datetime.datetime(1990,1,1)
        dat['Time'].attrs['VALIDMAX'] = datetime.datetime(2029,12,31,23,59,59,999000)
        dat['Time'].attrs['VAR_TYPE'] = 'support_data'
        dat['Time'].attrs['VAR_NOTES'] = 'Time data started or stopped'
        dat['Time'].attrs['DEPEND_0'] = 'Epoch'
        dat['Time'].attrs['FILLVAL'] = 'None'

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

        dat['Mode'] = dm.dmarray(np.zeros(len(dt), dtype=int))
        dat['Mode'][...] = -1
        dat['Mode'].attrs['FIELDNAM'] = 'Mode'
        dat['Mode'].attrs['FILLVAL'] = -1
        dat['Mode'].attrs['LABLAXIS'] = 'FIRE Mode'
        dat['Mode'].attrs['SCALETYP'] = 'linear'
        dat['Mode'].attrs['VALIDMIN'] = 0
        dat['Mode'].attrs['VALIDMAX'] = 1
        dat['Mode'].attrs['VAR_TYPE'] = 'support_data'
        dat['Mode'].attrs['VAR_NOTES'] = 'Is the line FIRE on (=1) or FIRE off (=0)'
        dat['Mode'][::2] = 1
        dat['Mode'][1::2] = 0

        dat['Duration'] = dm.dmarray(np.zeros(len(dt), dtype=int))
        dat['Duration'][...] = -1
        dat['Duration'].attrs['FIELDNAM'] = 'Duration'
        dat['Duration'].attrs['FILLVAL'] = -1
        dat['Duration'].attrs['LABLAXIS'] = 'FIRE Duration'
        dat['Duration'].attrs['SCALETYP'] = 'linear'
        dat['Duration'].attrs['VALIDMIN'] = 0
        dat['Duration'].attrs['VALIDMAX'] = 100000
        dat['Duration'].attrs['VAR_TYPE'] = 'support_data'
        dat['Duration'].attrs['VAR_NOTES'] = 'Duration of the on or off'
        df = np.asarray([ v1 - v2 for v1, v2 in zip(dat['Time'],dat['Epoch']) ])
        dat['Duration'][...] = np.asarray([ v.days*24*60*60 + v.seconds for v in df ])
        
        self.data = dat

    @classmethod
    def read(self, filename):
        pages = super(datatimes, self).read(filename)
        h = []
        for p in pages:
            h.extend(datatimesPage(p))
        # cull any bad data
        ## this has None in place of data
        h = [v for v in h if None not in v]    
        # sort the data
        h = sorted(h, key = lambda x: x[0])
        return datatimes(h)

