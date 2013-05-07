#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

This code makes quick summary plots for use after FIRE CPT
* this code is pretty dumb so be patient in case of issues

To use:
    1) process the L0 files to L1
       -- e.g. ./FIRE_L0_L1.py test_data/20130506-FB1/2013-05-06-Context.txt
    2) Run this code passing in the names of the processed L1 files
       -- e.g. ./quickPlots_CPT.py 2013-05-06-*_L1.txt
    3) Plots are created and saved, look at them


"""

import datetime
import os

import dateutil.parser as dup
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from optparse import OptionParser
from spacepy import datamodel as dm

from FIREutils import determineFileType


if __name__ == '__main__':
    usage = "usage: %prog [options] infile [outfile]"
    parser = OptionParser(usage=usage)

    parser.add_option("-f", "--force",
                  action="store_true", dest="force",
                  help="Force an overwrite, default=False", default=False)
    parser.add_option("", "--hdf5",
                  action="store_true", dest="hdf5",
                  help="Store data in HDF5 format not txt, default=False", default=False)
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("incorrect number of arguments")

#==============================================================================
# check on the inputs
#==============================================================================
    infiles = args
    for f in infiles:
        if not os.path.isfile(f):
            parser.error("File {0} does not exist".format(f))


#==============================================================================
# deal with the filetype options
#==============================================================================

    for f in infiles:
        try:
            tp = determineFileType(f)
        except (ValueError, NotImplementedError):
            # could not determine the type, die
            parser.error("Could not determine the file type: {0}".format(f))

        dat = dm.readJSONheadedASCII(f)
        dat['Epoch'][...] = [dup.parse(v) for v in dat['Epoch'][...]]

        fig = plt.figure()
        ax = fig.add_subplot(111)
        imname = f + '_ql_{0}.png'.format(datetime.datetime.now()).replace(' ', 'T')

        if tp == 'configfile':
            for var in range(16):
                ax.plot(dat['Epoch'], dat['reg{0:02}'.format(var)], label='reg{0:02}'.format(var))
            ax.set_ylim((-10, 300))
            ax.set_xlim((ax.get_xlim()[0], ax.get_xlim()[1]+(ax.get_xlim()[1]-ax.get_xlim()[0])*0.45))
            ax.legend(loc='upper right')
            fig.savefig(imname)
            plt.close()
        elif tp == 'mbpfile':
            ax.plot(dat['Epoch'], dat['Burst'][:,0], label='Burst 0')
            ax.plot(dat['Epoch'], dat['Burst'][:,1], label='Burst 1')
            ax.set_ylim((-2, 20))
            ax.legend(loc='upper left')
            fig.savefig(imname)
            plt.close()
        elif tp == 'contextfile':
            ax.plot(dat['Epoch'], dat['Context'][:,0], label='Context 0')
            ax.plot(dat['Epoch'], dat['Context'][:,1], label='Context 1')
            ax.set_ylim((0, 1000))
            ax.legend(loc='upper left')
            fig.savefig(imname)
            plt.close()
        elif tp == 'hiresfile':
            for v in range(6):
                ind00 = dat['hr0'][:,v] > 0
                ind01 = dat['hr0'][:,v] < 100
                ind0 = np.bitwise_and(ind00, ind01)
                ind10 = dat['hr1'][:,v] > 0
                ind11 = dat['hr1'][:,v] < 100
                ind1 = np.bitwise_and(ind10, ind11)

                ax.plot(dat['Epoch'][ind0], dat['hr0'][ind0, v], label='HR0-{0}'.format(v))
                ax.plot(dat['Epoch'][ind0], dat['hr1'][ind1, v], label='HR1-{0}'.format(v))
            ax.set_ylim((0, 11))
            ax.legend(loc='upper left')
            fig.savefig(imname)
            plt.close()
        elif tp == 'datatimes':
            pass

        print('Wrote: {0}'.format(imname))





