# -*- coding: utf-8 -*-
"""
FIRE_L0_L1.py

Convertor form the FIRE L0 packets to L1 data

"""

# standard library includes (alphabetical)
from abc import ABCMeta, abstractmethod
import datetime
# dependency includes (alphabetical)
import dateutil.parser as dup
import numpy as np
import spacepy.datamodel as dm


class L0(dm.SpaceData):
    """
    base class to hold L0 data
    """
    __metaclass__ = ABCMeta

    def __init__(self, filename, outfilename):
        """
        given a filename read in the data
        """
        self.outfilename = outfilename
        self.filename = filename
        self._readL0()
        self.writeFile(self.outfilename)

    def readL0(self, **kwargs):
        """
        read in the data file and return a list of the line sin the file
        """
        if 'delimiter' not in kwargs:
            kwargs['delimiter'] = ' '
        if 'skiprows' not in kwargs:
            kwargs['skiprows'] = 0
        df = open(self.filename, 'r')
        #skip the header
        for v in range(kwargs['skiprows']):
            header = df.readline().strip()
        raw_data = df.readlines()
        #TODO there will be MSU timestanps and all on the lines from BIRD, those need to be looked at
        raw_data = [v.strip() for v in raw_data]
        raw_data = dm.dmarray([v.split(kwargs['delimiter']) for v in raw_data])
        # the epochs are the first column
        epoch = [dup.parse(v) for v in raw_data[:,0]]
        self['Epoch'] = epoch
        # raw data is the rest
        self['raw_data'] = raw_data[:,1:]

    @abstractmethod
    def parseData(self):
        """
        Parse self['Epoch'] and self['raw_data'] into meaning quantities
        """
        pass

    def writeFile(self):
        """
        write out the data to a json headed ASCII file
        """
        # don't write ou the raw data
        del self['raw_data']
        dm.toJSONheadedASCII(self.outfilename, self, depend0='Epoch', order=['Epoch'])


class ConfigFile(L0):
    """
    class for a configuration file
    """
    def parseData(self):
        """
        Parse self['Epoch'] and self['raw_data'] into meaning quantities
        """
        self['data_type'] = self['raw_data'][:,0]
        self['packet_counter'] = self['raw_data'][:,1]
        self['cmd_reg_value'] = self['raw_data'][:,2]
        self['cntrl_reg'] = self['raw_data'][:,3]
        self['hi_res_interval'] = self['raw_data'][:,4]
        self['context selection'] = self['raw_data'][:,5]
        self['mbp_selection'] = self['raw_data'][:,6]


class MBPFile(L0):
    """
    class for microburst parameter data
    """
    def parseData(self):
        """
        Parse self['Epoch'] and self['raw_data'] into meaning quantities
        """
        self['MB0_100'] = self['raw_data'][:,0:2]
        self['MB0_500'] = self['raw_data'][:,2:5]
        self['MB1_100'] = self['raw_data'][:,5:7]
        self['MB1_500'] = self['raw_data'][:,7:10]


class ContextFile(L0):
    """
    class for context data
    """
    def parseData(self):
        """
        Parse self['Epoch'] and self['raw_data'] into meaning quantities
        """
        self['context'] = self['raw_data'][...]


class HiResFile(L0):
    """
    class for hi-res data data
    """
    def parseData(self):
        """
        Parse self['Epoch'] and self['raw_data'] into meaning quantities
        """
        self['hr'] = self['raw_data'][...]



"""
FIRE ICD definitions by byte:
    0: Data type
    1: Packet Counter
    2: Cmd Reg val
    3: Cntrl Reg
    4: Hi-res Interval
    5: Context Selection
    6: MBP Selection
    7: 0
    8-9: MB0 (100ms)
    10-12: MBO (500ms)
    13-14: MB1 (100ms)
    15-17: MB1 (500ms)
    18-20: C0
    21-23: C1
    24-25: HR0
    26-27: HR1
    28-29: HR2
    30-31: HR3
    32-33: HR4
    34-35: HR5
    36-37: HR6
    38-39: HR7
    40-41: HR8
    42-43: HR9
    44-45: HR10
    46-47: HR11
"""




