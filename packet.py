
import datetime
import time

import numpy as np

from CCITT_CRC16 import CRCfromString

class BIRDpacket(object):
    def __init__(self, strin):
        """
        given a line in a string input it as a packet
        """
        # replace this from the path or filename when it makes sense
        dt = datetime.date.today()
        hour, minute, second, millisecond = strin.split(' - ')[0].split(':')
        self.grt = datetime.datetime(dt.year, dt.month, dt.day, int(hour),
                               int(minute), int(second), int(millisecond)*100)
        self.raw = strin.split(' - ')[1]
        self.srcid = self.raw.split(' ')[1:3]
        self.destid = self.raw.split(' ')[3:5]
        self.cmd_tlm = self.raw.split(' ')[5]
        self.funid = self.raw.split(' ')[6]
        self.seqnum =  self.raw.split(' ')[7]
        self.seqidx =  self.raw.split(' ')[8]
        self.pktnum =  self.raw.split(' ')[9]
        self.datalen = self.raw.split(' ')[10]
        self.data = self.raw.split(' ')[11:11+int(self.datalen,16)]
        self.crc = self.raw.split(' ')[11+int(self.datalen, 16):11+int(self.datalen, 16)+2]
        self.valid_crc = self._crc_valid()

    def _crc_valid(self):
        """
        if the calcuated CRC matches what is in the packet True, False otherwise
        """
        calc_crc = CRCfromString(' '.join(self.raw.split(' ')[1:-3])).upper()
        if calc_crc[2:4].upper() == self.crc[0].upper() and \
           calc_crc[4:6].upper() == self.crc[1].upper():
            return True
        else:
            return False

    def __str__(self):
        return('BIRDpacket: GRT: {0} Len:{1}'.format(self.grt.isoformat(), int(self.datalen, 16)))

    __repr__ = __str__

        
class BIRDpackets(list):
    """
    make a list of all the BIRDpacket instances in a file
    """
    def __init__(self, infile):
        """
        given a filename parse into many BIRDpacket instances
        """
        super(BIRDpackets, self).__init__()
        with open(infile, 'r') as fp:
            dat = fp.readlines()
        dat = [v.strip() for v in dat]
        self.extend([BIRDpacket(v) for v in dat])

    def __str__(self):
        return("{0} packets: {1} bad CRC".format(len(self), np.sum([v.valid_crc for v in self if not v.valid_crc])))

    __repr__ = __str__
