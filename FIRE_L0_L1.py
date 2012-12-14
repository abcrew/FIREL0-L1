# -*- coding: utf-8 -*-
"""
FIRE_L0_L1.py

Convertor form the FIRE L0 packets to L1 data

"""
# standard library includes (alphabetical)
import datetime
# dependency includes (alphabetical)
import dateutil.parser as dup
import numpy as np
import spacepy.datamodel as dm




def readL0(datafile):
    """
    read in the data file and return a list of the line sin the file
    """
    df = open(datafile, 'r')
    #ski9p the header
    header = df.readline().strip()
    raw_data = df.readlines()
    data = dm.SpaceData() # dictionary to hold the data
    data.attrs['ReadDatetime'] = datetime.datetime.utcnow() #TODO think in UTC or local?  I like UTC
    data.attrs['DataDatetime'] = dup.parse(header)
    #TODO there will be MSU timestanps and all on the lines from BIRD, those need to be looked at
    data['raw'] = [v.strip() for v in raw_data]
    return data


def parseL0(indata):
    """
    take in a SpaceData of raw L0 and parse it
    return a SpaceData with the new info added
    """
    data_type = list()
    pkt_cntr = list()
    cmd_reg_val = list()
    cntrl_reg = list()
    d1hr = list()
    d2hr = list()
    hr0 = list()
    hr1 = list()
    hr2 = list()
    hr3 = list()
    hr4 = list()
    hr5 = list()
    

    for dat in indata['raw']:
        if(len(dat) == 96):
            data_type.append(int(dat[0:2],16))
            pkt_cntr.append(int(dat[2:4],16))
            cmd_reg_val.append(int(dat[4:6],16))
            cntrl_reg.append(int(dat[6:8],16))
            hr = list()
            for chan in range(6):
                hr.append(int(dat[24+chan*2:26+chan*2],16))
            d1hr.append(hr)
            hr = list()        
            for chan in range(6):
                hr.append(int(dat[36+chan*2:38+chan*2],16))
            d2hr.append(hr)
    
    nlines = len(data_type)

    d = list()

    for j in range(int(nlines/16)):
        data_str = dict(pkt_cntr=pkt_cntr[j*16+0:j*16+16], cmd_vals=cmd_reg_val[j*16+0:j*16+16],
                        d1hr=d1hr[j*16+0:j*16+16], d2hr=d2hr[j*16+0:j*16+16])
        d.append(data_str)
    

if __name__ == '__main__':
    datafile = 'tests/data/fire_data_121119_preship.rtf'
    d1 = readL0(datafile)
    d2 = parseL0(d1)




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

    
