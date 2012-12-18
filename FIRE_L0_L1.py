# -*- coding: utf-8 -*-
"""
FIRE_L0_L1.py

Converter form the FIRE L0 packets to L1 data

"""

# standard library includes (alphabetical)
from abc import ABCMeta, abstractmethod
from optparse import OptionParser
import os
import re

# dependency includes (alphabetical)
import dateutil.parser as dup
import numpy as np
import spacepy.datamodel as dm


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


class L0(dm.SpaceData):
    """
    base class to hold L0 data
    """
    __metaclass__ = ABCMeta

    def __init__(self, filename, outfilename):
        """
        given a filename read in the data
        """
        # have to call __init__ for SpaceData also
        super(L0, self).__init__()
        self.outfilename = outfilename
        self.filename = filename
        self.readL0()
        self.parseData()
        self.writeFile()

    def readL0(self, **kwargs):
        """
        read in the data file and return a list of the line sin the file
        """
        if 'delimiter' not in kwargs:
            kwargs['delimiter'] = ','
        if 'skiprows' not in kwargs:
            kwargs['skiprows'] = 0
        raw_data = np.loadtxt(self.filename,
                              dtype=str,
                              delimiter=kwargs['delimiter'],
                              skiprows=kwargs['skiprows'])
        # the epochs are the first column
        epoch = [dup.parse(v) for v in raw_data[:,0]]
        self['Epoch'] = dm.dmarray(epoch)
        # raw data is the rest
        ## often the last column is all '' if so we don't want it
        if (raw_data[:,-1] == '').all():
            raw_data = np.delete(raw_data, -1, -1)
        self['raw_data'] = raw_data[:,1:].astype(np.uint8)

    @abstractmethod
    def parseData(self):
        """
        Parse self['Epoch'] and self['raw_data'] into meaning quantities
        """
        pass

    def writeFile(self):
        """
        write out the data to a json headed ASCII file this is a L1 file!!
        """
        # don't write out the raw data
        del self['raw_data']
        dm.toJSONheadedASCII(self.outfilename, self, depend0='Epoch', order=['Epoch'])


class ConfigFile(L0):
    """
    class for a configuration file
    """
    def parseData(self):
        """
        Parse self['Epoch'] and self['raw_data'] into meaning quantities
        """
        self['data_type'] = dm.dmarray(self['raw_data'][:, 0])
        self['packet_counter'] = dm.dmarray(self['raw_data'][:, 1])
        self['cmd_reg_value'] = dm.dmarray(self['raw_data'][:, 2])
        self['cntrl_reg'] = dm.dmarray(self['raw_data'][:, 3])
        self['hi_res_interval'] = dm.dmarray(self['raw_data'][:, 4])
        self['context_selection'] = dm.dmarray(self['raw_data'][:, 5])
        self['mbp_selection'] = dm.dmarray(self['raw_data'][:, 6])
        # this cycles through the registers so this needs to also
        self['control_register'] = fillArray((len(self['Epoch'])))
        self['det_max_energy_setpoint'] = fillArray((len(self['Epoch'])))
        self['det_energy_setpoint_5'] = fillArray((len(self['Epoch'])))
        self['det_energy_setpoint_4'] = fillArray((len(self['Epoch'])))
        self['det_energy_setpoint_3'] = fillArray((len(self['Epoch'])))
        self['det_energy_setpoint_2'] = fillArray((len(self['Epoch'])))
        self['det_energy_setpoint_1'] = fillArray((len(self['Epoch'])))
        self['det_energy_setpoint_0'] = fillArray((len(self['Epoch'])))
        for key, reg in [('control_register', 0), ('det_max_energy_setpoint', 4),
                         ('det_energy_setpoint_5', 5), ('det_energy_setpoint_4', 6),
                         ('det_energy_setpoint_3', 7), ('det_energy_setpoint_2', 8),
                         ('det_energy_setpoint_1', 9), ('det_energy_setpoint_0', 10)]:
            mask = (self['packet_counter'] & 0b00001111) == reg
            self[key][mask] = self['cmd_reg_value'][mask]



class MBPFile(L0):
    """
    class for microburst parameter data
    """
    def parseData(self):
        """
        Parse self['Epoch'] and self['raw_data'] into meaning quantities
        """
        MB0_100 = self['raw_data'][:,0:2]
        MB0_500 = self['raw_data'][:,2:5]
        MB1_100 = self['raw_data'][:,5:7]
        MB1_500 = self['raw_data'][:,7:10]
        self['MB0_100'] = dm.dmarray(combineBytes(MB0_100[:,0],  MB0_100[:,1]))
        self['MB0_500'] = dm.dmarray(combineBytes(MB0_500[:,0],  MB0_500[:,1], MB0_500[:,2]))
        self['MB1_100'] = dm.dmarray(combineBytes(MB1_100[:,0],  MB1_100[:,1]))
        self['MB1_500'] = dm.dmarray(combineBytes(MB1_500[:,0],  MB1_500[:,1], MB1_500[:,2]))


class ContextFile(L0):
    """
    class for context data
    """
    def parseData(self):
        """
        Parse self['Epoch'] and self['raw_data'] into meaning quantities
        """
        cxt0 = self['raw_data'][:, :3]
        cxt1 = self['raw_data'][:, 3:]
        self['context0'] = dm.dmarray(combineBytes(cxt0[:, 0], cxt0[:, 1], cxt0[:, 2]))
        self['context1'] = dm.dmarray(combineBytes(cxt1[:, 0], cxt1[:, 1], cxt1[:, 2]))


class HiResFile(L0):
    """
    class for hi-res data data
    """
    def parseData(self):
        """
        Parse self['Epoch'] and self['raw_data'] into meaning quantities
        """
        hr0 = self['raw_data'][:,0:12]
        hr1 = self['raw_data'][:,12:]
        self['hr0'] = fillArray( (len(self['Epoch']), 6) )
        self['hr1'] = fillArray( (len(self['Epoch']), 6) )
        for chan, ii in enumerate((range(0, 12, 2))):
            self['hr0'][:, chan] = combineBytes(hr0[:, ii], hr0[:,ii+1])
            self['hr1'][:, chan] = combineBytes(hr1[:, ii], hr1[:,ii+1])


def fillArray(shape, fillval=-999, dtype=np.int):
    """
    create an array of given shape and type filled with fill
    """
    dat = np.zeros(shape, dtype=dtype)
    dat[...] = fillval
    return dm.dmarray(dat)

def combineBytes(*args):
    """
    given the bytes of a multi byte number combine into one
    pass them in least to most significant
    """
    ans = 0
    for i, val in enumerate(args):
        ans += (val << i*8) # 8 is the bits per number
    return ans

def determineFileType(filename):
    """
    given a filename figure out what type of file this is
    """
    # use an Re to match the filename convention and return one of
    ## 'configfile', 'mbpfile', 'contextfile', 'hiresfile' or ValueError
    if re.match(r'^.*ContextData.*$', filename):
        return 'contextfile'
    elif re.match(r'^.*Config.*$', filename):
        return 'configfile'
    elif re.match(r'^.*BurstData.*$', filename):
        return 'mbpfile'
    elif re.match(r'^.*HiResData.*$', filename):
        return 'hiresfile'
    else:
        raise(ValueError('No Match'))


if __name__ == '__main__':
    usage = "usage: %prog [options] infile [outfile]"
    parser = OptionParser(usage=usage)

    parser.add_option("-c", "--configfile",
                  action="store_true", dest="configfile",
                  help="This is a config file reading in", default=False)
    parser.add_option("-m", "--mbpfile",
                  action="store_true", dest="mbpfile",
                  help="This is a MBP file reading in", default=False)
    parser.add_option("-x", "--contextfile",
                  action="store_true", dest="contextfile",
                  help="This is a context file reading in", default=False)
    parser.add_option("-H", "--hiresfile",
                  action="store_true", dest="hiresfile",
                  help="This is a Hi-Res file reading in", default=False)
    parser.add_option("-f", "--force",
                  action="store_true", dest="force",
                  help="Force an overwrite, default=False", default=False)
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
        name += '_L1.txt'
        args.append(os.path.join(pth, name))
    outfile = args[1]
    if not os.path.isfile(os.path.expanduser(infile)):
        parser.error("file {0} not found".format(infile))
    if os.path.isfile(os.path.expanduser(outfile)) and not options.force:
        parser.error("file {0} found and will not overwrite".format(outfile))

#==============================================================================
# deal with the filetype options
#==============================================================================
    if sum( (options.configfile, options.mbpfile, options.contextfile, options.hiresfile) ) > 1:
        parser.error("File type flags are mutually exclusive")
    # if none specified then try and guess
    if sum( (options.configfile, options.mbpfile, options.contextfile, options.hiresfile) ) == 0:
        try:
            tp = determineFileType(infile)
            if tp == 'configfile':
                options.configfile = True
            elif tp == 'mbpfile':
                options.mbpfile = True
            elif tp == 'contextfile':
                options.contextfile = True
            elif tp == 'hiresfile':
                options.hiresfile = True
            else:
                raise(ValueError())
        except (ValueError, NotImplementedError):
            # could not determine the type, die
            parser.error("Could not determine the file type and flag not given")


    if options.configfile:
        ConfigFile(infile, outfile)
    elif options.mbpfile:
        MBPFile(infile, outfile)
    elif options.contextfile:
        ContextFile(infile, outfile)
    elif options.hiresfile:
        HiResFile(infile, outfile)
    else:
        raise(RuntimeError('How did we get here?  Programming error'))
    print('Wrote {0}'.format(outfile))


