import datetime
import itertools

import numpy as np
from spacepy import datamodel as dm

import FIREdata
import packet


datalen = 8
majorTimelen = 8
majorLen = majorTimelen+datalen
minorLen = majorLen


class datatimes(FIREdata.data):
    """
    a datatimes data file
    """
    def __init__(self):
        self.dat = self.getSkel()

    def getSkel(self):
        dat = dm.SpaceData()

        dat['Time'] = dm.dmarray([])
        dat['Time'].attrs['CATDESC'] = 'Start or stop Time'
        dat['Time'].attrs['FIELDNAM'] = 'Time'
        dat['Time'].attrs['LABEL'] = 'Start or stop Time'
        dat['Time'].attrs['SCALE_TYPE'] = 'linear'
        #dat['Time'].attrs['UNITS'] = 'none'
        #        dat['Time'].attrs['VALID_MIN'] = datetime.datetime(1990,1,1)
        #        dat['Time'].attrs['VALID_MAX'] = datetime.datetime(2029,12,31,23,59,59,999000)
        dat['Time'].attrs['VAR_TYPE'] = 'support_data'
        dat['Time'].attrs['VAR_NOTES'] = 'Time data started or stopped'
        dat['Time'].attrs['DEPEND_0'] = 'Epoch'
        dat['Time'].attrs['FILL_VALUE'] = -1

        dat['Epoch'] = dm.dmarray([])
        dat['Epoch'].attrs['CATDESC'] = 'Default Time'
        dat['Epoch'].attrs['FIELDNAM'] = 'Epoch'
        #dat['Epoch'].attrs['FILLVAL'] = datetime.datetime(2100,12,31,23,59,59,999000)
        dat['Epoch'].attrs['LABEL'] = 'Epoch'
        dat['Epoch'].attrs['SCALE_TYPE'] = 'linear'
        #        dat['Epoch'].attrs['VALID_MIN'] = datetime.datetime(1990,1,1)
        #        dat['Epoch'].attrs['VALID_MAX'] = datetime.datetime(2029,12,31,23,59,59,999000)
        dat['Epoch'].attrs['VAR_TYPE'] = 'support_data'
        dat['Epoch'].attrs['TIME_BASE'] = '0 AD'
        dat['Epoch'].attrs['MONOTON'] = 'INCREASE'
        dat['Epoch'].attrs['VAR_NOTES'] = 'Epoch at each configuration point'

        dat['Mode'] = dm.dmarray([], dtype=int)
        dat['Mode'][...] = -1
        dat['Mode'].attrs['FIELDNAM'] = 'Mode'
        dat['Mode'].attrs['FILL_VALUE'] = -1
        dat['Mode'].attrs['LABEL'] = 'FIRE Mode'
        dat['Mode'].attrs['SCALE_TYPE'] = 'linear'
        dat['Mode'].attrs['VALID_MIN'] = 0
        dat['Mode'].attrs['VALID_MAX'] = 1
        dat['Mode'].attrs['VAR_TYPE'] = 'support_data'
        dat['Mode'].attrs['VAR_NOTES'] = 'Is the line FIRE on (=1) or FIRE off (=0)'

        dat['Duration'] = dm.dmarray([], dtype=float)
        dat['Duration'][...] = -1
        dat['Duration'].attrs['FIELDNAM'] = 'Duration'
        dat['Duration'].attrs['FILL_VALUE'] = -1
        dat['Duration'].attrs['LABEL'] = 'FIRE Duration'
        dat['Duration'].attrs['SCALE_TYPE'] = 'linear'
        dat['Duration'].attrs['VALID_MIN'] = 0
        dat['Duration'].attrs['VALID_MAX'] = 100000
        dat['Duration'].attrs['VAR_TYPE'] = 'support_data'
        dat['Duration'].attrs['VAR_NOTES'] = 'Duration of the on or off'
        return dat

    def major_data(self, inval):
        """
        read in and add major data to the class
        """
        inval = FIREdata.hex2int(inval)
        dt = FIREdata.dat2time(inval[0:8])
        d1 = FIREdata.dat2time(inval[ majorTimelen:])
        self.dat['Epoch'] = dm.dmarray.append(self.dat['Epoch'], dt)
        self.dat['Time'] = dm.dmarray.append(self.dat['Time'], d1)

    def read(self, filename):
        # need to have pages and packet information
        packets = packet.BIRDpackets(filename)

        """
        data times is at most one page
        """

        previous_packet = None # holds the last packet
        dataBuffer = [] # this holds the data form a packet as measurement may roll onto
                        #   the next packet
        firstPacket = False
        for packet_ in packets:
            """
            options in here:
            1) new page starting with packet 01
            2) new page with missing packet 01
            3) current page with next packet
            4) current page with missing packet
            5) last packet of page at 13
            6) last packet of a page with missing 13
            """
            if packet_.pktnum == '01':
                firstPacket = True

            ### option 2 ###
            ### option 1 ###
            if previous_packet is None: # new page starting
                dataBuffer = [] # clear the dataBuffer as we are starting a new page
                previous_packet = packet_ # hang on to the last packet
                print packet_
                # this is a decodable page, start now
                dataBuffer.extend(packet_.data) # grab the data out
                # since p.pktnum == 01 this is a major time stamp, decode it.
            else:
                while len(dataBuffer) > 0:
                    if FIREdata.validDate(FIREdata.hex2int(dataBuffer[:majorTimelen])):
                        pass
                    else:
                        dataBuffer.pop(0)
            ### option 3 ###
            ### option 4 ###

            """
            regardless of the packet if there is more data in the buffer we should
            decode it and add it to the arrays
            """
            while len(dataBuffer) >= minorLen:
                tmp = [dataBuffer.pop(0) for v in range(majorLen)]
                self.major_data(tmp)

        # go through and remove duplicate times and data
        print("Looking for duplicate measurements")

        arr, dt_ind, return_inverse = np.unique(self.dat['Epoch'], return_index=True, return_inverse=True) # this is unique an sort
        print("Found {0} duplicates of {1}".format(len(return_inverse)-len(dt_ind), len(return_inverse)))

        self.dat['Epoch'] = arr
        self.dat['Time'] = self.dat['Time'][dt_ind]
        # populate Duration and Mode
        self.dat['Mode'] = dm.dmarray.append(self.dat['Mode'], np.zeros(len(self.dat['Epoch']), dtype=int))
        if firstPacket:
            self.dat['Mode'][::2] = 1
        dur = [FIREdata.total_seconds(v2 - v1) for v1, v2 in itertools.izip(self.dat['Epoch'], self.dat['Time'])]
        self.dat['Duration'] = dm.dmarray.append(self.dat['Duration'], dur)


        return self



