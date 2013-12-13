from __future__ import division

import datetime

import numpy as np
from spacepy import datamodel as dm

import FIREdata
from FIREdata import total_seconds
import packet

MFIB_transfer_time = 10*48 / 115200 * 1e6 # microseconds
# this is 48 bytes, 8 bits per byte, plus a start and stop
#  transferred at 11520 baud, then 1e6 seconds to microseconds

measurement_time = 18.75*1e3 # this is settable but I bet we will not change it.
# this is 18.75ms measurment and then 1e3 to go o microseconds


datalen = 24
majorTimelen = 8
minorTimelen = 2
majorLen = datalen+majorTimelen
minorLen = datalen+minorTimelen

measurement_per_packet = 238 // minorLen
# this is the number of measurments we hav to add if we miss a packet


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
        #dat['Epoch'].attrs['VALIDMIN'] = datetime.datetime(1990,1,1)
        #dat['Epoch'].attrs['VALIDMAX'] = datetime.datetime(2029,12,31,23,59,59,999000)
        dat['Epoch'].attrs['VAR_TYPE'] = 'support_data'
        dat['Epoch'].attrs['TIME_BASE'] = '0 AD'
        dat['Epoch'].attrs['MONOTON'] = 'INCREASE'
        dat['Epoch'].attrs['VAR_NOTES'] = 'Epoch at each hi-res measurement'
        dat['hr0'] = dm.dmarray([], dtype=int)
        dat['hr0'].attrs['CATDESC'] = 'Detector 0 hi-res'
        dat['hr0'].attrs['ELEMENT_LABELS'] = "hr0_0", "hr0_1", "hr0_2", "hr0_3", "hr0_4", "hr0_5",
        dat['hr0'].attrs['ELEMENT_NAMES'] =  "hr0-0", "hr0-1", "hr0-2", "hr0-3", "hr0-4", "hr0-5",
        dat['hr0'].attrs['FILL_VALUE'] = -2**16
        dat['hr0'].attrs['LABEL'] = 'Detector 0 hi-res'
        dat['hr0'].attrs['SCALE_TYPE'] = 'log'
        dat['hr0'].attrs['UNITS'] = 'counts'
        dat['hr0'].attrs['VALID_MIN'] = 0
        dat['hr0'].attrs['VALID_MAX'] = 2**16-1
        dat['hr0'].attrs['VAR_TYPE'] = 'data'
        dat['hr0'].attrs['VAR_NOTES'] = 'hr0 for each channel'
        dat['hr0'].attrs['DEPEND_0'] = 'Epoch'
        dat['hr0'].attrs['DEPEND_1'] = 'Channel'
        dat['hr1'] = dm.dmarray([], dtype=int)
        dat['hr1'].attrs['CATDESC'] = 'Detector 1 hi-res'
        dat['hr1'].attrs['ELEMENT_LABELS'] = "hr1_0", "hr1_1", "hr1_2", "hr1_3", "hr1_4", "hr1_5",
        dat['hr1'].attrs['ELEMENT_NAMES'] =  "hr1-0", "hr1-1", "hr1-2", "hr1-3", "hr1-4", "hr1-5",
        dat['hr1'].attrs['FILL_VALUE'] = -2**16
        dat['hr1'].attrs['LABEL'] = 'Detector 1 hi-res'
        dat['hr1'].attrs['SCALE_TYPE'] = 'log'
        dat['hr1'].attrs['UNITS'] = 'counts'
        dat['hr1'].attrs['VALID_MIN'] = 0
        dat['hr1'].attrs['VALID_MAX'] = 2**16-1
        dat['hr1'].attrs['VAR_TYPE'] = 'data'
        dat['hr1'].attrs['VAR_NOTES'] = 'hr1 for each channel'
        dat['hr1'].attrs['DEPEND_0'] = 'Epoch'
        dat['hr1'].attrs['DEPEND_1'] = 'Channel'
        dat['Channel'] = dm.dmarray(range(6))
        dat['Channel'].attrs['CATDESC'] = 'Channel Number'
        dat['Channel'].attrs['ELEMENT_LABELS'] = "0", "1", "2", "3", "4", "5",
        dat['Channel'].attrs['ELEMENT_NAMES'] =  "0", "1", "2", "3", "4", "5",
        dat['Channel'].attrs['FILL_VALUE'] = -2**16
        dat['Channel'].attrs['LABEL'] = 'Channel'
        dat['Channel'].attrs['SCALE_TYPE'] = 'linear'
        dat['Channel'].attrs['UNITS'] = ''
        dat['Channel'].attrs['VALID_MIN'] = 0
        dat['Channel'].attrs['VALID_MAX'] = 5
        dat['Channel'].attrs['VAR_TYPE'] = 'support_data'
        dat['Channel'].attrs['VAR_NOTES'] = 'channel number'
        return dat

    def major_data(self, inval):
        """
        read in and add major data to the class
        """
        dt = FIREdata.dat2time(FIREdata.hex2int(inval[:8]))
        # correct the time for the known delays
        dt -= datetime.timedelta(microseconds=(MFIB_transfer_time+measurement_time/2))

        # combine th nibbles and convert to an int
        d1 = [int(v2 + v1, 16) for (v1, v2) in zip(inval[majorTimelen::2], inval[majorTimelen+1::2])]

        self.dat['Epoch'] = dm.dmarray.append(self.dat['Epoch'], dt)
        if len(self.dat['hr0']) == 0:
            self.dat['hr0'] = dm.dmarray.hstack(self.dat['hr0'], d1[0:6])
            self.dat['hr1'] = dm.dmarray.hstack(self.dat['hr1'], d1[6:])
        else:
            self.dat['hr0'] = dm.dmarray.vstack(self.dat['hr0'], d1[0:6])
            self.dat['hr1'] = dm.dmarray.vstack(self.dat['hr1'], d1[6:])


    def minor_data(self, inval, meas_ind=0):
        """
        read in and add minor data to the class
        """
        # get the last time
        dt = self.dat['Epoch'][meas_ind-1]
        # we need to replace the milliseconds
        us = 1000*( int(inval[0]+inval[1], 16) )
        if  us < self.dat['Epoch'][-1].microsecond:
            dt += datetime.timedelta(seconds=1)
        if us == 1000000:
            print("found us=1000000")
            dt += datetime.timedelta(seconds=1)
        if us > 1000000:
            print("found us>1000000")
            return
        else:
            dt = dt.replace(microsecond=us)
        # now that e have the time this is just passed back to the caller so some
        #   checking can be done

        # combine th nibbles and convert to an int
        d1 = [int(v2 + v1, 16) for (v1, v2) in zip(inval[minorTimelen::2], inval[minorTimelen+1::2])]
        # set the data at the correct index to the decoded data
        self.dat['hr0'][meas_ind] = d1[0:6]
        self.dat['hr1'][meas_ind] = d1[6:]
        return dt

    def read(self, filename):
        # need to have pages and packet information
        packets = packet.BIRDpackets(filename)

        # If we do not start with a pktnum = 01 skip this page until we find a pktnum
        #  01 because that has the full time stamp
        #  TODO it may be possible to work backwards using the seqidx and seqnum

        meas_ind = 0 # this counts the measurement in a page
        previous_packet = None # holds the last packet
        dataBuffer = [] # this holds the data form a packet as measurmenet may roll onto
                        #   the next packet
        for packet_ in packets:
            """
            loop over all the packets and extract data from them
            - for a new page we have to get packet 01 or toss it
            - from there create the times for each measurement and populate the
               data as we go though the packets
               - there are 162 measurements per page as 18.75 ms
               - need to watch the minor stamps as they occur at 15 or 20ms increments
                  which is the FIRE data cadence but the data transmission rate is 15ms
               - also need to correct the timing for packet transmission time and
                  move it to the middle of the measurement
               - There are 0x13 (19) packets in each page (byte stuffing should not change this)
            """

            """
            options in here:
            1) new page starting with packet 01
            2) new page with missing packet 01
            3) current page with next packet
            4) current page with missing packet
            5) last packet of page at 13
            6) last packet of a page with missing 13
            """
            ### if this a new page? ###
            if previous_packet is not None and (packet_.seqidx != previous_packet.seqidx or \
            packet_.seqnum != previous_packet.seqnum): # means we have moved to a new page
                previous_packet = None

            ### option 2 ###
            if previous_packet is None and packet_.pktnum != '01':
#            elif previous_packet is None and p.pktnum != '01':
                print("Page did not start with packet '01' skipping packet {0}, cannot find time".format(packet_))
                continue # this just skips the packet
            ### option 1 ###
            elif previous_packet is None and packet_.pktnum == '01': # new page starting
                dataBuffer = [] # clear the dataBuffer as we are starting a new page
                previous_packet = packet_ # hang on to the last packet
                print packet_
                # this is a decodable page, start now
                dataBuffer.extend(packet_.data) # grab the data out
                # since p.pktnum == 01 this is a major time stamp, decode it.
                tmp = [dataBuffer.pop(0) for v in range(majorLen)]
                self.major_data(tmp)
                # now we need to replcate the data forward 162 measurements
                #  from the middlwe of one to the middle of the next is 18.75 ms
                dt = [self.dat['Epoch'][-1] +
                      datetime.timedelta(microseconds=measurement_time)*v for v in range(1, 162)]
                # add another 161 measurments on at the correct times
                self.dat['Epoch'] = dm.dmarray.append(self.dat['Epoch'], dt)
                # add on data will fill for the next 161 measurements as well
                arr = np.zeros((161, 6), dtype=int)
                arr.fill(self.dat['hr0'].attrs['FILL_VALUE'])
                self.dat['hr0'] = dm.dmarray.vstack( self.dat['hr0'], arr  )
                self.dat['hr1'] = dm.dmarray.vstack( self.dat['hr1'], arr  )
                # then update meas_ind to the next index to write
                meas_ind += 1
            ### option 3 ###
            elif previous_packet is not None and \
                int(packet_.pktnum, 16) == int(previous_packet.pktnum, 16)+1 and \
                packet_.seqidx == previous_packet.seqidx and \
                packet_.seqnum == previous_packet.seqnum: # next packet in current page
                previous_packet = packet_ # hang on to the last packet
                print packet_
                # this is a decodable page, start now
                dataBuffer.extend(packet_.data) # grab the data out
                # just let the while loop below take case of the data
            ### option 4 ###
            elif previous_packet is not None and \
                int(packet_.pktnum, 16) > int(previous_packet.pktnum, 16)+1 and \
                packet_.seqidx == previous_packet.seqidx and \
                packet_.seqnum == previous_packet.seqnum: # next packet in current page with a missing
                previous_packet = packet_ # hang on to the last packet
                print packet_
                dataBuffer = [] # clear the dataBuffer as we lost data
                # this is a decodable page, start now
                dataBuffer.extend(packet_.data) # grab the data out
                # look though the dataBuffer looking for what seems to be 2 minor stamps
                #   the right length apart
                while len(dataBuffer) > 0:
                    t1 = int(dataBuffer[0]+dataBuffer[1], 16)
                    t2 = int(dataBuffer[0+datalen+2]+dataBuffer[1+datalen+2], 16)
                    if (t2 == t1+15) or (t2 == t1+30) or \
                        (t2 == t1+15-1e6) or (t2 == t1+30-1e6): # this is certainly correct
                        break
                    else:
                        dataBuffer.pop(0)


                meas_ind += ( measurement_per_packet * (int(packet_.pktnum, 16)-int(previous_packet.pktnum, 16)))
                # just let the while loop below take case of the data



            """
            regardless of the packet if there is more data in the buffer we should
            decode it and add it to the arrays
            """
            while len(dataBuffer) >= minorLen:
                # since p.pktnum == 1 this is a major time stamp, decode it.
                tmp = [dataBuffer.pop(0) for v in range(minorLen)]
                dt = self.minor_data(tmp, meas_ind)
                meas_ind += 1
#                if np.abs(total_seconds(dt-self.dat['Epoch'][meas_ind])) > 0.0128:
#                    print("Something wrong with time sync")
#                    raise(ValueError("Time sync error"))

        # go through and remove duplicate times and data
        print("Looking for duplicate measurements")

        arr, dt_ind, return_inverse = np.unique(self.dat['Epoch'], return_index=True, return_inverse=True) # this is unique an sort
        print("Found {0} duplicates of {1}".format(len(return_inverse)-len(dt_ind), len(return_inverse)))

        self.dat['Epoch'] = arr
        self.dat['hr0'] = self.dat['hr0'][dt_ind]
        self.dat['hr1'] = self.dat['hr1'][dt_ind]

        return self




"""
a missing page means 248 / 26 => 9.5 samples missing the ms should be valid
just 15*9=135 ms later so it might often roll over
"""



