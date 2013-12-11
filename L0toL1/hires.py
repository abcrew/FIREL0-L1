import datetime

import numpy as np
from spacepy import datamodel as dm

import FIREdata
import packet
from page import page



def printHiresPage(inpage):
    """
    print out a hires page for debugging
    """
    # the first one is 8 bytes then 24
    dat = inpage.split(' ')
    print ' '.join(dat[0:datalen+majorTimelen])
    for ii in range(datalen+majorTimelen, len(dat), datalen+minorTimelen):
        print ' '.join(dat[ii:ii+datalen+minorTimelen])


datalen = 24
majorTimelen = 8
minorTimelen = 2

class hiresPage(FIREdata.dataPage):
    """
    a page of hires data

    each hi res starts a page with a full 8 byte time stamp then
    24 bytes of data then a 2 byte ms then 24 then 2 on and on
    """
    def __init__(self, inpage):
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

        if (np.asarray(inval) == '00').all(): # is this line fill?
            return
        dt = FIREdata.dat2time(inval[0:8])
        d1 = np.asarray(inval[self._majorTimelen::2])
        d2 = np.asarray(inval[self._majorTimelen+1::2])
        self.append([dt, d2*2**8+d1])

    def minor_data(self, inval):
        """
        read in and add minor data to the class
        """
        if (np.asarray(inval) == '00').all(): # is this line fill?
            return
        # get the last time
        dt = self[-1][0]
        # we need to replace the milliseconds
        us = 1000*(inval[0]*2**8 + inval[1])
        if  us < self[-1][0].microsecond:
            dt += datetime.timedelta(seconds=1)
        if us == 1000000:
            print("found us=1000000")
            dt += datetime.timedelta(seconds=1)
        elif us > 1000000:
            print("found us>1000000")
            return
        else:
            dt = dt.replace(microsecond=us)
        d1 = np.asarray(inval[self._minorTimelen::2])
        d2 = np.asarray(inval[self._minorTimelen+1::2])
        self.append([dt, d2*2**8+d1])


class hires(FIREdata.data):
    """
    a hi-res data file
    """
    def __init__(self, inlst):
        dt = zip(*inlst)[0]
        counts = np.hstack(zip(*inlst)[1]).reshape((-1, 12))
        dat = dm.SpaceData()

        # go through the data and change the dtype and set the None to fill
        # TODO this does not work, need to decide how
        tmp = np.zeros(data.shape, dtype=int)
        for (i, j), val in np.ndenumerate(data):
            try:
                tmp[i,j] = val
            except (TypeError, ValueError):
                tmp[i,j] = -2**16-1

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

# TODO working here
    @classmethod
    def read(self, filename):
        h = []
        # need to have pages and packet information
        pages, pktnum = super(hires, self).read(filename, retpktnum=True)
        # If we do not start with a pktnum = 01 skip this page until we find a pktnum
        #  01 because that has the full time stamp
        #  TODO it may be possible to work backwards using the seqidx and seqnum

        for p in pages:
            # is a page dpes not start with packet zero it is lost
            #   as the absolute time cannot be figured out
            1/0
            start_ind = 0
            stop_ind  = start_ind + datalen + majorTimelen
##            while stop_ind < (len(p)-minorTimelen-datalen):
            while stop_ind < len(p):
                skipped = 0
                if None not in p[start_ind:stop_ind]:
                    # the data is all there in a row just make a hires object
                    cp = hiresPage(p[start_ind:stop_ind], h)
                else:
                    print("Encountered a missing packet")
                    missing_ind = p[start_ind:stop_ind].index(None)
                    if missing_ind < (minorTimelen-1):
                        # did not have a whole time stamp skip the hires there is not useful info
                        print("\tSkipped data no time stamp".format())
                        skipped=1
                    elif missing_ind >= (minorTimelen+1)-1:
                        # this means we have a valid time stamp and at least 1 valid measurement
                        #    so fill in the missing bytes with 00 and then set it to None
                        #    the hires() class then needs to catch the None and set to fill
                        fill = ['00'] * ((minorTimelen+datalen) - missing_ind)
                        cp = hiresPage(p[start_ind:stop_ind][0:missing_ind] + fill, h)
                        cp[0][1][1] = [None]
                        print("\t{0} Filled some data".format(cp[0][0].isoformat()))
                        stop_ind -= (len(p[start_ind:stop_ind])-missing_ind-1)
                        skipped=1
                    else:
                        # this means no valid data so fill in the missing bytes with 00 and then set it to None
                        #    the hires() class then needs to catch the None and set to fill
                        #    we are keeping this since there was a valid time stamp
                        fill = ['00'] * ((minorTimelen+datalen) - missing_ind)
                        cp = hiresPage(p[start_ind:stop_ind][0:missing_ind] + fill, h)
                        if cp:
                            cp[0][1][:] = [None, None]
                            print("\t{0} Filled all data".format(cp[0][0].isoformat()))
                        stop_ind -= (len(p[start_ind:stop_ind])-missing_ind-1)
                        skipped=1

                start_ind = stop_ind
                if skipped:
                    # we need to get back on sync, for these data that means finding a
                    #   valid date in the data
                    # for Hires we need to find 2 minors in 14 bytes
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
                        
        print("Decoded {0} hires measurements".format(len(h)))
        return hires(h)




"""
a missing page means 248 / 26 => 9.5 samples missing the ms should be valid
just 15*9=135 ms later so it might oftern roll over
"""



