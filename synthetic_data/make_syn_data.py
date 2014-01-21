
from __future__ import division

"""
Make synthetic packets so that we can play with breaking them and decodng them as in reality


"""

from pylab import *

import datetime
import itertools
import os
import sys

import numpy as np
import spacepy.time as spt

from L0toL1 import packet
from L0toL1.CCITT_CRC16 import CRCfromString

dt0 = datetime.datetime(2014, 1, 14)
def makeGRT():
    global dt0
    for i in range(10000):
        dt0 += datetime.timedelta(seconds=1)
        yield dt0.strftime("%H:%M:%S:123")


def makeTimes(starttime=datetime.datetime(2000, 1, 1), num=1000):
    """
    make a times array
    """
    dt = [datetime.timedelta(microseconds=30e3), 
          datetime.timedelta(microseconds=15e3), 
          datetime.timedelta(microseconds=15e3), 
          datetime.timedelta(microseconds=15e3)]
    ans = [starttime]
    for ii, val in enumerate(itertools.cycle(dt)):
        if ii >= num:
            break
        ans.append(ans[-1] + val)
    return ans


def split(str, num=2):
    return [ str[start:start+num] for start in range(0, len(str), num) ]

def ints_to_hex(inval, bytes=1, reverse=False):
    """
    convert all the data into its correct hex repr
    """
    if inval > 2**(8*bytes):
        raise(ValueError("Too small a size for {0} specified: {1}".format(inval, bytes)))
    ans = '{0:04X}'.format(inval)
    if len(ans) > (bytes*2):
        ans = ans[-(bytes*2):]
    if reverse:
        ans = ' '.join(split(ans.strip())[::-1])
        return ans + ' '
    return ' '.join(split(ans)) + ' '
    

def datetime_to_major(inval):
    """
    return the integers of a datetime 8 bytes
    yy, mm, dd, hh, mm, ss, mmmm
    """
    yy, mm, dd, hh, MM, ss, mmmm = (int(v) for v in inval.strftime('%y %m %d %H %M %S %f').split())
    ans = ''.join(ints_to_hex(v, 1) for v in [yy, mm, dd, hh, MM, ss]) + ints_to_hex( mmmm//1000, 2)  # microseconds truncated to milliseconds
    return ans
    
def datetime_to_minor(inval):
    """
    return the integers of a datetime 2 bytes
    mmmm
    """
    mmmm = int(inval.strftime('%f'))
    return ints_to_hex(mmmm//1000,2)  # microseconds truncated to milliseconds



def makePacketHeader(datalen, srcid=65287, destid=65281, cmd_tml=0, funid=205, seqnum=1, seqidx=1, pktnum=1):
    """
    C0 FF 07 FF 01 00 CD 1A 01 01 DE 0D 0C 0A 06 06
    """
    ans = ''
    header = ('C0 ' + ints_to_hex(srcid, 2) + ints_to_hex(destid, 2) + 
              ints_to_hex(cmd_tml, 1) + ints_to_hex(funid, 1) + 
              ints_to_hex(seqnum, 1) + ints_to_hex(seqidx, 1) + 
              ints_to_hex(pktnum, 1) + ints_to_hex(datalen+1, 1))
    ans += header
    return ans

def makePacket(data, srcid=65287, destid=65281, cmd_tml=0, funid=205, seqnum=1, seqidx=1, pktnum=1):
    ans = makePacketHeader(len(data)//3,  srcid, destid, cmd_tml, funid, seqnum, seqidx, pktnum)
    ans += data
    ans += ' ' + ints_to_hex(int(CRCfromString(ans.strip())[2:], 16),2) + 'C0 ' 
    return ans

def makeData(times, amp=10, period=40):
    """
    make sine wave data on a cadence

    period is given in seconds

    one detector is x10 larger than the other
    the channels are all 1.2x the previous one 
    """
    omega = 2*np.pi/period
    omega = 6.366995622580105
    ticks = spt.Ticktock(times).JD
    ticks -= ticks[0]
    ticks *= 24*60*60  # change to seconds
    val = amp*np.sin(omega/40*ticks)
    val -= val.min()
    val += 50
    channels = np.vstack([val*1.2*6, val*1.2*5, val*1.2*4, val*1.2*3, val*1.2*2, val*1.2*1])
    return np.vstack( [channels, channels/10] ).T.astype(int)
    

def buildPackets(starttime=datetime.datetime(2012, 3, 14, 12, 30, 50, 100000), num=1000, seed=123):
    """
    do all the work of builing packets and spit them out

    16000 times is 5 minutes
    """
    times = makeTimes(starttime, num*9)
    # build up a 4096 page of data
    newPage = 1
    nbytes = 0
    page = ''
    data = makeData(times)
    leftover = ''

    print '** data stats **', data.min(), data.max()
    
    figure(figsize=(20,9))
    subplot(211)
    plot(times, data[:,0:6])
    subplot(212)
    plot(times, data[:,6:])
    savefig('Input_fb_fake_data.png')
    
    data = data.tolist()

    packets = []
    seqnum = 63
    seqidx = 0 
    np.random.seed(seed)
    while times: # while we are not done
        while times:
            if len(page.split()) + 26 > 4096:
                break 
            t = times.pop(0)
            # add the time to the data stack
            if newPage:
                page += datetime_to_major(t) 
                newPage = False
            else:
                page +=  datetime_to_minor(t) 
                # now add the data
            page += ''.join([ints_to_hex(v, 2, reverse=True) for v in data.pop(0)])

        newPage = True
        #        def makePacket(data, srcid=65287, destid=65281, cmd_tml=0, funid=205, seqnum=1, seqidx=1, pktnum=1):
        seqidx += 1
        pktnum = 1
        page += ' '.join(['00']*(4096-len(page.split())))
        while page:
            # grab a 222 byte chunk
            # make the packets random length
            packenlen = 222 - np.random.random_integers(0, 5)
            
            print 'seqidx', seqidx, 'pktnum', pktnum, hex(pktnum), 'len(page)', len(page.split()), 'pktlen', packenlen
            # now make packets for these data, that is a page
            # add 00 on the end so that we have 4096 bytes

            tmp = page[0:packenlen*3]
            page = page[packenlen*3:]
            if '' in tmp.split():
                1/0
            packets.append(makePacket(tmp.strip(), seqnum=seqnum, seqidx=seqidx, pktnum=pktnum))
            pktnum += 1
    # add the GRT to the packets so we can use that piece
    packets = ['{0} - '.format(makeGRT().next()) + v for v in packets]
    
    return packets


if __name__ == '__main__':
    # do it
    if len(sys.argv) != 2:
        print('Usage: {0} outfile'.format(sys.argv[0]))
        sys.exit(1)

    if os.path.isfile(sys.argv[1]):
        print("outout exists and will not be overwritten")
        sys.exit(2)
    packets = buildPackets(num=1094)
    try:
        with open(sys.argv[1], 'w') as fp:
            for d in packets:
                fp.writelines(d)
                fp.write('\n')
    except Exception:
        os.remove(sys.argv[1])
        sys.exit(-1)
    print("Wrote: {0}".format(sys.argv[1]))

    
