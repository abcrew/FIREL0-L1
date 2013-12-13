import abc
import datetime
import itertools
import os
import time

import numpy as np
from spacepy import datamodel as dm

import packet
import page


def total_seconds(dt):
    """
    make up for pyhton2.6 not having datetime.timedelta.total_seconds
    """
    ans = dt.days * 24 * 60 * 60
    ans += dt.seconds
    ans += (dt.microseconds / 1e6)
    return ans


def hex2int(inpage):
    """
    convert a page of ascii hex data to integrers and None as needed
    """
    dat = []
    for v in inpage:
        try:
            dat.append(int(v, 16))
        except TypeError:
            dat.append(None)
    return dat

def dat2time(inval):
    """
    take 8 bytes and change them to a datetime
    """
    t0 = datetime.datetime(2000 + inval[0], inval[1], inval[2],
                           inval[3], inval[4], inval[5],
                           1000*(inval[6]*(2**8) + inval[7]))
    return t0

def validDate(inval, mindate=datetime.datetime(2013, 12, 1), maxdate=datetime.datetime(2015, 12, 31)):
    """
    go through input data and if it makes a date in the given rage it is valid, otherwise it is not
    """
    try:
        inval = [int(v, 16) for v in inval]
    except TypeError:
        return False
    try:
        date = dat2time(inval)
        if date >= mindate and date <= maxdate:
            return True
        else:
            return False
    except (ValueError, TypeError):
        return False

    ## if isinstance(inval, str) and len(inval) > 2:
    ##     t0tmp = inval.split()
    ##     t1tmp = [int(v, 16) for v in t0tmp[0:6]]
    ##     t1tmp.append(int(t0tmp[6]+t0tmp[7], 16))
    ##     t0 = datetime.datetime(2000 + t1tmp[0], t1tmp[1], t1tmp[2],
    ##                            t1tmp[3], t1tmp[4], t1tmp[5], 1000*t1tmp[6])
    ## else:
    ##     try:
    ##         t1tmp = [int(v, 16) for v in inval[0:6]]
    ##     except TypeError:
    ##         t1tmp = inval[0:6]
    ##     try:
    ##         t1tmp.append(int(inval[6]+inval[7], 16))
    ##     except TypeError:
    ##         t1tmp.append(2**8*inval[6] + inval[7])
    ##     try:
    ##         t0 = datetime.datetime(2000 + t1tmp[0], t1tmp[1], t1tmp[2],
    ##                                t1tmp[3], t1tmp[4], t1tmp[5], 1000*t1tmp[6])
    ##     except ValueError:
    ##         return None
    ## return t0

class data(object):
    __metaclass__ = abc.ABCMeta
    """
    just a few methods common to all the data type classes below
    """
    def write(self, filename, hdf5=False):
        if hdf5:
            dm.toHDF5(filename, self.dat)
        else:
            dm.toJSONheadedASCII(filename, self.dat, order=['Epoch'] )
        print('    Wrote {0}'.format(os.path.abspath(filename)))

    @classmethod
    @abc.abstractmethod
    def read(self, filename, retpktnum=False):
        """read in the data from the file"""
        b = packet.BIRDpackets(filename)
        print('    Read {0} packets'.format(len(b)))
        pages = page.page.fromPackets(b)
        print('    Read {0} pages'.format(len(pages)))
        if retpktnum:
            # build a list the size of pages that tells the
            #  pktnum of each byte in the pages list
            return pages, b
        else:
            return pages

class dataPage(list):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def major_data(self, inval):
        """Method the decodes data with a major time stamp"""
        return

    @abc.abstractmethod
    def minor_data(self, inval):
        """Method the decodes data with a minor time stamp"""
        return


