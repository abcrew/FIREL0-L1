import datetime

import numpy as np
from spacepy import datamodel as dm

import FIREdata
import packet


datalen = 24
majorTimelen = 8
minorTimelen = 2
majorLen = datalen+majorTimelen
minorLen = datalen+minorTimelen

#        dat = FIREdata.hex2int(inpage)


class hires(FIREdata.data):
    """
    a hi-res data file
    """
    def __init__(self):
        self.dat = self.getSkel()
        pass 

        ## dt = zip(*inlst)[0]
        ## counts = np.hstack(zip(*inlst)[1]).reshape((-1, 12))
        ## dat = dm.SpaceData()

        ## # go through the data and change the dtype and set the None to fill
        ## # TODO this does not work, need to decide how
        ## tmp = np.zeros(data.shape, dtype=int)
        ## for (i, j), val in np.ndenumerate(data):
        ##     try:
        ##         tmp[i,j] = val
        ##     except (TypeError, ValueError):
        ##         tmp[i,j] = -2**16-1

    def getSkel(self):
        dat = dm.SpaceData()
        dat['Epoch'] = dm.dmarray([])
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
        dat['hr0'] = dm.dmarray([])
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
        dat['hr1'] = dm.dmarray([])
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
        return dat

    def major_data(self, inval):
        """
        read in and add major data to the class
        """
        dt = FIREdata.dat2time(FIREdata.hex2int(inval[:8]))

        d1 = [int(v2 + v1, 16) for (v1, v2) in zip(inval[majorTimelen::2], inval[majorTimelen+1::2])]
        self.dat['Epoch'] = dm.dmarray.append(self.dat['Epoch'], dt)
        if not self.dat['hr0']:
            self.dat['hr0'] = dm.dmarray.hstack(self.dat['hr0'], d1[0:6])
            self.dat['hr1'] = dm.dmarray.hstack(self.dat['hr1'], d1[6:])
        else:
            self.dat['hr0'] = dm.dmarray.vstack(self.dat['hr0'], d1[0:6])
            self.dat['hr1'] = dm.dmarray.vstack(self.dat['hr1'], d1[6:])
            

    def minor_data(self, inval, delta=0.0):
        """
        read in and add minor data to the class
        """
        # get the last time
        dt = self.dat['Epoch'][-1]
        # we need to replace the milliseconds
        us = 1000*( int(inval[0]+inval[1], 16) )
        if  us < self.dat['Epoch'][-1].microsecond:
            dt += datetime.timedelta(seconds=1)
        if us == 1000000:
            print("found us=1000000")
            dt += datetime.timedelta(seconds=1)
        elif us > 1000000:
            print("found us>1000000")
            return
        else:
            dt = dt.replace(microsecond=us)
        d1 = [int(v2 + v1, 16) for (v1, v2) in zip(inval[minorTimelen::2], inval[minorTimelen+1::2])]
        self.dat['Epoch'] = dm.dmarray.append(self.dat['Epoch'], dt)
        self.dat['hr0'] = dm.dmarray.vstack(self.dat['hr0'], d1[0:6])
        self.dat['hr1'] = dm.dmarray.vstack(self.dat['hr1'], d1[6:])

    def read(self, filename):
        h = []
        # need to have pages and packet information
        packets = packet.BIRDpackets(filename)
        
        # If we do not start with a pktnum = 01 skip this page until we find a pktnum
        #  01 because that has the full time stamp
        #  TODO it may be possible to work backwards using the seqidx and seqnum

        epoch = []
        tmp = []
        data  = []
        dataBuffer = []
        newPage = True
        lastPktnum = 1
        """
        loop over all the packets pulling data out into a data buffer for decoding
        """
        for p in packets:
            if newPage and int(p.pktnum, 16) != lastPktnum:
                print("Page did not start with packet '01' skipping packet {0}, cannot find time".format(p))
                continue
            elif not newPage and int(p.pktnum, 16) < lastPktnum+1: # new page starting
                newPage=True
            if newPage and int(p.pktnum, 16) == 1: # this is the first packet in a page
                print p
                # this is a decodable page, start now
                dataBuffer.extend(p.data)
                lastPktnum = int(p.pktnum, 16)
                newPage = False
                # since p.pktnum == 1 this is a major time stamp, decode it.
                tmp = [dataBuffer.pop(0) for v in range(majorLen)]
                self.major_data(tmp)
            elif not newPage and int(p.pktnum, 16) == lastPktnum+1:
                # this is not the start of a page but the next in sequence
                print p
                # this is a decodable page, start now
                dataBuffer.extend(p.data)
                lastPktnum = int(p.pktnum, 16)
                newPage = False
                while len(dataBuffer) >= minorLen:
                    # since p.pktnum == 1 this is a major time stamp, decode it.
                    tmp = [dataBuffer.pop(0) for v in range(minorLen)]
                    self.minor_data(tmp)
            elif not newPage and int(p.pktnum, 16) > lastPktnum+1:
                """
                here we need to add time per missing packet
                222/26. * 75/4 = 160.09615384615384 ms
                222 - bytes per page seems normal
                26. is gthe bytes per data with a minor time
                75 is 15ms*3 + 30ms
                4 is average time per measurment

                Then we need to sync back up since there will be left over data in the new packet
                should do that by last_time + missingNum*160ms
                move a byte at a time to find a minor near that, then look 24 bytes later for another that makes sense
                the current data in dataBuffer should be dropped
                """                # TODO here!!
                # this is not the start of a page and there was one or more missed
                print p
                print("Missing packet, flushed {0} bytes form dataBuffer".format(len(dataBuffer)))
                dataBuffer = []
                # this is a decodable packet, start now
                dataBuffer.extend(p.data)
                microseconds=1000*(int(p.pktnum, 16)-lastPktnum)*160
                dt = self.dat['Epoch'][-1] + datetime.timedelta(microseconds=microseconds)
                # loop over the data looking for a timestamp that is close
                for i in range(len(dataBuffer)):
                    if np.abs(microseconds - int(dataBuffer[i]+dataBuffer[i+1], 16)) < 30:
                        1/0
                lastPktnum = int(p.pktnum, 16)
                newPage = False

                while len(dataBuffer) >= minorLen:
                    # since p.pktnum == 1 this is a major time stamp, decode it.
                    tmp = [dataBuffer.pop(0) for v in range(minorLen)]
                    self.minor_data(tmp)
            
                
        1/0
                        
        print("Decoded {0} hires measurements".format(len(h)))
        return hires(h)

        



"""
a missing page means 248 / 26 => 9.5 samples missing the ms should be valid
just 15*9=135 ms later so it might oftern roll over
"""



