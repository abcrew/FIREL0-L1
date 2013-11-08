#!/usr/bin/env python2.6

"""
module to transfer files from inside (ect-soc-s1) to outside (stevens)

uses a configuration file for products, sources, destinations, and dates
"""


import ConfigParser
import datetime
import os
import os.path
import re
import subprocess
import sys
import warnings


def toBool(value):
    if value in ['True', 'true', True, 1, 'Yes', 'yes']:
        return True
    elif value in ['False', 'false', False, 0, 'No', 'no']:
        return False
    else:
        return value

def toNone(value):
    if value in ['', 'None']:
        return None
    else:
        return value



class Transfer(object):
    """
    class to actually do the transferring and handle what to transfer
    """
    def __init__(self, configFilename=None, options=None):
        #setup the attributes that will be used in this class
        self.confdict = {} # conf dict from the configuration file
        self.configFilename = configFilename
        self.readconfig()
        if options.list:
            if options.filter is not None:
                must_have = [v for v in options.filter.split(',')]
                self.confdict = dict(((k, v) for (k, v) in self.confdict.iteritems() if min((m in k for m in must_have))))
            keys = sorted(self.confdict.keys())
            for c in keys:
                print(c)
            if not keys: # if there were none
                print('** No matching sections found. Filter was "{0}"  **'.format(options.filter))
            return

        if options.filter is not None:
            must_have = [v for v in options.filter.split(',')]
            self.confdict = dict(((k, v) for (k, v) in self.confdict.iteritems() if min((m in k for m in must_have))))
            if not self.confdict:
                print('** No matching sections found. Filter was "{0}"  **'.format(options.filter))

        for trans in self.confdict:
            self.doRsync(trans)

    def doRsync(self, key):
        """
        do the rsync according to the key
        """
        if sys.platform == 'darwin':
            cmd = ["/opt/local/bin/lftp -e 'mirror"]
        else:
            cmd = ["lftp -e 'mirror"]
        cmd.append(self.confdict[key]['source'])
        cmd.append(self.confdict[key]['destination'])
        cmd.append(" ;bye '")
        if self.confdict[key]['descend']:
            cmd.append('-r')
        else:
            #cmd.append('-d')
            pass
        if self.confdict[key]['flags'] is not None:
            cmd.extend(self.confdict[key]['flags'].split())
            if 'remotehost' in self.confdict[key] and self.confdict[key]['remotehost'] is not None: # early eval to the rescue
                  cmd.append( self.confdict[key]['remotehost'])
        #if self.confdict[key]['delete']: cmd.append('--delete-after')
        # add in some timeouts TODO make them setable
        cmd = ' '.join(cmd)
        print("Running: {0}".format(cmd))
        subprocess.call(cmd, shell=True)

    def readconfig(self):
        expected_items = ['source', 'destination', 'flags', 'descend', 'delete']
        # Create a ConfigParser object, to read the config file
        cfg=ConfigParser.SafeConfigParser()
        cfg.read(self.configFilename)
        sections = cfg.sections()
        # Read each parameter in turn
        ans = {}
        for section in sections:
            ans[section] = dict(cfg.items(section))
        # make sure that for each section the reqiured items are present
        for k in ans:
            for ei in expected_items:
                if ei not in ans[k]:
                    raise(ValueError('Section [{0}] does not have required key "{1}"'.format(k, ei)))
        # check that we can parse the dates
        for k in ans:
            if not '@' in ans[k]['source']:
                ans[k]['source'] = os.path.join(os.path.abspath(os.path.expanduser(os.path.expandvars(ans[k]['source']))), '')
            ans[k]['destination']   = os.path.expanduser(os.path.expandvars(ans[k]['destination']))
            ans[k]['flags']   = toNone(ans[k]['flags'])
            ans[k]['descend'] = toBool(ans[k]['descend'])
            ans[k]['delete'] = toBool(ans[k]['delete'])

        self.confdict = ans
