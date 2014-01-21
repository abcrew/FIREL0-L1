#!/usr/bin/env python

"""
Code to combine FIREBIRD data files changing the GRT time into a GRT datetime


"""
import datetime
import os
import sys

from L0toL1 import packet

def doIt(files):
    """
    read in the files and covert all the GRT to isoformat
    """
    ans = []
    for f in files:
        with open(f, 'r') as fp:
            lines = fp.readlines()
        ans.extend([packet.parseline(v, filename=f) for v in lines])
    ans = sorted(ans)
    return ans


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: {0} infile [[infile] [infile] [...]]".format(sys.argv[0]))
        sys.exit(-1)
    files = sys.argv[1:]
    ans = doIt(files)
    ext = files[0].split('-')[-1]
    outname = datetime.date.today().isoformat() + '-' + ext
    with open(outname, 'w') as fp:
        fp.writelines(ans)
    print("Wrote: {0}, {1} packets".format(os.path.abspath(outname), len(ans)))


    

    
