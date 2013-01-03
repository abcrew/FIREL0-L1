#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cal_Spectra.py

Compute calibration spectra from the L1 FIREBIRD files

"""

import datetime
from optparse import OptionParser
import os
import re

# dependency includes (alphabetical)
import dateutil.parser as dup
import numpy as np
import spacepy.datamodel as dm


data = dm.SpaceData()

def isConfig(dat):
    """
    if the file is a congig file return True, else False
    """
    keys = [u'cntrl_reg',
            u'data_type',
            u'det_energy_setpoint',
            u'control_register',
            u'context_selection',
            u'Epoch',
            u'cmd_reg_value',
            u'packet_counter',
            u'hi_res_interval',
            u'mbp_selection',
            u'det_max_energy_setpoint']

    for k in keys:
        if k not in dat:
            return False
    return True

def isHires(dat):
    """
    if the file is a Hires file return True, else False
    """
    if 'hr0' in dat and 'hr1' in dat and 'Epoch' in dat:
        return True
    else:
        return False

def readfiles(files):
    """
    read in the files and store the data we need to data
    """
    global data # glabal means we can edit this
    for f in files:
        try:
            dat = dm.readJSONheadedASCII(f)
        except IOError:
            print('File {0} is not valid JSONheadedascii, skipped'.format(f))
            continue
        if not isHires(dat) and not isConfig(dat):
            print('File {0} is not hires or config, skipped'.format(f))
            continue # not the kind of file we want
        ## file is now for sure wanted store its info to data
        data[f] = dat







if __name__ == '__main__':
    usage = "usage: %prog [options] infile1 [[infile2],[...]]"
    parser = OptionParser(usage=usage)

    parser.add_option("-p", "--plot",
                  action="store_true", dest="plot",
                  help="Also plot the spectra to file", default=False)
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("incorrect number of arguments, have to specify at least one file")

    readfiles(args)





