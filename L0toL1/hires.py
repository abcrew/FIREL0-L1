from __future__ import division

from collections import deque
import copy
import datetime
import time

import numpy as np
from spacepy import datamodel as dm

from dataSkeletons import getSkelHIRES
import FIREdata
from FIREdata import total_seconds
import packet

MFIB_transfer_time = 10*48 / 115200 * 1e6 # microseconds
# this is 48 bytes, 8 bits per byte, plus a start and stop
#  transferred at 115200 baud, then 1e6 seconds to microseconds
MFIB_transfer_timeDT = datetime.timedelta(microseconds=MFIB_transfer_time)

measurement_time = 18.75*1e3 # this is settable but I bet we will not change it.
# this is 18.75ms measurment and then 1e3 to go o microseconds
measurement_timeDT = datetime.timedelta(microseconds=measurement_time)

datalen = 24
majorTimelen = 8
minorTimelen = 2
majorLen = datalen+majorTimelen
minorLen = datalen+minorTimelen

measurement_per_packet = 238 // minorLen
# this is the number of measurments we have to add if we miss a packet

time_diffDT =  [datetime.timedelta(microseconds=11.25e3),
                datetime.timedelta(microseconds=7.5e3),
                datetime.timedelta(microseconds=3.75e3),
                datetime.timedelta(microseconds=0e3),]
#                datetime.timedelta(microseconds=15e3)]




def timeDuration(msg, tm):
    tm2 = time.time()
    print("{0} took {1:0.2f} seconds".format(msg, tm2-tm))
    return tm2


def index(val, data):
    """
    given a numpy array find the first occurance of val in the array
    - this is a feature request in numpy 2.x
    - same as the [].index() for a list
    """
    for ii, v in enumerate(data):
        if val == v:
            return ii
    raise(ValueError("{0} is not in in the array".format(val)))

class contigousPackets(list):
    """
    class to hold contigous packets
    """
    def majorStamps(self):
        """
        return the major time stamps
        """
        major = []
        for v in self:
            if v.pktnum == '01': # this is a major stamp
                major.append(v)
        stamps = []
        for v in major:
            stamps.append(FIREdata.dat2time(FIREdata.hex2int(v.data[:8])))
        return stamps

    @classmethod
    def fromPackets(cls, inval):
        """
        given an input list of packets return a list of contigousPackets() objects
        for each contigous chunk in the input list
        """
        # loop over all the packets
        # place first into a new contigousPackets() object
        # if the next is contigous append it
        # else make a new object and continue
        ans = []
        cp = cls([inval[0]])
        for v in inval[1:]: # loop over packets
            if cls.isContigous(cp[-1], v):
                cp.append(v)
            else:
                ans.append(cp)
                cp = cls([v])
        if cp:
            ans.append(cp)
        return ans            
        
        
    @staticmethod
    def isContigous(in1, in2):
        """
        return True if in2 is contigous after in1 False otherwise
        """
        if in1.seqnum != in2.seqnum: # different request
            return False
        if (in1.seqidx == in2.seqidx) and \
               (int(in1.pktnum, 16)+1 == int(in2.pktnum, 16)):
            # same page, next packet
            return True
        if (int(in1.seqidx, 16)+1 == int(in2.seqidx, 16)) and  \
           (in1.pktnum == '13' and in2.pktnum == '01'):
            # next page, first to last packet
            return True
        return False

class hires(FIREdata.data):
    """
    a hi-res data file
    """
    def __init__(self):
        self.dat = getSkelHIRES()
        self.meas_ind = 0
        self.start_ind = 0
        self.stop_ind = 0
        self.Epoch = []
        self.Timestamp = []
        self.hr0 = []
        self.hr1 = []
        self.Flag = []
        self.seqnum = []
        self.seqidx = []
        self.pktnum = []
        self.grt = []

    @staticmethod
    def inc_minor_time(dt, inval):
        # we need to replace the milliseconds
        us = 1000*( int(inval[0]+inval[1], 16) )
        ## print("DT: {0}  us: {1}  delta: {2}".format(dt, us, us-dt.microsecond))
        if  us < dt.microsecond:
            dt += datetime.timedelta(seconds=1)
        #if us == 1000000:
        #    print("found us=1000000")
        #    dt += datetime.timedelta(seconds=1)
        dt = dt.replace(microsecond=us)
        return dt

    
    def minor_data(self, inval, info, firstTime=None):
        """
        read in and add minor data to the class
        """
        ##   print("\t\tIN MINOR"), 
        # get the previous stamp time
        if firstTime is not None:
            dt = firstTime
        else:
            dt = self.Timestamp[-1]
        # take that stamp time and increment
        try:
            t1 = self.inc_minor_time(dt, inval[0:2]) # pass the timestamp in
        except ValueError:
            # for some reason there is a us > 100000 sometimes... bit flip?
            return
        self.Timestamp.extend([t1])
        ##   print(" {0} ".format(t1.isoformat()))

        # combine th nibbles and convert to an int
        d1 = [int(v2 + v1, 16) for (v1, v2) in
              zip(inval[minorTimelen::2], inval[minorTimelen+1::2])]
        # set the data at the correct index to the decoded data
        self.hr0.append(d1[0:6])
        self.hr1.append(d1[6:])

        # just use the info from the first bit of the data
        self.seqnum.append( int(info[0].seqnum, 16))
        self.seqidx.append( int(info[0].seqidx, 16))
        self.pktnum.append( int(info[0].pktnum, 16))

    def decodeWhile(self, dataBuffer, dataInfo, firstTime):
        """
        regardless of the packet if there is more data in the buffer we should
        decode it and add it to the arrays

        firstTime is the time at the start of the dataBuffer, as the are always contigous
        this is a safe thing to pass along
        """
        tmp = [dataBuffer.pop(0) for v in range(minorLen)]
        tmpinfo = [dataInfo.pop(0) for v in range(minorLen)]
        ##  print("\tIn while {0} bytes left in buffer".format(len(dataBuffer)))
        self.minor_data(tmp, tmpinfo, firstTime=firstTime)
        
        while len(dataBuffer) >= minorLen:
            # grab the data and trim the buffer
            tmp = [dataBuffer.pop(0) for v in range(minorLen)]
            tmpinfo = [dataInfo.pop(0) for v in range(minorLen)]
            ##   print("\tIn while {0} bytes left in buffer".format(len(dataBuffer)))
            self.minor_data(tmp, tmpinfo)

    def timestampToEpoch(self):
        """
        change the timestamps to Epoch, be 15, 15, 15, 30 aware
        """
        tm = self.Timestamp[self.start_ind:self.stop_ind+1]
        tm_diff = np.diff(tm)
        try:
            ind30 = tm_diff.tolist().index(datetime.timedelta(0, 0, 30000))
            flag = 0
        except ValueError: # hmm... odd issue where deltas are all over the place
            # assume first one is good
            ind30=1
            flag = -1
        if ind30 == 0:
            tm_diff = np.diff(tm[1:])
            # the +1 since we skipped one
            try:
                ind30 = tm_diff.tolist().index(datetime.timedelta(0, 0, 30000))+1
                flag = 0 
            except ValueError: # hmm... odd issue where deltas are all over the place
                # assume first one is good
                ind30=1
                flag = -1
        # the time one before the 30 is the real time, then all others are
        #  18.75 ms from there
        epoch0 = self.Timestamp[self.start_ind:][ind30-1]
        n_pre = ind30-1
        epoch = [epoch0 - datetime.timedelta(microseconds=18.75*1e3*v) for v in range(n_pre, 0, -1)]
        epoch += [epoch0]
        epoch += [epoch0 + datetime.timedelta(microseconds=18.75*1e3*v)
                  for v in range(n_pre+1, len(tm), 1)]
        self.Epoch.extend(epoch)
        tmp = np.zeros(len(epoch), dtype=int)
        tmp.fill(flag)
        self.Flag.append(tmp)
            
    @staticmethod
    def stampToData(inval):
        """
        take a datetime and figure out what the data would have to be
        for that stamp
        """
        vals = inval.strftime("%y,%m,%d,%H,%M,%S,%f").split(',')
        vals2 = ['{0:02X}'.format(int(v)) for v in vals[:-1]]
        tmp = '{0:04X}'.format(int(vals[-1])//1000)
        vals2.extend([tmp[:2], tmp[2:]])
        return vals2

    def read(self, filename):
        # need to have pages and packet information
        tm = time.time()
        packets = packet.BIRDpackets(filename)
        tm = timeDuration("Packet read", tm)
        
        cp = contigousPackets.fromPackets(packets)
        # TODO for now drop all contigousPackets() that don't have a majorStamp
        cp = [v for v in cp if v.majorStamps() and len(v) > 30]
        # at least 30 contigous packets to bother

        print( "Decoding data from {0} contigous segments".format( len(cp) ))

        # now cp is a list of contigousPackets() so a lot of checking is unneeded

        while len(cp) > 0:
            packets_ = cp.pop(0)
            time0 = time.time()
            self.start_ind = len(self.Timestamp)
            majors = packets_.majorStamps() # get the major timestamps
            dataBuffer = [] # clear any remaining data
            dataInfo = [] # clear any remaining info
            for packet_ in packets_:  # loop over each packet in the contigousPackets()
                if packet_.pktnum == '13': # last packet of a page
                    packet_.data = packet_.data[:-8] # throw away the fill bytes
                # here combine all the data together and decode         
                dataBuffer.extend(packet_.data) # grab the data out
                dataInfo.extend([packet_]*len(packet_.data))
            # search through the data for the major stamps and then sync up the time
            # TODO is there a chance that the data could look like major stamps?
            #   probably, but unlikely, if there is more than one sync to them all
            #   then the probability drops more
            findme = [hires.stampToData(v) for v in majors]
            # the /2 is since each element has 2 bytes (characters)
            ind = np.asarray([FIREdata.sublistExists(dataBuffer, v) for v in findme])//2
            if None in ind:
                raise(ValueError("Did not find the timestamp in the data!!"))
            # figure out what time the first major makes the first minor entry
            #   1) also if the first data is not a major some data will have to be thrown away
            #   2) think on the 15, 15, 15, 30 pattern and how to propigate that backwards

            # loop over all the values of ind changing majors to minors and removing fill
            for jj, ind_n in enumerate(ind):
                ##  print(dataBuffer[ind[jj]:ind[jj]+50])
                ##  print len(dataBuffer), len(dataInfo)
                dataBuffer = FIREdata.majorToMinor(dataBuffer, ind[jj])
                dataInfo = FIREdata.majorToMinor(dataInfo, ind[jj])
                ## print(dataBuffer[ind[jj]:ind[jj]+50])
                ## print len(dataBuffer), len(dataInfo)
                # now the indicies of the rest are 6 too high, fix them
                ind[jj+1:] = ind[jj+1:]-6
                ##  print(dataBuffer[ind[jj]:ind[jj]+50])
                if jj == 0:
                    # 1) to remove them look for matching minors at the start that
                    #      is the number of extra bytes
                    ##  print(dataBuffer[:40])
                    # find the start of the data in the stream
                    extra = FIREdata.findMinors(dataBuffer, minorLen)
                    ind -= extra # all of the inds here
                    for ii in range(extra):
                        dataBuffer.pop(0)
                        dataInfo.pop(0)
                    ##  print len(dataBuffer), len(dataInfo)
                    ##  print(dataBuffer[ind[jj]:ind[jj]+50])
                # there could well be fill inside the data before the end of a page
                #   loop over all the minors looking for all zeros after
                fill = FIREdata.findFill(dataBuffer, minorLen, ind[jj])
                if ind[jj] > fill:
                    for ii in range(ind[jj]-fill):
                        dataBuffer.pop(fill)
                        dataInfo.pop(fill)
                    ## if ind[jj] % minorLen != 0:
                    ##     raise(ValueError("Fill removal failed"))
                    ind[jj:] -= ind[jj]-fill
            # 2) Now that we have the right starting place
            #    and the data all prepared for decoding
            # figure out the time for the first timestamp
            n_minors = ind[0] // minorLen

            # the time back to the start is
            avg_t = np.average([15, 15, 15, 30])*1e3
            start_t = majors[0] - datetime.timedelta(microseconds=avg_t*(n_minors+3))
            while len(dataBuffer) > minorLen:
                try:
                    firstTime = self.inc_minor_time( start_t, dataBuffer[0:2] )
                    break
                except ValueError:
                    dataBuffer = dataBuffer[minorLen:]
                    dataInfo = dataInfo[minorLen:]
                    ind += minorLen
            ##  print majors[0], start_t, majors[0]-start_t

            self.decodeWhile(dataBuffer, dataInfo, firstTime)
            # now that all the data are decoded create the epoch variable
            #   from the timestamps
            self.stop_ind = len(self.Timestamp)-1
            self.timestampToEpoch()
            print('{3} to go: Decoded data from {0} to {1}  --  {2}  ({4:0.2f}s)'.format(self.Epoch[self.start_ind].isoformat(),
                                                                self.Epoch[self.stop_ind].isoformat(),
                                                                self.Epoch[self.stop_ind]-self.Epoch[self.start_ind], len(cp), time.time()-time0))

        self.dat['Epoch'] = dm.dmarray.append(self.dat['Epoch'], self.Epoch)
        self.dat['Timestamp'] = dm.dmarray.append(self.dat['Timestamp'], self.Timestamp)
        hr0 = np.asarray(self.hr0)
        hr1 = np.asarray(self.hr1)
        self.dat['hr0'] = dm.dmarray.append(self.dat['hr0'], hr0).reshape(-1, 6)
        self.dat['hr1'] = dm.dmarray.append(self.dat['hr1'], hr1).reshape(-1, 6)
        self.dat['Flag'] = dm.dmarray.append(self.dat['Flag'], self.Flag)
        self.dat['seqnum'] = dm.dmarray.append(self.dat['seqnum'], self.seqnum)
        self.dat['seqidx'] = dm.dmarray.append(self.dat['seqidx'], self.seqidx)
        self.dat['pktnum'] = dm.dmarray.append(self.dat['pktnum'], self.pktnum)
        ## self.dat['pktnum'] = self.dat['pktnum'][len(self.dat['pktnum'])-len(self.dat['Epoch']):]
        del self.dat['Flag']

        # go through and remove duplicate times and data
        print("Looking for duplicate measurements")

        arr, dt_ind, return_inverse = np.unique(self.dat['Epoch'], return_index=True, return_inverse=True) # this is unique an sort
        print("Found {0} duplicates of {1}".format(len(return_inverse)-len(dt_ind), len(return_inverse)))

        self.dat['Epoch'] = arr
        self.dat['Timestamp'] = self.dat['Timestamp'][dt_ind]
        self.dat['hr0'] = self.dat['hr0'][dt_ind]
        self.dat['hr1'] = self.dat['hr1'][dt_ind]
        self.dat['seqnum'] = self.dat['seqnum'][dt_ind]
        self.dat['seqidx'] = self.dat['seqidx'][dt_ind]
        self.dat['pktnum'] = self.dat['pktnum'][dt_ind]
        ##  self.dat['Flag'] = self.dat['Flag'][dt_ind]

        
        return self

