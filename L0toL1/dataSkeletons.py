
from spacepy import datamodel as dm


def getSkelHIRES():
    dat = dm.SpaceData()
    dat['Flag'] = dm.dmarray([], dtype=int)
    dat['Flag'].attrs['CATDESC'] = 'Data flags'
    dat['Flag'].attrs['FIELDNAM'] = 'Flag'
    dat['Flag'].attrs['FILL_VALUE'] = -255
    dat['Flag'].attrs['LABLAXIS'] = 'Flag'
    dat['Flag'].attrs['SCALETYP'] = 'linear'
    dat['Flag'].attrs['VALID_MIN'] = -254
    dat['Flag'].attrs['VALID_MAX'] = 0
    dat['Flag'].attrs['VAR_TYPE'] = 'support_data'
    dat['Flag'].attrs['VAR_NOTES'] = 'Data flags, 0-good, -1-suspect time'
    dat['Epoch'] = dm.dmarray([])
    dat['Epoch'].attrs['CATDESC'] = 'Default Time'
    dat['Epoch'].attrs['FIELDNAM'] = 'Epoch'
    #dat['Epoch'].attrs['FILLVAL'] = datetime.datetime(2100,12,31,23,59,59,999000)
    dat['Epoch'].attrs['LABLAXIS'] = 'Epoch'
    dat['Epoch'].attrs['SCALETYP'] = 'linear'
    #dat['Epoch'].attrs['VALIDMIN'] = datetime.datetime(1990,1,1)
    #dat['Epoch'].attrs['VALIDMAX'] = datetime.datetime(2029,12,31,23,59,59,999000)
    dat['Epoch'].attrs['VAR_TYPE'] = 'support_data'
    dat['Epoch'].attrs['TIME_BASE'] = '0 AD'
    dat['Epoch'].attrs['MONOTON'] = 'INCREASE'
    dat['Epoch'].attrs['VAR_NOTES'] = 'Epoch at each hi-res measurement'
    dat['Timestamp'] = dm.dmarray([])
    dat['Timestamp'].attrs['CATDESC'] = 'Default Time'
    dat['Timestamp'].attrs['FIELDNAM'] = 'Timestamp'
    #dat['Timestamp'].attrs['FILLVAL'] = datetime.datetime(2100,12,31,23,59,59,999000)
    dat['Timestamp'].attrs['LABLAXIS'] = 'Timestamp'
    dat['Timestamp'].attrs['SCALETYP'] = 'linear'
    #dat['Timestamp'].attrs['VALIDMIN'] = datetime.datetime(1990,1,1)
    #dat['Timestamp'].attrs['VALIDMAX'] = datetime.datetime(2029,12,31,23,59,59,999000)
    dat['Timestamp'].attrs['VAR_TYPE'] = 'support_data'
    dat['Timestamp'].attrs['TIME_BASE'] = '0 AD'
    dat['Timestamp'].attrs['MONOTON'] = 'INCREASE'
    dat['Timestamp'].attrs['VAR_NOTES'] = 'Timestamp at each hi-res measurement'
    dat['hr0'] = dm.dmarray([], dtype=int)
    dat['hr0'].attrs['CATDESC'] = 'Detector 0 hi-res'
    dat['hr0'].attrs['ELEMENT_LABELS'] = "hr0_0", "hr0_1", "hr0_2", "hr0_3", "hr0_4", "hr0_5",
    dat['hr0'].attrs['ELEMENT_NAMES'] =  "hr0-0", "hr0-1", "hr0-2", "hr0-3", "hr0-4", "hr0-5",
    dat['hr0'].attrs['FILL_VALUE'] = -2**16
    dat['hr0'].attrs['LABEL'] = 'Detector 0 hi-res'
    dat['hr0'].attrs['SCALE_TYPE'] = 'log'
    dat['hr0'].attrs['UNITS'] = 'counts'
    dat['hr0'].attrs['VALID_MIN'] = 0
    dat['hr0'].attrs['VALID_MAX'] = 2**16-1
    dat['hr0'].attrs['VAR_TYPE'] = 'data'
    dat['hr0'].attrs['VAR_NOTES'] = 'hr0 for each channel'
    dat['hr0'].attrs['DEPEND_0'] = 'Epoch'
    dat['hr0'].attrs['DEPEND_1'] = 'Channel'
    dat['hr1'] = dm.dmarray([], dtype=int)
    dat['hr1'].attrs['CATDESC'] = 'Detector 1 hi-res'
    dat['hr1'].attrs['ELEMENT_LABELS'] = "hr1_0", "hr1_1", "hr1_2", "hr1_3", "hr1_4", "hr1_5",
    dat['hr1'].attrs['ELEMENT_NAMES'] =  "hr1-0", "hr1-1", "hr1-2", "hr1-3", "hr1-4", "hr1-5",
    dat['hr1'].attrs['FILL_VALUE'] = -2**16
    dat['hr1'].attrs['LABEL'] = 'Detector 1 hi-res'
    dat['hr1'].attrs['SCALE_TYPE'] = 'log'
    dat['hr1'].attrs['UNITS'] = 'counts'
    dat['hr1'].attrs['VALID_MIN'] = 0
    dat['hr1'].attrs['VALID_MAX'] = 2**16-1
    dat['hr1'].attrs['VAR_TYPE'] = 'data'
    dat['hr1'].attrs['VAR_NOTES'] = 'hr1 for each channel'
    dat['hr1'].attrs['DEPEND_0'] = 'Epoch'
    dat['hr1'].attrs['DEPEND_1'] = 'Channel'
    dat['Channel'] = dm.dmarray(range(6))
    dat['Channel'].attrs['CATDESC'] = 'Channel Number'
    dat['Channel'].attrs['ELEMENT_LABELS'] = "0", "1", "2", "3", "4", "5",
    dat['Channel'].attrs['ELEMENT_NAMES'] =  "0", "1", "2", "3", "4", "5",
    dat['Channel'].attrs['FILL_VALUE'] = -2**16
    dat['Channel'].attrs['LABEL'] = 'Channel'
    dat['Channel'].attrs['SCALE_TYPE'] = 'linear'
    dat['Channel'].attrs['UNITS'] = ''
    dat['Channel'].attrs['VALID_MIN'] = 0
    dat['Channel'].attrs['VALID_MAX'] = 5
    dat['Channel'].attrs['VAR_TYPE'] = 'support_data'
    dat['Channel'].attrs['VAR_NOTES'] = 'channel number'
    dat['seqnum'] = dm.dmarray([], dtype=int)
    dat['seqnum'].attrs['CATDESC'] = 'Sequence number for data'
    dat['seqnum'].attrs['FILL_VALUE'] = -1
    dat['seqnum'].attrs['LABEL'] = 'Data packet sequence number'
    dat['seqnum'].attrs['SCALE_TYPE'] = 'linear'
    dat['seqnum'].attrs['UNITS'] = ''
    dat['seqnum'].attrs['VALID_MIN'] = 0
    dat['seqnum'].attrs['VALID_MAX'] = 2**8
    dat['seqnum'].attrs['VAR_TYPE'] = 'support_data'
    dat['seqnum'].attrs['VAR_NOTES'] = 'seqnum for each data point'
    dat['seqnum'].attrs['DEPEND_0'] = 'Epoch'
    dat['seqidx'] = dm.dmarray([], dtype=int)
    dat['seqidx'].attrs['CATDESC'] = 'Sequence index for data'
    dat['seqidx'].attrs['FILL_VALUE'] = -1
    dat['seqidx'].attrs['LABEL'] = 'Data packet sequence index'
    dat['seqidx'].attrs['SCALE_TYPE'] = 'linear'
    dat['seqidx'].attrs['UNITS'] = ''
    dat['seqidx'].attrs['VALID_MIN'] = 0
    dat['seqidx'].attrs['VALID_MAX'] = 2**8
    dat['seqidx'].attrs['VAR_TYPE'] = 'support_data'
    dat['seqidx'].attrs['VAR_NOTES'] = 'seqidx for each data point'
    dat['seqidx'].attrs['DEPEND_0'] = 'Epoch'
    dat['pktnum'] = dm.dmarray([], dtype=int)
    dat['pktnum'].attrs['CATDESC'] = 'Packet number for data'
    dat['pktnum'].attrs['FILL_VALUE'] = -1
    dat['pktnum'].attrs['LABEL'] = 'TM packet number'
    dat['pktnum'].attrs['SCALE_TYPE'] = 'linear'
    dat['pktnum'].attrs['UNITS'] = ''
    dat['pktnum'].attrs['VALID_MIN'] = 0
    dat['pktnum'].attrs['VALID_MAX'] = 2**8
    dat['pktnum'].attrs['VAR_TYPE'] = 'support_data'
    dat['pktnum'].attrs['VAR_NOTES'] = 'pktnum for each data point'
    dat['pktnum'].attrs['DEPEND_0'] = 'Epoch'
    return dat
