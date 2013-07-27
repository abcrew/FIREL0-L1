#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cal_Spectra.py

Compute calibration spectra from the L1 FIREBIRD files

"""

import bisect
import datetime
import itertools
import getpass
from optparse import OptionParser
import os

# dependency includes (alphabetical)
import numpy as np
import spacepy.datamodel as dm

config = dm.SpaceData()
hires  = dm.SpaceData()

data = dm.SpaceData()
output = dm.SpaceData()
output['Channel'] = dm.dmarray(np.arange(257))
output['Channel'].attrs['LABEL'] = 'Channel'

output['Detector0'] = dm.dmarray(np.zeros(257))
output['Detector1'] = dm.dmarray(np.zeros(257))
output['Detector0'].attrs['DEPEND_0'] = 'Channel'
output['Detector0'].attrs['Units'] = 'Counts'
output['Detector0'].attrs['SCALE_TYPE'] = 'log'
output['Detector0'].attrs['VALID_MIN'] = 0
output['Detector0'].attrs['VALID_MAX'] = 2**16
output['Detector0'].attrs['LABEL'] = 'Total Counts'
output['Detector0'].attrs['TITLE'] = 'FIREBIRD Spectra'
output['Detector0'].attrs['ELEMENT_LABELS'] = ['Detector 0']

for k in output['Detector0'].attrs:
    output['Detector1'].attrs[k] = output['Detector0'].attrs[k]
output['Detector1'].attrs['ELEMENT_LABELS'] = ['Detector 1']

output.attrs['Creation_Date'] = datetime.date.today().isoformat()
output.attrs['Created_By'] = getpass.getuser()
output.attrs['Input_Files'] = []


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
    files = set(files) # make this a unique set of files so that the same is not read twice
    for f in files:
        try:
            dat = dm.readJSONheadedASCII(f)
        except (IOError, ValueError):
            print('File {0} is not valid JSONheadedascii, skipped'.format(f))
            continue
        if not isHires(dat) and not isConfig(dat):
            print('File {0} is not hires or config, skipped'.format(f))
            continue # not the kind of file we want
        ## file is now for sure wanted store its info to data
        data[f] = dat

def parseData():
    """
    parse the contents of data and collect what we need
    """
    global config, hires
    for key in data:
        if isHires(data[key]):
            print('Using hires File: {0}'.format(os.path.abspath(key)))
            output.attrs['Input_Files'].append(os.path.abspath(key))
#            if not hires: # empty SpaceData
#                hires = data[key]
#            else:
            for k in data[key]:
                try:
                    hires[k] = dm.dmarray(np.append(hires[k], data[key][k]))
                except KeyError:
                    hires[k] = data[key][k]
            srt = np.argsort(hires['Epoch'])
            for k in hires:
                hires[k] = hires[k][srt]
        elif isConfig(data[key]):
            print('Using config File: {0}'.format(os.path.abspath(key)))
            output.attrs['Input_Files'].append(os.path.abspath(key))
#            if not config: # empty SpaceData
#                config = data[key]
#            else:
            for k in data[key]:
                try:
                    config[k] = dm.dmarray(np.append(config[k], data[key][k]))
                except KeyError:
                    config[k] = data[key][k]
            srt = np.argsort(config['Epoch'])
            for k in config:
                config[k] = config[k][srt]
        else:
            raise(RuntimeError('Should not have gotten here, error'))

def fillOutput():
    """
    fill the output data file
    """
    #==============================================================================
    #     config file
    #==============================================================================
    # go through and find the first set of settings
    ind = np.where(config['det_energy_setpoint'] >= 0)
    ## ind[0] is sorted!!
    # we assume they all change together (not int he middle of wrting them out)
    times = []
    values = np.zeros([len(ind[0]), 6])
    values[...] = -999
    for ii, (x, y) in enumerate(itertools.izip(ind[0], ind[1])):
        times.append(config['Epoch'][x])
        values[ii,ind[1][ii]] = config['det_energy_setpoint'][x,y]

    ## go through the valus again and it if is -999 go back to a number, if that
    ##    fails go forward and replae with that
    # TODO this throws away data until the first full config set
    for ind, val in np.ndenumerate(values):
        if val != -999:
            continue
        tmp = values[:ind[0], ind[1]]
        for v2 in tmp[::-1]:
            if v2 != -999:
                values[ind] = v2
                break
    #==============================================================================
    #     hires file
    #==============================================================================
    where_ind = np.where(hires['hr0'] > 0)

    for ind in itertools.izip(where_ind[0], where_ind[1]):
        # ind[0] is the time step
        # ind[1] is the channel that was triggered
        tm = bisect.bisect_right(times, hires['Epoch'][ind[0]])
        chan = ind[1]
        if values[tm, chan] == -999:
            continue

        output['Detector0'][values[tm, chan]] += hires['hr0'][ind]

    where_ind = np.where(hires['hr1'] > 0)

    for ind in itertools.izip(where_ind[0], where_ind[1]):
        # ind[0] is the time step
        # ind[1] is the channel that was triggered
        tm = bisect.bisect_right(times, hires['Epoch'][ind[0]])
        chan = ind[1]
        if values[tm, chan] == -999:
            continue

        output['Detector1'][values[tm, chan]] += hires['hr1'][ind]

def writeOutput():
    """
    write out the data to a file, always make a new filename
    """
    for ii in range(100000):
        filename = 'FB_Spectra_{0:05}.txt'.format(ii)
        if not os.path.isfile(filename):
            break
    if ii == 100000-1:
        raise(RuntimeError('Wow how many times has this been run int his directory?'))
    dm.toJSONheadedASCII(filename, output, order=['Channel', 'Detector0', 'Detector1'])
    print('*** Wrote {0} ***'.format(filename))
    return filename

def plot(filename):
    """
    plot the spectra with the same filename
    """
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(11, 8.5))
    ax = fig.add_subplot(111)
    ax.semilogy(output['Channel'], output['Detector0'], 'g.', lw=2)
    ax.semilogy(output['Channel'], output['Detector0'], 'g', lw=2, label=output['Detector0'].attrs['ELEMENT_LABELS'][0])
    ax.semilogy(output['Channel'], output['Detector1'], 'b.', lw=2)
    ax.semilogy(output['Channel'], output['Detector1'], 'b', lw=2, label=output['Detector1'].attrs['ELEMENT_LABELS'][0])
    ax.legend(fancybox=True, shadow=True, loc='upper left')
    ax.set_axisbelow(True)
    ax.yaxis.grid(color='gray', linestyle='dashed')
    ax.xaxis.grid(color='gray', linestyle='dashed')
    ax.set_xlim([0, 256])
    ax.set_xticks(range(0, 256+1, 16))
    ax.set_xlabel(output['Channel'].attrs['LABEL'])
    ax.set_ylabel(output['Detector0'].attrs['LABEL'])
    ax.set_title(output['Detector0'].attrs['TITLE'] + '\n' +
                hires['Epoch'][0] + ' -- ' + hires['Epoch'][-1])

    ax.text(255, ax.get_ylim()[1], '\n'.join(data.keys()), rotation=-90,
            horizontalalignment='right', verticalalignment='top',
            size='small')

    fname = os.path.splitext(filename)[0] + os.extsep + 'png'
    fig.savefig(fname)
    fname = os.path.splitext(filename)[0] + os.extsep + 'pdf'
    fig.savefig(fname)
    print('*** Wrote {0}/{1} ***'.format(fname, '.png'))


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
    parseData()
    fillOutput()
    filename = writeOutput()

    if options.plot:
        plot(filename)



