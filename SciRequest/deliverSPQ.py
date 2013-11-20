#!/usr/bin/env python2.6

#==============================================================================
# This code enables a user to enter what requests we want to get
# it is clunky but will be a start
#==============================================================================



# standard library includes (alphabetical)
import ConfigParser
import glob
import os
from optparse import OptionParser
import sys

try:
    import paramiko
except ImportError:
    print('paramiko missing must manually upload')
    sys.exit(1)


def readconfig(configFilename):
    # Create a ConfigParser object, to read the config file
    cfg=ConfigParser.SafeConfigParser()
    cfg.read(configFilename)
    sections = cfg.sections()
    # Read each parameter in turn
    ans = {}
    for section in sections:
        ans[section] = dict(cfg.items(section))
    return ans

def makeSFTP(config, port=22):
    t = paramiko.Transport((config['connection']['remotehost'], port))
    t.connect(username=config['connection']['username'], password=config['connection']['password'])
    sftp = paramiko.SFTPClient.from_transport(t)
    return sftp

def remoteFiles(sftp, fu, config):
    """
    given a sftp session and flught unit number get a list of remote files
    """
    section = [v for v in config if str(fu) in v][0]
    if not section:
        raise(ValueError('Invalid FIREBIRD unit'))
    return set(sftp.listdir(config[section]['destination']))

def upload(sftp, fname, config):
    """
    upload a file to the right place as specified by config
    """
    try:
        fu = int(fname[3])
    except ValueError:
        raise(ValueError('Bad filename entered'))
    section = [v for v in config if str(fu) in v][0]
    if not section:
        raise(ValueError('Invalid FIREBIRD unit'))
    attr = sftp.put(os.path.abspath(fname), os.path.join(config[section]['destination'], fname))
#    if not attr:
#        raise(ValueError('Upload unsuccessful'))

def localFiles(localdir):
    """
    get the SPQ files form the local dir
    """
    files = glob.glob('FU_[1234]_SPQ_201[3456789][01][0-9][0-3][0-9]_v[0-9][0-9].csv')
    if not files:
        raise(ValueError('No SPQ files in requested directory: {0}'.format(localdir)))
    return set(files)

def filesToUpload(remotefiles, localfiles):
    """
    given the two sets which files to upload
    """
    return localfiles.difference(remotefiles)

def _whichFB(inval):
    """
    given an input string which FB unit does it belong to?
    """
    if inval.startswith('FU_1'):
        return 1
    elif inval.startswith('FU_2'):
        return 2
    elif inval.startswith('FU_3'):
        return 3
    elif inval.startswith('FU_4'):
        return 4
    else:
        raise(ValueError('Cannot determine which FIREBIRD unit'))



if __name__ == '__main__':
    usage = "usage: %prog [options] localDirectory"
    parser = OptionParser(usage=usage)

    parser.add_option("-f", "--force",
                  action="store_true", dest="force",
                  help="Force an overwrite, default=False", default=False)
    parser.add_option("-c", "--config", dest="config",
                  help="Configuration file to use, default=FIREBIRD_deliver.conf",
                  default='./FIREBIRD_deliver.conf')
    parser.add_option("-d", "--dryrun", dest="dryrun",
                  help="Only dryrun, do not actually upload", action='store_true',
                  default=False)

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("incorrect number of arguments")

    # get local files
    localfiles = localFiles(args[0])
    fus = set([_whichFB(v) for v in localfiles])

    # read config
    config = readconfig(options.config)
    # connect
    sftp = makeSFTP(config)

    remotefiles = set([])
    for fu in fus:
        for f in remoteFiles(sftp, fu, config):
            remotefiles.add(f)

    filestoupload = filesToUpload(remotefiles, localfiles)

    for f in filestoupload:
        if not options.dryrun:
            upload(sftp, f, config)
            print('Uploaded: {0}'.format(f))
        else:
            print('<DRYRUN> Uploaded: {0}'.format(f))
    if not filestoupload:
        print('No new files to upload')

    sftp.close()
