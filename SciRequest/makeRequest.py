#!/usr/bin/env python2.6

#==============================================================================
# This code enables a user to enter what requests we want to get
# it is clunky but will be a start
#==============================================================================



# standard library includes (alphabetical)
import datetime
from optparse import OptionParser
import os
import readline
import warnings

import dateutil.parser as dup

from Request import Entry
from Request import Request

readline.parse_and_bind('enable-keypad')

typeDict = {'HIRES':None,
            'CONTEXT':None,
            'MICRO_BURST':None,
            'CONFIG':None,
            'DATA_TIMES':None,}

request = None

def make_request():
    global request
    print('Enter request date or enter for today (YYYYMMDD)')
    line = raw_input(': ')
    if not line:
        rdate = datetime.datetime.utcnow().date()
    else:
        rdate = datetime.datetime.strptime(line, '%Y%m%d').date()
    request = Request(date=rdate)

    
def print_inst():
    """
    print the instructions
    """
    txt = """**Tool to prepare a FIREBIRD data request**
    enter some number of requests in this way:
    sc, typ, date, duration, priority 

    sc may be 1,2,3,4
    type may be {0}
    date in the format YYYYMMDDThh:mm:ss
    duration in seconds
    priority is an integer, higher values higher priority

    write writes the comand files
    quit quits""".format(' '.join(typeDict.keys()))
    print(txt)

def input_loop():
    line = ''
    while line != 'quit' and line != 'write':
        line = raw_input(':::: ')
        if line in ['stop', 'write']:
            break
        if line == 'help':
            print_inst()
            continue
        # make an entry from the input
        line = line.split(',')
        line = [v.strip() for v in line]
        if len(line) != 5:
            print('** input much be 5 entries **')
            continue
        try:
            sc = int(line[0])
        except ValueError:
            print("** invalid sc [1,2,3,4]**")
            continue
        typ = line[1].upper()
        if typ not in typeDict:
            print("** invalid type [{0}]**".format(' '.join(typeDict.keys())))
            continue
        try:
            date = datetime.datetime.strptime(line[2], '%Y%m%dT%H:%M:%S')
        except ValueError, e:
            print e
            continue
        try:
            dur = int(line[3])
        except ValueError:
            print("** invalid duration**")
            continue
        if dur <= 0:
            print("** invalid duration**")
            continue
        try:
            pri = int(line[4])
        except ValueError:
            print("** invalid priority**")
            continue
        if pri <= 0:
            print("** invalid priority**")
            continue

        warnings.simplefilter('error')
        try:
            entry = Entry(sc, typ, date, dur, pri)
        except UserWarning, e:
            warnings.simplefilter('ignore')
            entry = Entry(sc, typ, date, dur, pri)
            print('** {0} **'.format(e))
        t1 = date + datetime.timedelta(seconds=dur)
        print('{0}: created    --  {1} to {2}').format(entry, date.isoformat(), t1.isoformat())
        request.addEntry(entry)

    if line == 'write':
        request.sortEntries()
        request.toFile()
        

if __name__ == '__main__':
    usage = "usage: %prog [options] Data_Times [[Data_Times]...]"
    parser = OptionParser(usage=usage)

    parser.add_option("-f", "--force",
                  action="store_true", dest="force",
                  help="Force an overwrite, default=False", default=False)
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("incorrect number of arguments")

#==============================================================================
# check on the inputs
#==============================================================================

#    fu = args[0]
#    try:
#        fu = int(fu)
#    except ValueError:
#        parser.error("Did not understand FU designation: {0}.  [1,2,3,4]".format(fu))
#    if fu not in [1,2,3,4]:
#        parser.error("Invalid FU designation: {0}.  [1,2,3,4]".format(fu))
        
        

#    outname = args[0]
    dtfiles = [os.path.expandvars(os.path.expanduser(v)) for v in args[:]]
    for f in dtfiles:
        if not os.path.isfile(f):
            parser.error("Data_Times file: {0} did not exist")

    make_request()
    print_inst()

    input_loop()








