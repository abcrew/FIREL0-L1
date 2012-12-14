# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
/Users/abcrew/.spyder2/.temp.py
"""

datafile = '/Users/abcrew/Desktop/FB_data/FIRE_CAL/fire_data_121119_preship.rtf'

df = open(datafile, 'r')
header = df.readline()
raw_data = df.readlines()

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


for i in raw_data:
    if(len(i) > 96):
        data_type.append(int(i[0:2],16))
        pkt_cntr.append(int(i[2:4],16))
        cmd_reg_val.append(int(i[4:6],16))
        cntrl_reg.append(int(i[6:8],16))
        hr = list()
        for k in range(6):
            hr.append(int(i[24+k*2:26+k*2],16))
        d1hr.append(hr)
        hr = list()        
        for k in range(6):
            hr.append(int(i[36+k*2:38+k*2],16))
        d2hr.append(hr)
    
    
    
nlines = len(data_type)

d = list()


for j in range(int(nlines/16)):
    data_str = dict(pkt_cntr=pkt_cntr[j*16+0:j*16+16], cmd_vals=cmd_reg_val[j*16+0:j*16+16],
                    d1hr=d1hr[j*16+0:j*16+16], d2hr=d2hr[j*16+0:j*16+16])
    d.append(data_str)
    
    
    
    

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

    