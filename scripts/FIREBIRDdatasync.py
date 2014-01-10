#!/usr/bin/env python2.6

""" Get the latest kernels and make master kernel files for use with furnish """

from optparse import OptionParser
import os

import DataSync.sync as ss


def doIt(conffile, verbose):
    """
    do the sync
    """
    ss.Transfer(conffile, verbose)


if __name__ == '__main__':
    usage = "usage: %prog [options] config_file"
    parser = OptionParser(usage=usage)

    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose",
                  help="Verbose output", default=False)
    parser.add_option("-f", "--filter",
                  dest="filter", help="Comma seperated list of strings that must be in the sync conf name (e.g. -f firebird,fu1)",
                  default=None)
    parser.add_option("-l", "--list",
                  dest="list", help="Instead of syncing list the sections of the conf file",
                  action="store_true", default=False)

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("incorrect number of arguments")

    if not os.path.isfile(os.path.expanduser(args[0])): # if the config file does not exist bail out
        parser.error("config file {0} not found".format(args[0]))

    doIt(args[0], options)



