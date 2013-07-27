# -*- coding: utf-8 -*-
"""
Created on Mon May  6 19:54:26 2013

@author: balarsen
"""
import re


def determineFileType(filename):
    """
    given a filename figure out what type of file this is
    """
    # use an Re to match the filename convention and return one of
    ## 'configfile', 'mbpfile', 'contextfile', 'hiresfile' or ValueError
    if re.match(r'^.*Context(_L1)?\.txt$', filename):
        return 'contextfile'
    elif re.match(r'^.*Config(_L1)?\.txt$', filename):
        return 'configfile'
    elif re.match(r'^.*Burst(_L1)?\.txt$', filename):
        return 'mbpfile'
    elif re.match(r'^.*HiRes(_L1)?\.txt$', filename):
        return 'hiresfile'
    elif re.match(r'^.*DataTimes(_L1)?\.txt$', filename):
        return 'datatimes'
    else:
        raise(ValueError('No Match'))



