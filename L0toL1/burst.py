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


datalen = 10
majorTimelen = 8
minorTimelen = 2 

class burstPage(FIREdata.dataPage):
    """
    a page of burst data
    """
    def __init__(self, inpage, h):
        len1 = datalen+majorTimelen
        len2 = datalen+minorTimelen
        dat = FIREdata.hex2int(inpage)

        if len(inpage) == len1: # major
            try:
                self.t0 = FIREdata.dat2time(dat[0:8])
                self.major_data(dat)
            except ValueError:
                return
            print("\tData at time {0} decoded".format(self[-1][0].isoformat()))
        elif len(inpage) == len2: # minor
            try:
                self.minor_data(dat, h)
            except ValueError:
                return
        
    def major_data(self, inval):
        """
        read in and add major data to the class
        """
        dt = FIREdata.dat2time(inval[0:8])
        # there are 10 times 100ms each before this one

        # dt is the time that was in the fill stamp
        #   the data that follow are each 100 ms after dt
        dt2 = [dt + datetime.timedelta(microseconds=100e3)*i for i in range(0,10)]
        # get the data from inval
        d1 = np.asarray(inval[ majorTimelen:])
        # change in the invals back to hex so that they can be
        #    split on the nibble
        d1 = np.asanyarray(['{:02x}'.format(v) for v in d1])
        # split them on the nibble
        d2 = [int(v[0], 16) for v in d1]
        d3 = [int(v[1], 16) for v in d1]
        dout = zip(d2, d3)
        for v1, v2 in zip(dt2, dout):
            self.append( (v1, v2) )

    def minor_data(self, inval, h):
        """
        read in and add minor data to the class
        """
        dt = h[-1][0] # this is the last time
        minute = inval[0]
        second = inval[1]
        # increment all measurements by 100ms
        dt2 = [dt + datetime.timedelta(microseconds=100e3)*i for i in range(1,11)]
        if dt2[0].minute != minute or dt2[0].second != second:
            print('\tBurst lost sync, cannot recover page')
            return
        d1 = np.asarray(inval[minorTimelen:])
        d1 = np.asanyarray(['{:02x}'.format(v) for v in d1])
        # split them on the nibble
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

        # go through Brurst and change the data type and set the None to fill
        tmp = np.zeros(data.shape, dtype=int)
        for (i, j), val in np.ndenumerate(data):
            try:
                tmp[i,j] = val
            except (TypeError, ValueError):
                tmp[i,j] = -2**16-1

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
        dat['Burst'].attrs['FILLVAL'] = -2**16-1

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

# TODO working here
    @classmethod
    def read(self, filename):
        h = []
        pages = super(burst, self).read(filename)
        # use a sliding window to find valid packets
        for p in pages:
            start_ind = 0
            stop_ind  = start_ind + datalen + majorTimelen
##            while stop_ind < (len(p)-minorTimelen-datalen):
            while stop_ind < len(p):
                skipped = 0
                if None not in p[start_ind:stop_ind]:
                    # the data is all there in a row just make a burst object
                    cp = burstPage(p[start_ind:stop_ind], h)
                else:
                    print("Encountered a missing packet")
                    missing_ind = p[start_ind:stop_ind].index(None)
                    if missing_ind < (minorTimelen-1):
                        # did not have a whole time stamp skip the burst there is not useful info
                        print("\tSkipped data no time stamp".format())
                        skipped=1
                    elif missing_ind >= (minorTimelen+1)-1:
                        # this means we have a valid time stamp and at least 1 valid measurement
                        #    so fill in the missing bytes with 00 and then set it to None
                        #    the burst() class then needs to catch the None and set to fill
                        fill = ['00'] * ((minorTimelen+datalen) - missing_ind)
                        cp = burstPage(p[start_ind:stop_ind][0:missing_ind] + fill, h)
                        cp[0][1][1] = [None]
                        print("\t{0} Filled some data".format(cp[0][0].isoformat()))
                        stop_ind -= (len(p[start_ind:stop_ind])-missing_ind-1)
                        skipped=1
                    else:
                        # this means no valid data so fill in the missing bytes with 00 and then set it to None
                        #    the burst() class then needs to catch the None and set to fill
                        #    we are keeping this since there was a valid time stamp
                        fill = ['00'] * ((minorTimelen+datalen) - missing_ind)
                        cp = burstPage(p[start_ind:stop_ind][0:missing_ind] + fill, h)
                        if cp:
                            cp[0][1][:] = [None, None]
                            print("\t{0} Filled all data".format(cp[0][0].isoformat()))
                        stop_ind -= (len(p[start_ind:stop_ind])-missing_ind-1)
                        skipped=1

                start_ind = stop_ind
                if skipped:
                    # we need to get back on sync, for these data that means finding a
                    #   valid date in the data
                    # for Burst we need to find 2 minors in 14 bytes
                    skip_num = 0
                    try:
                        while start_ind < len(p) and \
                              ((int(p[start_ind], 16)-int(p[start_ind+minorTimelen+datalen],16)) != 0 or \
                               (int(p[start_ind], 16)-int(p[start_ind+minorTimelen+datalen],16)) != 1) and \
                              ((int(p[start_ind+1], 16)-int(p[start_ind+minorTimelen+datalen+1],16)) != 1 or \
                               (int(p[start_ind+1], 16)-int(p[start_ind+minorTimelen+datalen+1],16)) < 0):
                            start_ind += 1
                            skip_num += 1
                    except IndexError:
                        continue
                    # TODO needed another +1 here for some reason
                    start_ind += 1
                    skip_num += 1
                    print("\t\tSkipped {0} bytes at the start of the next packet".format(skip_num))

                stop_ind = start_ind + (datalen + minorTimelen)
                h.extend(cp)
                        
        print("Decoded {0} burst measurements".format(len(h)))
        return burst(h)


