#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SPQToJAS.py

Take a SPQ file and output a JAS script for the operator

"""

# standard library includes (alphabetical)
import datetime
from optparse import OptionParser
import os


# JAS format:
#  HIRES, 2013, 12, 6, 14, 31, 0, 60, FU_2_JAS_0043_20131209_0716.jpp


# this is type, then seconds of data per block
typeDict = {'HIRES':None,
            'CONTEXT':None,
            'MICRO_BURST':None,
            'CONFIG':None,
            'DATA_TIMES':None} # This was a TBD and 2000 was made up

def toNone(inval):
    if inval in [0, 'NONE', 'None']:
        return None

def NoneToStr(inval):
    if inval is None:
        return 'NONE'


class SPQline(object):
    def __init__(self, inline):
        """
        take a line of a file and parse into this object
        """
        p_line = inline.split(',')
        p_line = [v.strip() for v in p_line]
        if p_line == ['']: # empty line
            return
        self.dtype = p_line[0].upper()
        if self.dtype not in typeDict.keys():
            raise(ValueError("Did not understand dtype, {0}  must be {1}".format(self.dtype, ' '.join(typeDict.keys()))))
        self.year = p_line[1]
        self.month = p_line[2]
        self.day = p_line[3]
        self.hour = p_line[4]
        self.minute = p_line[5]
        self.second = p_line[6]
        self.duration = p_line[7]
        self.JAS = toNone(p_line[8])
        if self.dtype != "DATA_TIMES":
            self.dt = datetime.datetime(int(self.year), int(self.month), int(self.day),
                                        int(self.hour), int(self.minute), int(self.second))
        else:
            self.dt = None
            
    def __str__(self):
        outstr = ', '.join([self.dtype, self.year, self.month, self.day,
                            self.hour, self.minute, self.second, NoneToStr(self.JAS)])
        return outstr
    
    __repr__ = __str__


class SPQfile(list):
    def __init__(self):
        self.comments = []
    
    def addLine(self, inobj):
        if not isinstance(inobj, SPQline):
            raise(ValueError("Invalid input dtype"))
        self.append(inobj)

    def addComment(self, inobj):
        self.comments.append(inobj)

    def __str__(self):
        outstr = '\n'.join(self.comments)
        outstr += '\n'.join(self)
        return outstr
    
    __repr__ = __str__

    def toFile(self, outname):
        with open(outname, 'w') as fp:
            for v in self.comments:
                fp.writelines(v + '\n')
            for v in self:
                fp.writelines(str(v) + '\n')
        print("Wrote: {0}".format(os.path.abspath(outname)))

def parseFile(infile):
    with open(infile, 'r') as fp:
        lines = fp.readlines()
    spqf = SPQfile()
    for spql in lines:
        if spql[0] == '#':
            spqf.addComment(spql)
            continue
        tmp = SPQline(spql)
        if hasattr(tmp, 'dtype'): # else a blank line
            spqf.addLine(tmp)
    return spqf
    

if __name__ == '__main__':
    usage = "usage: %prog [options] infile"
    parser = OptionParser(usage=usage)

    parser.add_option("-f", "--force",
                  action="store_true", dest="force",
                  help="Force an overwrite, default=False", default=False)
    parser.add_option("-o", "--outfile",
                      dest="outfile",
                      help="Use a difference output filename", default=None)
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("incorrect number of arguments")

    if not os.path.isfile(args[0]):
        raise(OSError("Input file: {0} not found".format(args[0])))

    if options.outfile is None:
        options.outfile = args[0] + ".processed"
    
    if os.path.isfile(options.outfile) and not options.force:
        raise(RuntimeError("Outfile: {0} exists and will not overwrite, try --force".format(options.outfile)))

    spq = parseFile(args[0])
    
    if os.path.isfile(options.outfile):
        os.remove(options.outfile)
    spq.toFile(options.outfile)

