#!/usr/bin/env python2.6

#==============================================================================
# This code enables a user to enter what requests we want to get
# it is clunky but will be a start
#==============================================================================



# standard library includes (alphabetical)
import datetime
from optparse import OptionParser
import os
try:
    import readline
    readline.parse_and_bind('enable-keypad')
except ImportError:
    pass
import sys
import warnings

from Request import Entry
from Request import Request
from Request import typeDict
from Request import parseData_Times
from Request import FIREOffException


warnings.simplefilter('always')

request = None

def make_request():
    global request
    print('Enter request date or enter for today (YYYYMMDD)')
    line = raw_input(': ')
    if not line:
        rdate = datetime.datetime.utcnow().date()
    else:
        try:
            rdate = datetime.datetime.strptime(line, '%Y%m%d').date()
        except ValueError:
            print('  ** Bad time format')
            make_request()
            return
    request = Request(date=rdate)

    
def print_inst():
    """
    print the instructions
    """
    txt = """**Tool to prepare a FIREBIRD data request**
    enter some number of requests in this way:
    sc, type, date, duration, priority 
    (e.g. 3, MICRO_BURST, 20130821T00:40:00, 40, 30)

    sc may be 1,2,3,4
    type may be {0}
    date in the format YYYYMMDDThh:mm:ss or YYYY-MM-DDThh:mm:ss
    duration in seconds
    priority is an integer, higher values higher priority

    write writes the command files
    quit quits

    ShortCuts:
    sc, DATA_TIMES::             - creates a DATA_TIMES entry from now forward (all always downlinked, priority=1000)
    sc, CONFIG:YYYYMMDD:         - creates CONFIG entries to fill a day (will skip time with no data, priority=900)
    sc, CONTEXT:YYYYMMDD:        - creates CONTEXT entries to fill a day (will skip time with no data, priority=700)
    sc, MICRO_BURST:YYYYMMDDThh: - creates MICRO_BURST entries to fill an hour (will skip time with no data, priority=500)
    """.format(' '.join(typeDict.keys()))
    print(txt)

def input_loop(datatimes=None):
    line = ''
    while True:
        line = raw_input(':::: ')
        if line in ['stop', 'write']:
            break
        if line == 'help':
            print_inst()
            continue
        # make an entry from the input
        try:
            line = line.split(',')
        except AttributeError:
            continue
        line = [v.strip() for v in line]
        # is the input a ShortCut?
        if len(line) == 2:
            try:
                sc = int(line[0])
            except ValueError:
                print("** invalid sc [1,2,3,4]**")
                continue            
            if line[1].upper() == 'DATA_TIMES::':
                entry = Entry(sc, 'DATA_TIMES', datetime.datetime.utcnow().replace(microsecond=0), 1, 1000)
                print('{0}: CREATED    --  {1} to {2}').format(entry, entry.date.isoformat(), entry.endDate.isoformat())
                request.addEntry(entry)
                continue
            elif line[1].upper().startswith('CONFIG'):
                tmp = line[1].split(':')
                date =  datetime.datetime.strptime(tmp[1], '%Y%m%d')
                date2 = date
                while date2.day == date.day: 
                    try:
                        entry = Entry(sc, 'CONFIG', date2, int(typeDict['CONFIG']['dataPerBlock'])*60 , 900, datatimes=datatimes) # hi pri
                    except FIREOffException:
                        date2 += datetime.timedelta(seconds=1)
                        continue
                    print('{0}: created    --  {1} to {2}').format(entry, entry.date.isoformat(), entry.endDate.isoformat())
                    request.addEntry(entry)
                    date2 += datetime.timedelta(seconds=entry.duration)
                continue
            elif line[1].upper().startswith('CONTEXT'):
                tmp = line[1].split(':')
                date =  datetime.datetime.strptime(tmp[1], '%Y%m%d')
                date2 = date
                while date2.day == date.day: 
                    try:
                        entry = Entry(sc, 'CONTEXT', date2, int(typeDict['CONTEXT']['dataPerBlock'])*60 , 700, datatimes=datatimes) # hi pri
                    except FIREOffException:
                        date2 += datetime.timedelta(seconds=1)
                        continue
                    print('{0}: created    --  {1} to {2}').format(entry, entry.date.isoformat(), entry.endDate.isoformat())
                    request.addEntry(entry)
                    date2 += datetime.timedelta(seconds=entry.duration)
                continue               
            elif line[1].upper().startswith('MICRO_BURST'):
                tmp = line[1].split(':')
                date =  datetime.datetime.strptime(tmp[1], '%Y%m%dT%H')
                date2 = date
                while date2.day == date.day: 
                    try:
                        entry = Entry(sc, 'MICRO_BURST', date2, int(typeDict['MICRO_BURST']['dataPerBlock'])*60 , 500, datatimes=datatimes) 
                    except FIREOffException:
                        date2 += datetime.timedelta(seconds=1)
                        continue
                    print('{0}: created    --  {1} to {2}').format(entry, entry.date.isoformat(), entry.endDate.isoformat())
                    request.addEntry(entry)
                    date2 += datetime.timedelta(seconds=entry.duration)
                continue               
                
        elif len(line) != 5:
            print('** input much be 5 entries **')
            continue
        else:
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
                try:
                    date = datetime.datetime.strptime(line[2], '%Y-%m-%dT%H:%M:%S')
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
                entry = Entry(sc, typ, date, dur, pri, datatimes=datatimes)
            except UserWarning, e:
                warnings.simplefilter('always')
                entry = Entry(sc, typ, date, dur, pri, datatimes=datatimes)
                print('** {0} **'.format(e))
            print('{0}:  CREATED    --   {1} to {2}').format(entry, entry.date.isoformat(), entry.endDate.isoformat())
            request.addEntry(entry)

    if line == 'write':
        request.sortEntries()
        request.toFile()


    
if __name__ == '__main__':
    usage = "usage: %prog [options] [Data_Times]"
    parser = OptionParser(usage=usage)

    parser.add_option("-f", "--force",
                  action="store_true", dest="force",
                  help="Force an overwrite, default=False", default=False)
    (options, args) = parser.parse_args()

    if len(args) > 1:
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
    if len(args) != 0:
        dtfile = args[0]
        if not os.path.isfile(dtfile):
            parser.error("Data_Times file: {0} did not exist")
    else:
        dtfile = None
            
    times = parseData_Times(dtfile)
                
    make_request()
    print_inst()

    input_loop(datatimes=times)
    







