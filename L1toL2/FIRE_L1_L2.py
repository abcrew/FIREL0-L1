# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 12:03:07 2014

@author: abcrew
"""

import numpy as np
import spacepy.datamodel as dm
import spacepy.time as spt
import spacepy.toolbox as tb
import datetime
import glob
from copy import deepcopy

test_ephem = '/Users/abcrew/Desktop/FU-2/MagEphem/20131208_FU-2-1min_MagEphem.txt'
test_hires = '/Users/abcrew/Desktop/FB_data/Flight/2014-01-22-HiRes_L1.txt'
test_context = '/Users/abcrew/Desktop/FB_data/2014-02-01-Context_L1.txt'

"""
Process L1->L2
Steps:
    1) Figure out what type of data file it is
    2) Trim it down to a smaller size-->only the points from the correct day
    3) Build a new data structure [Is there an easy way to do this?]
    4) Step through data file and select appropriate ephem values
        a) Initially find nearest value
        b) Later want to do a linear interpolation
    5) Run through the data and flag 'questionable point'
    6) Write a new file (meta data?)
"""

"""
Fields that I want:
    Rgeod_LatLon [2 elements]
    Rgeod_Height
    CDMAG_MLAT
    CDMAG_MLON
    CDMAG_MLT
    Kp
    Dst
    FieldLineType
    S_sc_to_pfn
    S_sc_to_pfs
    S_pfs_to_Bmin
    S_Bmin_to_sc
    S_total
    d2B_ds2
    Sb0
    RadiusOfCurv
    Loss_Cone_Alpha_n
    Loss_Cone_Alpha_s
    Lsimple
    InvLat
    Lm_eq
    InvLat_eq
    BoverBeq
    MlatFromBoverBeq
"""

"""
Constants of note:
    Detector 0 is Collimated (Context->Channel 6: >1MeV)
    Detector 1 is Surface (Context-> Channel 5: ~775keV)
    Center Energies:
        240, 329, 457, 639, 890, >1033keV [Collimated]
        202, 280, 392, 552, 772, >900keV [Surface]
    Nominal Geometric Factor (analytic-> need to revise):
        23, 9, cm^2 sr
        
    
"""

ephem_list = ['Rgeod_Height', 'Rgeod_Height', 'CDMAG_MLAT', 'CDMAG_MLON', 'CDMAG_MLT', 'Kp', 'Dst',
              'S_sc_to_pfn', 'S_sc_to_pfs', 'S_pfs_to_Bmin', 'S_Bmin_to_sc',
              'S_total', 'd2B_ds2', 'Sb0', 'RadiusOfCurv', 'Loss_Cone_Alpha_n', 'Loss_Cone_Alpha_s',
              'Lsimple', 'InvLat', 'Lm_eq', 'InvLat_eq', 'BoverBeq', 'MlatFromBoverBeq']

test_ephem_list = ['Rgeod_LatLon', 'Bsc_gsm', 'Rgeod_Height', 
                   'Rgeod_Height', 'CDMAG_MLAT', 'CDMAG_MLON', 'CDMAG_MLT', 'Kp', 'Dst',
              'S_sc_to_pfn', 'S_sc_to_pfs', 'S_pfs_to_Bmin', 'S_Bmin_to_sc',
              'S_total', 'd2B_ds2', 'Sb0', 'RadiusOfCurv', 'Loss_Cone_Alpha_n', 'Loss_Cone_Alpha_s',
              'Lsimple', 'InvLat', 'Lm_eq', 'InvLat_eq', 'BoverBeq', 'MlatFromBoverBeq', 'Pfn_geo', 'Pfs_geo',
              'Pmin_gsm', 'Bmin_gsm']

"""
Handles the overall package for turning L1->L2 files
    1) Determine file type
    2) Call appropriate function
"""

def FIRE_L1_L2(datafile, ephemfile):
    ftype = Determine_file_type(datafile)
    if ftype < 1:
        print 'Invalid Datafile'
        return 0
    if ftype == 1:
        data = FIRE_Context_L1_L2(datafile, ephemfile)
    if ftype == 2:
        data = FIRE_HiRes_L1_L2(datafile, ephemfile)
    return data
    
"""
Turns Hires L1->L2
Only converts L, MLT, Lat, Lon from Ephem
Need to add in the energy/GF conversions to fluxes
e_flux:
    cts/sec*energy/gf
    orig: cts/18.75ms, gf is constant (per detector)
    Want to mix channels (every other so they go by energy)
"""
def FIRE_HiRes_L1_L2(datafile, ephemfile):
    full_data = dm.readJSONheadedASCII(datafile)
    ephem = dm.readJSONheadedASCII(ephemfile)
    data = Trim_data_file(full_data, ephem)
    labels = ephem.keys()
    ephem_fields = ['Lsimple', 'CDMAG_MLT']
    dt = spt.Ticktock(data['Epoch']).TAI
    et = spt.Ticktock(ephem['DateTime']).TAI
    for i in range(len(ephem_fields)):
        print ephem_fields[i]
        y = ephem[ephem_fields[i]]
        nx = tb.interpol(dt, et, y)
        data[ephem_fields[i]] = dm.dmarray(nx)
    ephem_lat = ephem['Rgeod_LatLon'][:,0]
    ephem_lon = ephem['Rgeod_LatLon'][:,1]
    nx = tb.interpol(dt, et, ephem_lat)
    data['Lat'] = dm.dmarray(nx)
    nx = tb.interpol(dt, et, ephem_lon)
    data['Lon'] = dm.dmarray(nx)
    n_lines = len(data['Epoch'])
    eflux = np.zeros(n_lines,12)
    day = ephem['DateTime'][0][0:10]
    outfile = datafile[:-23] + day + '-HiRes_L2.txt'
    dm.toJSONheadedASCII(outfile, data)
    return data

"""
Converts Context to L2
Has all desired Ephem tags (given by "test_ephem_list")
1)  for each ephem field, step through and do interpolation
2)  Properly process the L1 Context data to L2:
    i) Hold onto the L1 values
    ii) Convert into a # flux
    iii) Despike [Remove Beacon/spurious values]
3) Write a new file

Conversion coefficients:
    L1: Counts per 6s
    L2: Energy flux:
        Counts/s*energy/geometric factor
        
    Col: GF: 9cm^2sr, E: 1033keV
    Sur: GF: 23cm^2sr, E: 775keV

"""
def FIRE_Context_L1_L2(datafile, ephemfile):
    full_data = dm.readJSONheadedASCII(datafile)
    ephem = dm.readJSONheadedASCII(ephemfile)
    meta = dm.readJSONheadedASCII(ephemfile)
    data = Trim_data_file(full_data, ephem)
    labels = ephem.keys()
    ephem_fields = test_ephem_list
    dt = spt.Ticktock(data['Epoch']).TAI
    et = spt.Ticktock(ephem['DateTime']).TAI
    for i in range(len(ephem_fields)):
        dim = np.size(ephem[ephem_fields[i]][0])
        print ephem_fields[i], dim
        nx = np.empty([len(dt),dim])
        if dim > 1:
            for j in range(dim):
                y = ephem[ephem_fields[i]][:,j]
                nx[:,j] = tb.interpol(dt, et, y)
            data[ephem_fields[i]] = dm.dmarray(nx, attrs = meta[ephem_fields[i]].attrs)
        else:
            y = ephem[ephem_fields[i]] 
            nx = tb.interpol(dt, et, y)
            data[ephem_fields[i]] = dm.dmarray(nx, attrs = meta[ephem_fields[i]].attrs)
    col = deepcopy(data['Context'][:,0])
    sur = deepcopy(data['Context'][:,1])
    despike(col, 250, 10)
    despike(sur, 250, 10)
    col = (col/(6*9))*1033
    sur = (sur/(6*23))*772
    data['col'] = dm.dmarray(col, attrs = {'Description': 'Collimated Detector Energy Flux', 'SCALE_TYPE': 'log'})
    data['sur'] = dm.dmarray(sur, attrs = {'Description': 'Surface Detector Energy Flux', 'SCALE_TYPE': 'log'})
    day = ephem['DateTime'][0][0:10]
    outfile = datafile[:-25] + day + '-Context_L2.txt'
    order = ['Epoch', 'col', 'sur', 'Context']
#    order = ['Epoch', 'Context']
    order.extend(ephem_fields)
    dm.toJSONheadedASCII(outfile, data)
    return data


"""
Determines the type of Datafile by parsing the last few characters
Assumes that these follow the standard naming conventions from L1
Date_FILETYPE_L1.txt
FILETYPE could be Context, HiRes, Config, or MicroBurst
Right now only work with Context or HiRes 
"""    
def Determine_file_type(datafile):
    l1 = datafile[-6:-4]
    if l1 != 'L1':
        print 'Invalid File Type'
        return 0
    fstring = datafile[-10:-4]
    if fstring == 'ext_L1':
        print 'Context File'
        return 1
    elif fstring == 'Res_L1':
        print 'HiRes File'
        return 2
    else:
        print 'Unknown File'
        return -1
        
"""
Responsible for trimming out the data that is not from the same day as the ephem file
Iterates through all keys for which there are the same number of lines as the time stamp
and trims them down
"""        
def Trim_data_file(data, ephem):
    day = ephem['DateTime'][0][0:10]
    print day
    n_data_lines = len(data['Epoch'])
    mask = np.zeros(n_data_lines, dtype = bool)
    for i in range(n_data_lines):
        if data['Epoch'][i][0:10] == day:
            mask[i] = True
            if i % 100 == 0:
                print i
    print np.sum(mask)
    for key in data.iterkeys():
        if len(data[key]) == n_data_lines:
            print key
            data[key] = data[key][mask]
    n_final_lines = len(data['Epoch'])
    print 'Starting lines', n_data_lines
    print 'Ending lines', n_final_lines
    return data
    
"""
Takes a numpy array of data, and goes through comparing each element to the
one immediately before and after; if it is greater than height times those values
it is replaced by the average of them
    array: input array
    height: scale value not to exceed (i.e. 255)
    floor: to avoid jumps relative to 0,1 this is used as the minimum array value
"""    
def despike(array, height, floor):
    nlines = len(array)
    for i in range(nlines-2)+np.ones(nlines-2):
        if(array[i] > array[i-1]*height and array[i] > array[i+1]*height and array[i]>height*floor):
            array[i] = (array[i+1]+array[i-1])/2
            print 'Adjustment made', i
    