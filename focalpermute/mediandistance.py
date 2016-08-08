#pylint: disable=unused-import
'''Calculate the all median distances'''

#region Imports
#region base
import math
from collections import defaultdict as collection
#endregion

#region custom
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import numpy as np
import pandas as pd
import xlwings #dont delete this - call it from immediate sometimes
#endregion

#region mine
from enum import Enum
import funclib.iolib as iolib
import funclib.statslib as statslib
import funclib.arraylib as arraylib
import funclib.stringslib as stringslib
#endregion
#endregion


#region Globals
_PATH = './data'
_EXCEL_DATA_PATH = r'C:\development\python\focalpermute\data\pam_fmm_for_plots.xlsx'
_OUTPATH = r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\My Papers\WalesRSA-MSP\matplotlib'
#endregion




#region class enums
class EnumSurvey(Enum):
    '''enum used to select survey type - PAM or FMM'''
    pam = 1
    fmm = 2

class EnumSpatial(Enum):
    '''is it focal or crisp'''
    crisp = 1
    focal = 2


class EnumData(Enum):
    ''' my data or directed survey data'''
    mine = 1
    directed = 2
#endregion



#region Init data
def get_data(survey=EnumSurvey.fmm, spatial=EnumSpatial.crisp, data=EnumData.directed):
    '''(EnumSurvey, EnumSpatial) -> ndarray
    Load data previously exported as numpy arrays
    from arcgis for both FMM and PAM data.
    '''

    if survey == EnumSurvey.fmm:
        if spatial == EnumSpatial.crisp:
            if data == EnumData.directed:
                a = np.load(_PATH + '/NP_FMM_VALUE.np').astype(float) #FMM CRISP DIRECTED
            else:
                a = np.load(_PATH + '/NP_FMM_VENUE.np').astype(float) #FMM CRISP MINE
                a = a[0:56, 0:69]
        else:
            if data == EnumData.directed:
                a = np.load(_PATH + '/np_fmm_value_focal.np').astype(float) #FMM FOCAL DIRECTED
                a = a[1:57,1:70] #fix array size to match other fmm arrays
            else:
                a = np.load(_PATH + '/NP_FMM_VENUE_FOCAL.np').astype(float) #FMM FOCAL MINE
                a = np.delete(a, 69, 1)
    else:
        if spatial == EnumSpatial.crisp:
            if data == EnumData.directed:
                a = np.load(_PATH + '/' + 'NP_PAM_DAYSPAKM.np').astype(float) #PAM CRISP DIRECTED
            else:
                a = np.load(_PATH + '/' + 'PAMSansPAMVCntRaster.np').astype(float) #PAM CRISP MINE
        else:
            if data == EnumData.directed:
                a = np.load(_PATH + '/' + 'np_pam_dayspa_focal.np').astype(float) #PAM FOCAL DIRECTED
                a = a[1:78,1:119] #fix array size to match other fmm arrays
            else:
                a = np.load(_PATH + '/' + 'NP_PAM_VENUE_FOCAL.np').astype(float) #PAM FOCAL MINE

    return a


def _bin_excel_data():
    '''() -> numpy
    Returns the entire datasetin a single dataframe
    from previously exported excel dataset
    Includes column with 3.29 winsorized values by the
    4 stratifications fmm-focal fmm-crisp pam-focal pam-crisp
    '''
    bins = [25, 50, 75]
    df = pd.read_excel(_EXCEL_DATA_PATH)
    assert isinstance(df, pd.DataFrame)
    
    #venue
    df_fmm_crisp = df.query('spatial_method=="crisp" and survey=="fmm"').copy()
    df_fmm_crisp['venue_binned'] = statslib.quantile_bin(df_fmm_crisp['venue'], bins, True)
    df_fmm_crisp['survey_value_binned'] = statslib.quantile_bin(df_fmm_crisp['survey_value'], bins, True)

    df_fmm_focal = df.query('spatial_method=="focal" and survey=="fmm"').copy()
    df_fmm_focal['venue_binned'] = statslib.quantile_bin(df_fmm_focal['venue'], bins, True)
    df_fmm_focal['survey_value_binned'] = statslib.quantile_bin(df_fmm_focal['survey_value'], bins, True)

    df_pam_crisp = df.query('spatial_method=="crisp" and survey=="pam"').copy()
    df_pam_crisp['venue_binned'] = statslib.quantile_bin(df_pam_crisp['venue'], bins, True)
    df_pam_crisp['survey_value_binned'] = statslib.quantile_bin(df_pam_crisp['survey_value'], bins, True)

    df_pam_focal = df.query('spatial_method=="focal" and survey=="pam"').copy()
    df_pam_focal['venue_binned'] = statslib.quantile_bin(df_pam_focal['venue'], bins, True)
    df_pam_focal['survey_value_binned'] = statslib.quantile_bin(df_pam_focal['survey_value'], bins, True)

    df_binned = pd.concat([df_fmm_crisp, df_fmm_focal, df_pam_crisp, df_pam_focal])

    return df_binned
#endregion




def _bin_array_quartile(nd):
    '''(ndarray) -> ndarray
    puts array values into quartile bins, leaving zeros as zero
    nd is 'byref'
    '''
    a = np.copy(nd)
    return statslib.quantile_bin(a, [(float(1)/3)*100, (float(2)/3)*100], zero_as_zero=True)


def _difference(a, b):
    '''(ndarray, ndarray) -> ndarray
    get absolute difference between two matrices.
    Effectively one from the other then abs it.
    '''
    x = np.copy(a)
    y = np.copy(b)
    return np.abs(x - y)


def _check_array(a, b):
    '''(ndarray,ndarray)
    perform array checks raising error if problem
    '''
    if a.shape != b.shape:
        raise ValueError('Array shapes did not match.')


def _make_matrices():
    results = collection(dict)
    fmm_distance = {}
    pam_distance = {}

    fmm_freq = {}
    pam_freq = {}
    
    #FMM
    a = _bin_array_quartile(get_data(EnumSurvey.fmm, EnumSpatial.crisp, EnumData.directed))
    b = _bin_array_quartile(get_data(EnumSurvey.fmm, EnumSpatial.crisp, EnumData.mine))
    _check_array(a, b)
    fmm_distance['crispDirected_crispMine'] = _difference(a, b)
    fmm_freq['crispDirected_crispMine'] = _class_frequency(a, b) #directed should be rows
    
    a = _bin_array_quartile(get_data(EnumSurvey.fmm, EnumSpatial.focal, EnumData.directed))
    b = _bin_array_quartile(get_data(EnumSurvey.fmm, EnumSpatial.focal, EnumData.mine))
    _check_array(a, b)
    fmm_distance['focalDirected_focalMine'] = _difference(a, b)
    fmm_freq['focalDirected_focalMine'] = _class_frequency(a, b)

    a = _bin_array_quartile(get_data(EnumSurvey.fmm, EnumSpatial.crisp, EnumData.directed))
    b = _bin_array_quartile(get_data(EnumSurvey.fmm, EnumSpatial.focal, EnumData.mine))
    _check_array(a, b)
    fmm_distance['crispDirected_focalMine'] = _difference(a, b)
    fmm_freq['crispDirected_focalMine'] = _class_frequency(a, b)

    a = _bin_array_quartile(get_data(EnumSurvey.fmm, EnumSpatial.focal, EnumData.directed))
    b = _bin_array_quartile(get_data(EnumSurvey.fmm, EnumSpatial.crisp, EnumData.mine))
    _check_array(a, b)
    fmm_distance['focalDirected_crispMine'] = _difference(a, b)
    fmm_freq['focalDirected_crispMine'] = _class_frequency(a, b)

    a = _bin_array_quartile(get_data(EnumSurvey.fmm, EnumSpatial.focal, EnumData.directed))
    b = _bin_array_quartile(get_data(EnumSurvey.fmm, EnumSpatial.crisp, EnumData.directed))
    _check_array(a, b)
    fmm_distance['focalDirected_crispDirected'] = _difference(a, b)
    fmm_freq['focalDirected_crispDirected'] = _class_frequency(a, b)

    a = _bin_array_quartile(get_data(EnumSurvey.fmm, EnumSpatial.focal, EnumData.mine))
    b = _bin_array_quartile(get_data(EnumSurvey.fmm, EnumSpatial.crisp, EnumData.mine))
    _check_array(a, b)
    fmm_distance['focalMine_crispMine'] = _difference(a, b)
    fmm_freq['focalMine_crispMine'] = _class_frequency(a, b)

    results['fmm_distance'] = fmm_distance
    results['fmm_freq'] = fmm_freq

    #PAM 
    a = _bin_array_quartile(get_data(EnumSurvey.pam, EnumSpatial.crisp, EnumData.directed))
    b = _bin_array_quartile(get_data(EnumSurvey.pam, EnumSpatial.crisp, EnumData.mine))
    _check_array(a, b)
    pam_distance['crispDirected_crispMine'] = _difference(a, b)
    pam_freq['crispDirected_crispMine'] = _class_frequency(a, b)

    a = _bin_array_quartile(get_data(EnumSurvey.pam, EnumSpatial.focal, EnumData.directed))
    b = _bin_array_quartile(get_data(EnumSurvey.pam, EnumSpatial.focal, EnumData.mine))
    _check_array(a, b)
    pam_distance['focalDirected_focalMine'] = _difference(a, b)
    pam_freq['focalDirected_focalMine'] = _class_frequency(a, b)

    a = _bin_array_quartile(get_data(EnumSurvey.pam, EnumSpatial.crisp, EnumData.directed))
    b = _bin_array_quartile(get_data(EnumSurvey.pam, EnumSpatial.focal, EnumData.mine))
    _check_array(a, b)
    pam_distance['crispDirected_focalMine'] = _difference(a, b)
    pam_freq['crispDirected_focalMine'] = _class_frequency(a, b)

    a = _bin_array_quartile(get_data(EnumSurvey.pam, EnumSpatial.focal, EnumData.directed))
    b = _bin_array_quartile(get_data(EnumSurvey.pam, EnumSpatial.crisp, EnumData.mine))
    _check_array(a, b)
    pam_distance['focalDirected_crispMine'] = _difference(a, b)
    pam_freq['focalDirected_crispMine'] = _class_frequency(a, b)

    a = _bin_array_quartile(get_data(EnumSurvey.pam, EnumSpatial.focal, EnumData.directed))
    b = _bin_array_quartile(get_data(EnumSurvey.pam, EnumSpatial.crisp, EnumData.directed))
    _check_array(a, b)
    pam_distance['focalDirected_crispDirected'] = _difference(a, b)
    pam_freq['focalDirected_crispDirected'] = _class_frequency(a, b)

    a = _bin_array_quartile(get_data(EnumSurvey.pam, EnumSpatial.focal, EnumData.mine))
    b = _bin_array_quartile(get_data(EnumSurvey.pam, EnumSpatial.crisp, EnumData.mine))
    _check_array(a, b)
    pam_distance['focalMine_crispMine'] = _difference(a, b)
    pam_freq['focalMine_crispMine'] = _class_frequency(a, b)

    results['pam_distance'] = pam_distance
    results['pam_freq'] = pam_freq
    return results


def _class_frequency(a, b):
    '''(ndarray, ndarray) -> pandas.dataframe, pandas.dataframe
    Takes arrays a and b (expected to be integer arrays) and
    calulates the frequency of corresponding values so:
    a=[1,2,3]
    b=[1,2,3]
    [['1,1',1]
    ['2,2',1]
    ['3,3',1]]

    It then returns two pandas dataframes, the first is the frequency of the items
    
    Rows correspond to array a, cols to row b.
    '''
    assert isinstance(a, np.ndarray)
    assert isinstance(b, np.ndarray)

    x = a.copy().astype(str)
    y = b.copy().astype(str)

    z = np.char.add(np.char.add(x, [',']), y)
    freq = arraylib.np_frequencies(z) # [[val1 freq1],[val2 freq2] ...]

    df = _create_freq_dataframe(freq) #row, col

    for coords, n in freq:
        row, col = coords.split(',')
        df[col][row] = n #dataframe is col row

    return df


def _create_freq_dataframe(freq_counts):
    '''(ndarray)->dataframe
    takes an ndarray of frequency counts and creates empty dataframe
    to populate with frequency values for further processing.

    Example of freq_counts:
    [['0.0,0.0', '124'],
    ['0.0,1.0', '29'],
    ['0.0,2.0', '6'],
    ['0.0,3.0', '2'],
    ['0.0,4.0', '2']]
    '''
    v = []
    for coords, freq in freq_counts:
        x, y = coords.split(',')
        v.append(x)
        v.append(y)

    a = np.unique(np.array(v))
    df = pd.DataFrame(index=a, columns=a) #row, col
    return df


def get_results():
    '''top level call to distance
    '''
    matrices = _make_matrices()
    z = 2
    #stuff to calculate
    #average deviations for each median value
    #Get data ready for graphing differences
    #You can do stats on the differences if want
