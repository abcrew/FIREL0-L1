#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FIRE_L0_L1.py

Converter form the FIRE L0 packets to L1 data

"""

# standard library includes (alphabetical)
from optparse import OptionParser
import os
import re

# dependency includes (alphabetical)


from FIREdata import burst
from FIREdata import config
from FIREdata import context
from FIREdata import datatimes
from FIREdata import hires



def determineFileType(filename):
    """
    given a filename figure out what type of file this is
    """
    # use an Re to match the filename convention and return one of
    ## 'configfile', 'mbpfile', 'contextfile', 'hiresfile' or ValueError
    if re.match(r'^.*Context\.txt$', filename):
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
    try:
        tp = determineFileType(infile)
    except (ValueError, NotImplementedError):
        # could not determine the type, die
        parser.error("Could not determine the file type and flag not given: {0}".format(infile))

    if tp == 'configfile':
        d = config.read(infile)
    elif tp == 'mbpfile':
        d = burst.read(infile)
    elif tp == 'contextfile':
        d = context.read(infile)
    elif tp == 'hiresfile':
        d = hires.read(infile)
    elif tp == 'datatimes':
        d = datatimes.read(infile)
    else:
        raise(ValueError())

    if options.force and os.path.isfile(os.path.expanduser(outfile)):
        os.remove(outfile)
    d.write(outfile, hdf5=options.hdf5)
    print('Wrote {0}'.format(outfile))


