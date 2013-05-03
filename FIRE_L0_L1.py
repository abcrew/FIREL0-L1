#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FIRE_L0_L1.py

Converter form the FIRE L0 packets to L1 data

"""

# standard library includes (alphabetical)
from abc import ABCMeta, abstractmethod
import datetime
from optparse import OptionParser
import os
import re

# dependency includes (alphabetical)
import dateutil.parser as dup
import numpy as np
import spacepy.datamodel as dm

from FIREdata import burst
from FIREdata import config
from FIREdata import hires
from FIREdata import datatimes



def determineFileType(filename):
    """
    given a filename figure out what type of file this is
    """
    # use an Re to match the filename convention and return one of
    ## 'configfile', 'mbpfile', 'contextfile', 'hiresfile' or ValueError
    if re.match(r'^.*ContextData\.txt$', filename):
        return 'contextfile'
    elif re.match(r'^.*Config\.txt$', filename):
        return 'configfile'
    elif re.match(r'^.*Burst\.txt$', filename):
        return 'mbpfile'
    elif re.match(r'^.*HiRes\.txt$', filename):
        return 'hiresfile'
    elif re.match(r'^.*DataTimes\.txt$', filename):
        return 'datatimes'
    else:
        raise(ValueError('No Match'))


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

    if len(args) < 1 or len(args) > 2:
        parser.error("incorrect number of arguments")

#==============================================================================
# check on the inputs
#==============================================================================
    infile = args[0]
    if len(args) == 1:
        # build the default output filename
        pth = os.path.abspath(os.path.dirname(infile))
        name = os.path.splitext(os.path.basename(infile))[0]
        if not options.hdf5:
            name += '_L1.txt'
        else:
            name += '_L1.h5'
        args.append(os.path.join(os.curdir, name))
    outfile = args[1]
    if not os.path.isfile(os.path.expanduser(infile)):
        parser.error("file {0} not found".format(infile))
    if os.path.isfile(os.path.expanduser(outfile)) and not options.force:
        parser.error("file {0} found and will not overwrite, try --force".format(outfile))

#==============================================================================
# deal with the filetype options
#==============================================================================
    configfile = False
    mbpfile = False
    contextfile = False
    hiresfile = False
    datatimesfile = False
    try:
        tp = determineFileType(infile)
    except (ValueError, NotImplementedError):
        # could not determine the type, die
        parser.error("Could not determine the file type and flag not given: {0}".format(infile))

    if tp == 'configfile':
        configfile = True
    elif tp == 'mbpfile':
        mbpfile = True
    elif tp == 'contextfile':
        contextfile = True
    elif tp == 'hiresfile':
        hiresfile = True
    elif tp == 'datatimes':
        datatimesfile = True
    else:
        raise(ValueError())

    if configfile:
        d = config.readConfig(infile)
    elif mbpfile:
        d = burst.readBurst(infile)
    elif contextfile:
        ContextFile(infile, outfile)
    elif hiresfile:
        d = hires.readHighRes(infile)
    elif datatimes:
        d = datatimes.readDatatimes(infile)
    else:
        raise(RuntimeError('How did we get here?  Programming error'))
    d.write(outfile, hdf5=options.hdf5)
    print('Wrote {0}'.format(outfile))


