import abc
import datetime
import itertools
import os
import time

import numpy as np
from spacepy import datamodel as dm

import packet


def dat2time(inval):
    """
    take 8 bytes and change them to a datetime
    """
    if isinstance(inval, str) and len(inval) > 2:
        t0tmp = inval.split()
        t1tmp = [int(v, 16) for v in t0tmp[0:6]]
        t1tmp.append(int(t0tmp[6]+t0tmp[7], 16))
        t0 = datetime.datetime(2000 + t1tmp[0], t1tmp[1], t1tmp[2],
                               t1tmp[3], t1tmp[4], t1tmp[5], 1000*t1tmp[6])
    else:
        try:
            t1tmp = [int(v, 16) for v in inval[0:6]]
        except TypeError:
            t1tmp = inval[0:6]
        try:
            t1tmp.append(int(inval[6]+inval[7], 16))
        except TypeError:
            t1tmp.append(2**8*inval[6] + inval[7])
        try:
            t0 = datetime.datetime(2000 + t1tmp[0], t1tmp[1], t1tmp[2],
                                   t1tmp[3], t1tmp[4], t1tmp[5], 1000*t1tmp[6])
        except ValueError:
            return None
    return t0

class data(object):
    __metaclass__ = abc.ABCMeta
    """
    just a few methods common to all the data type classes below
    """
    def write(self, filename, hdf5=False):
        if hdf5:
            dm.toHDF5(filename, self.data)
        else:
            dm.toJSONheadedASCII(filename, self.data, order=['Epoch'] )
        print('    Wrote {0}'.format(os.path.abspath(filename)))

    @classmethod
    @abc.abstractmethod
    def read(self, filename):
        """read in the data from the file"""
        pass
            
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


