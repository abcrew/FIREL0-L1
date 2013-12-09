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

datalen = 6
majorTimelen = 8
minorTimelen = 8 # no minor

class contextPage(FIREdata.dataPage):
    """
    a page of context data
    """
    def __init__(self, inpage):
        len1 = datalen+majorTimelen
        len2 = datalen+minorTimelen
        dat = FIREdata.hex2int(inpage)
        try:
            self.t0 = FIREdata.dat2time(dat[0:8])
        except ValueError:
            return
        self.major_data(dat[0:datalen+majorTimelen])
        start = datalen+majorTimelen
        # the index of the start of each FIRE data
        for ii in range(start, len(dat), datalen+minorTimelen): 
            stop = ii+datalen+majorTimelen
            try:
                self.minor_data(dat[ii:stop])
            except IndexError: # malformed data for some reason, skip it
                print("Skipping malformed context: {0}".format(dat[ii:stop]))
        # sort the data
        self = sorted(self, key = lambda x: x[0])

    def major_data(self, inval):
        """
        read in and add major data to the class
        """
        if (np.asarray(inval) == 0).all(): # is this line fill?
            return
        dt = FIREdata.dat2time(inval[0:8])
        d1 = np.asarray(inval[ majorTimelen:])
        d1 = np.asanyarray(['{0}'.format(v) for v in d1])
        d2 = int(d1[2] + d1[1] + d1[0], 16)
        d3 = int(d1[5] + d1[4] + d1[3], 16)
        dout = [d2, d3]
        self.append( (dt, dout) )

    minor_data = major_data

class context(FIREdata.data):
    """
    a context data file
    """
    def __init__(self, inlst):
        dt = zip(*inlst)[0]
        data = np.hstack(zip(*inlst)[1]).reshape((-1, 2))

        # go through Context and change the data type and set the None to fill
        tmp = np.zeros(data.shape, dtype=int)
        for (i, j), val in np.ndenumerate(data):
            try:
                tmp[i,j] = val
            except (TypeError, ValueError):
                tmp[i,j] = -2**16-1

        
        dat = dm.SpaceData()

        dat['Context'] = dm.dmarray(tmp[:])
        dat['Context'].attrs['CATDESC'] = 'Context data'
        dat['Context'].attrs['FIELDNAM'] = 'Context'
        dat['Context'].attrs['LABLAXIS'] = 'Context data'
        dat['Context'].attrs['SCALETYP'] = 'log'
        #dat['time'].attrs['UNITS'] = 'none'
        dat['Context'].attrs['UNITS'] = ''
        dat['Context'].attrs['VALIDMIN'] = 0
        dat['Context'].attrs['VALIDMAX'] = 2**15-1
        dat['Context'].attrs['VAR_TYPE'] = 'data'
        dat['Context'].attrs['VAR_NOTES'] = 'Context data 6s average'
        dat['Context'].attrs['DEPEND_0'] = 'Epoch'
        dat['Context'].attrs['FILLVAL'] = -2**16-1

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
        h = []
        pages = super(context, self).read(filename)
        # use a sliding window to find valid packets
        for p in pages:
            start_ind = 0
            stop_ind  = start_ind + datalen + majorTimelen
            while stop_ind < (len(p)-majorTimelen-datalen):
                skipped = 0
                if None not in p[start_ind:stop_ind]:
                    # the data is all there in a row just make a context object
                    cp = contextPage(p[start_ind:stop_ind])
                else:
                    # print("Encountered a missing packet")
                    missing_ind = p[start_ind:stop_ind].index(None)
                    if missing_ind < (majorTimelen-1):
                        # did not have a whole time stamp skip the context there is not useful info
                        print("\tSkipped data no time stamp".format())
                        skipped=1
                    elif missing_ind >= (majorTimelen+datalen/2)-1:
                        # this means we have a valid time stamp and 1 valid measurement
                        #    so fill in the missing bytes with 00 and then set it to None
                        #    the context() class then needs to catch the None and set to fill
                        fill = ['00'] * ((majorTimelen+datalen) - missing_ind)
                        cp = contextPage(p[start_ind:stop_ind][0:missing_ind] + fill)
                        cp[0][1][1] = [None]
                        print("\t{0} Filled some data".format(cp[0][0].isoformat()))
                        stop_ind -= (len(p[start_ind:stop_ind])-missing_ind-1)
                        skipped=1
                    else:
                        # this means no valid data so fill in the missing bytes with 00 and then set it to None
                        #    the context() class then needs to catch the None and set to fill
                        #    we are keeping this since there was a valid time stamp
                        fill = ['00'] * ((majorTimelen+datalen) - missing_ind)
                        cp = contextPage(p[start_ind:stop_ind][0:missing_ind] + fill)
                        if cp:
                            cp[0][1][:] = [None, None]
                            print("\t{0} Filled all data".format(cp[0][0].isoformat()))
                        stop_ind -= (len(p[start_ind:stop_ind])-missing_ind-1)
                        skipped=1

                start_ind = stop_ind
                if skipped:
                    # we need to get back on sync, for these data that means finding a
                    #   valid date in the data
                    skip_num = 0
                    while start_ind < len(p) and \
                              len(p[start_ind:]) > majorTimelen+datalen and \
                              not FIREdata.validDate(p[start_ind:start_ind+majorTimelen+datalen]):
                        start_ind += 1
                        skip_num += 1
                    print("\t\tSkipped {0} bytes at the start of the next packet".format(skip_num))

                stop_ind = start_ind + (datalen + majorTimelen)
                h.extend(cp)
                        
        print("Decoded {0} context measurements".format(len(h)))
        return context(h)


