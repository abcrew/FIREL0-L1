import datetime

import numpy as np
from spacepy import datamodel as dm

import FIREdata
import packet
from page import page

def printConfigPage(inpage):
    """
    print out a hires page for debugging
    """
    # the first one is 8+16 bytes then 16+2
    dat = inpage.split(' ')
    print ' '.join(dat[0:16+8])
    for ii in range(16+8+2, len(dat), 16+2):
        print ' '.join(dat[ii:ii+16+2])

class configPage(FIREdata.dataPage):
    """
    a page of config data
    """
    def __init__(self, inpage):
        self._datalen = 16
        self._majorTimelen = 8
        self._minorTimelen = 2
        dat = inpage.split()
        dat = [int(v, 16) for v in dat]

        self.t0 = FIREdata.dat2time(inpage[0:25])
        # now the data length is 24
        self.major_data(dat[0:self._datalen+ self._majorTimelen])
        start = self._datalen+ self._majorTimelen
        for ii in range(start, len(dat), self._datalen+self._minorTimelen): # the index of the start of each FIRE data
            stop = ii+self._datalen+self._minorTimelen  # 24 bytes of data and 2 for a minor time stamp
            self.minor_data(dat[ii:stop])
        # sort the data
        self = sorted(self, key = lambda x: x[0])

    def minor_data(self, inval):
        """
        read in and add minor data to the class
        """
        if len(inval) < self._datalen+self._minorTimelen+2:
            return
        if (np.asarray(inval) == 0).all(): # is this line fill?
            return
        dt = self[-1][0] # this is the last time
        second = inval[1]
        minute = inval[0]
        if minute < self[-1][0].minute:
            dt += datetime.timedelta(hours=1)
        dt = dt.replace(minute=minute)
        dt = dt.replace(second=second)
        d1 = np.asarray(inval[self._minorTimelen:]) # 2 bytes of checksum
        self.append([dt, d1])

    def major_data(self, inval):
        """
        read in and add major data to the class
        """
        if (np.asarray(inval) == 0).all(): # is this line fill?
            return
        dt = FIREdata.dat2time(inval[0:8])
        d1 = np.asarray(inval[ self._majorTimelen:])
        self.append([dt, d1])



class config(FIREdata.data):
    """
    a config data file
    """
    def __init__(self, inlst):
        dt = zip(*inlst)[0]
        data = np.hstack(zip(*inlst)[1]).reshape((-1, 16))
        dat = dm.SpaceData()

        dat['reg00'] = dm.dmarray(data[:,0])
        dat['reg00'].attrs['CATDESC'] = 'Control Register'
        dat['reg00'].attrs['FIELDNAM'] = 'reg{0:02}'.format(0)
        dat['reg00'].attrs['LABLAXIS'] = 'Control Register'
        dat['reg00'].attrs['SCALETYP'] = 'linear'
        #dat['reg00'].attrs['UNITS'] = 'none'
        dat['reg00'].attrs['VALIDMIN'] = 0
        dat['reg00'].attrs['VALIDMAX'] = 2**8-1
        dat['reg00'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg00'].attrs['VAR_NOTES'] = 'Bits: 7-0: 0, 0, uB data on, context on, det2 hi on, det1 hi on, HVPS on, pulser on'
        dat['reg00'].attrs['DEPEND_0'] = 'Epoch'

        dat['reg01'] = dm.dmarray(data[:,1])
        dat['reg01'].attrs['CATDESC'] = 'Hi-Res Interval'
        dat['reg01'].attrs['FIELDNAM'] = 'reg{0:02}'.format(1)
        dat['reg01'].attrs['LABLAXIS'] = 'Hi-Res Interval'
        dat['reg01'].attrs['SCALETYP'] = 'linear'
        #dat['reg01'].attrs['UNITS'] = 'none'
        dat['reg01'].attrs['VALIDMIN'] = 0
        dat['reg01'].attrs['VALIDMAX'] = 2**8-1
        dat['reg01'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg01'].attrs['VAR_NOTES'] = 'Hi-Res Interval'
        dat['reg01'].attrs['DEPEND_0'] = 'Epoch'

        dat['reg02'] = dm.dmarray(data[:,2])
        dat['reg02'].attrs['CATDESC'] = 'Context Bin Selection'
        dat['reg02'].attrs['FIELDNAM'] = 'reg{0:02}'.format(2)
        dat['reg02'].attrs['LABLAXIS'] = 'Context Bin Selection'
        dat['reg02'].attrs['SCALETYP'] = 'linear'
        #dat['reg02'].attrs['UNITS'] = 'none'
        dat['reg02'].attrs['VALIDMIN'] = 0
        dat['reg02'].attrs['VALIDMAX'] = 2**8-1
        dat['reg02'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg02'].attrs['VAR_NOTES'] = 'Context Bin Selection'
        dat['reg02'].attrs['DEPEND_0'] = 'Epoch'

        dat['reg03'] = dm.dmarray(data[:,3])
        dat['reg03'].attrs['CATDESC'] = 'uBurst Bin Selection'
        dat['reg03'].attrs['FIELDNAM'] = 'reg{0:02}'.format(3)
        dat['reg03'].attrs['LABLAXIS'] = 'uBurst Bin Selection'
        dat['reg03'].attrs['SCALETYP'] = 'linear'
        #dat['reg03'].attrs['UNITS'] = 'none'
        dat['reg03'].attrs['VALIDMIN'] = 0
        dat['reg03'].attrs['VALIDMAX'] = 2**8-1
        dat['reg03'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg03'].attrs['VAR_NOTES'] = 'uBurst Bin Selection'
        dat['reg03'].attrs['DEPEND_0'] = 'Epoch'

        dat['reg04'] = dm.dmarray(data[:,4])
        dat['reg04'].attrs['CATDESC'] = 'Detector Max Energy Setpoint'
        dat['reg04'].attrs['FIELDNAM'] = 'reg{0:02}'.format(4)
        dat['reg04'].attrs['LABLAXIS'] = 'Detector Max Energy Setpoint'
        dat['reg04'].attrs['SCALETYP'] = 'linear'
        #dat['reg04'].attrs['UNITS'] = 'none'
        dat['reg04'].attrs['VALIDMIN'] = 0
        dat['reg04'].attrs['VALIDMAX'] = 2**8-1
        dat['reg04'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg04'].attrs['VAR_NOTES'] = 'Detector Max Energy Setpoint'
        dat['reg04'].attrs['DEPEND_0'] = 'Epoch'

        dat['reg05'] = dm.dmarray(data[:,5])
        dat['reg05'].attrs['CATDESC'] = 'Detector Energy Setpoint5'
        dat['reg05'].attrs['FIELDNAM'] = 'reg{0:02}'.format(5)
        dat['reg05'].attrs['LABLAXIS'] = 'Detector Energy Setpoint5'
        dat['reg05'].attrs['SCALETYP'] = 'linear'
        #dat['reg05'].attrs['UNITS'] = 'none'
        dat['reg05'].attrs['VALIDMIN'] = 0
        dat['reg05'].attrs['VALIDMAX'] = 2**8-1
        dat['reg05'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg05'].attrs['VAR_NOTES'] = 'Detector Energy Setpoint5'
        dat['reg05'].attrs['DEPEND_0'] = 'Epoch'

        dat['reg06'] = dm.dmarray(data[:,6])
        dat['reg06'].attrs['CATDESC'] = 'Detector Energy Setpoint4'
        dat['reg06'].attrs['FIELDNAM'] = 'reg{0:02}'.format(6)
        dat['reg06'].attrs['LABLAXIS'] = 'Detector Energy Setpoint4'
        dat['reg06'].attrs['SCALETYP'] = 'linear'
        #dat['reg06'].attrs['UNITS'] = 'none'
        dat['reg06'].attrs['VALIDMIN'] = 0
        dat['reg06'].attrs['VALIDMAX'] = 2**8-1
        dat['reg06'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg06'].attrs['VAR_NOTES'] = 'Detector Energy Setpoint4'
        dat['reg06'].attrs['DEPEND_0'] = 'Epoch'

        dat['reg07'] = dm.dmarray(data[:,7])
        dat['reg07'].attrs['CATDESC'] = 'Detector Energy Setpoint3'
        dat['reg07'].attrs['FIELDNAM'] = 'reg{0:02}'.format(7)
        dat['reg07'].attrs['LABLAXIS'] = 'Detector Energy Setpoint3'
        dat['reg07'].attrs['SCALETYP'] = 'linear'
        #dat['reg07'].attrs['UNITS'] = 'none'
        dat['reg07'].attrs['VALIDMIN'] = 0
        dat['reg07'].attrs['VALIDMAX'] = 2**8-1
        dat['reg07'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg07'].attrs['VAR_NOTES'] = 'Detector Energy Setpoint3'
        dat['reg07'].attrs['DEPEND_0'] = 'Epoch'

        dat['reg08'] = dm.dmarray(data[:,8])
        dat['reg08'].attrs['CATDESC'] = 'Detector Energy Setpoint2'
        dat['reg08'].attrs['FIELDNAM'] = 'reg{0:02}'.format(8)
        dat['reg08'].attrs['LABLAXIS'] = 'Detector Energy Setpoint2'
        dat['reg08'].attrs['SCALETYP'] = 'linear'
        #dat['reg08'].attrs['UNITS'] = 'none'
        dat['reg08'].attrs['VALIDMIN'] = 0
        dat['reg08'].attrs['VALIDMAX'] = 2**8-1
        dat['reg08'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg08'].attrs['VAR_NOTES'] = 'Detector Energy Setpoint2'
        dat['reg08'].attrs['DEPEND_0'] = 'Epoch'

        dat['reg09'] = dm.dmarray(data[:,9])
        dat['reg09'].attrs['CATDESC'] = 'Detector Energy Setpoint1'
        dat['reg09'].attrs['FIELDNAM'] = 'reg{0:02}'.format(9)
        dat['reg09'].attrs['LABLAXIS'] = 'Detector Energy Setpoint1'
        dat['reg09'].attrs['SCALETYP'] = 'linear'
        #dat['reg09'].attrs['UNITS'] = 'none'
        dat['reg09'].attrs['VALIDMIN'] = 0
        dat['reg09'].attrs['VALIDMAX'] = 2**8-1
        dat['reg09'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg09'].attrs['VAR_NOTES'] = 'Detector Energy Setpoint1'
        dat['reg09'].attrs['DEPEND_0'] = 'Epoch'

        dat['reg10'] = dm.dmarray(data[:,10])
        dat['reg10'].attrs['CATDESC'] = 'Detector Energy Setpoint0'
        dat['reg10'].attrs['FIELDNAM'] = 'reg{0:02}'.format(10)
        dat['reg10'].attrs['LABLAXIS'] = 'Detector Energy Setpoint0'
        dat['reg10'].attrs['SCALETYP'] = 'linear'
        #dat['reg10'].attrs['UNITS'] = 'none'
        dat['reg10'].attrs['VALIDMIN'] = 0
        dat['reg10'].attrs['VALIDMAX'] = 2**8-1
        dat['reg10'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg10'].attrs['VAR_NOTES'] = 'Detector Energy Setpoint0'
        dat['reg10'].attrs['DEPEND_0'] = 'Epoch'

        dat['reg11'] = dm.dmarray(data[:,11])
        dat['reg11'].attrs['CATDESC'] = 'Config parameter {0}'.format(11)
        dat['reg11'].attrs['FIELDNAM'] = 'reg{0:02}'.format(11)
        dat['reg11'].attrs['LABLAXIS'] = 'Register {0:02} value'.format(11)
        dat['reg11'].attrs['SCALETYP'] = 'linear'
        #dat['reg11'].attrs['UNITS'] = 'none'
        dat['reg11'].attrs['VALIDMIN'] = 0
        dat['reg11'].attrs['VALIDMAX'] = 2**8-1
        dat['reg11'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg11'].attrs['VAR_NOTES'] = 'register{0:02} data'.format(11)
        dat['reg11'].attrs['DEPEND_0'] = 'Epoch'

        dat['reg12'] = dm.dmarray(data[:,12])
        dat['reg12'].attrs['CATDESC'] = 'Config parameter {0}'.format(12)
        dat['reg12'].attrs['FIELDNAM'] = 'reg{0:02}'.format(12)
        dat['reg12'].attrs['LABLAXIS'] = 'Register {0:02} value'.format(12)
        dat['reg12'].attrs['SCALETYP'] = 'linear'
        #dat['reg12'].attrs['UNITS'] = 'none'
        dat['reg12'].attrs['VALIDMIN'] = 0
        dat['reg12'].attrs['VALIDMAX'] = 2**8-1
        dat['reg12'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg12'].attrs['VAR_NOTES'] = 'register{0:02} data'.format(12)
        dat['reg12'].attrs['DEPEND_0'] = 'Epoch'

        dat['reg13'] = dm.dmarray(data[:,13])
        dat['reg13'].attrs['CATDESC'] = 'Config parameter {0}'.format(13)
        dat['reg13'].attrs['FIELDNAM'] = 'reg{0:02}'.format(13)
        dat['reg13'].attrs['LABLAXIS'] = 'Register {0:02} value'.format(13)
        dat['reg13'].attrs['SCALETYP'] = 'linear'
        #dat['reg13'].attrs['UNITS'] = 'none'
        dat['reg13'].attrs['VALIDMIN'] = 0
        dat['reg13'].attrs['VALIDMAX'] = 2**8-1
        dat['reg13'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg13'].attrs['VAR_NOTES'] = 'register{0:02} data'.format(13)
        dat['reg13'].attrs['DEPEND_0'] = 'Epoch'

        dat['reg14'] = dm.dmarray(data[:,14])
        dat['reg14'].attrs['CATDESC'] = 'Config parameter {0}'.format(14)
        dat['reg14'].attrs['FIELDNAM'] = 'reg{0:02}'.format(14)
        dat['reg14'].attrs['LABLAXIS'] = 'Register {0:02} value'.format(14)
        dat['reg14'].attrs['SCALETYP'] = 'linear'
        #dat['reg14'].attrs['UNITS'] = 'none'
        dat['reg14'].attrs['VALIDMIN'] = 0
        dat['reg14'].attrs['VALIDMAX'] = 2**8-1
        dat['reg14'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg14'].attrs['VAR_NOTES'] = 'register{0:02} data'.format(14)
        dat['reg14'].attrs['DEPEND_0'] = 'Epoch'

        dat['reg15'] = dm.dmarray(data[:,15])
        dat['reg15'].attrs['CATDESC'] = 'Config parameter {0}'.format(15)
        dat['reg15'].attrs['FIELDNAM'] = 'reg{0:02}'.format(15)
        dat['reg15'].attrs['LABLAXIS'] = 'Register {0:02} value'.format(15)
        dat['reg15'].attrs['SCALETYP'] = 'linear'
        #dat['reg15'].attrs['UNITS'] = 'none'
        dat['reg15'].attrs['VALIDMIN'] = 0
        dat['reg15'].attrs['VALIDMAX'] = 2**8-1
        dat['reg15'].attrs['VAR_TYPE'] = 'support_data'
        dat['reg15'].attrs['VAR_NOTES'] = 'register{0:02} data'.format(15)
        dat['reg15'].attrs['DEPEND_0'] = 'Epoch'

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
        b = packet.BIRDpackets(filename)
        print('    Read {0} packets'.format(len(b)))
        pages = page.fromPackets(b)
        print('    Read {0} pages'.format(len(pages)))
        h = []
        for p in pages:
            h.extend(configPage(p))
        # sort the data
        h = sorted(h, key = lambda x: x[0])
        return config(h)

