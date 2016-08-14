#pylint: disable=unused-import, multiple-statements, dangerous-default-value
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
import statsmodels.stats.inter_rater as ir
import scipy.stats as stats
import xlwings #dont delete this - call it from immediate sometimes
#endregion


#region mine
from enum import Enum
from funclib.baselib import switch
import funclib.iolib as iolib
import funclib.statslib as statslib
import funclib.arraylib as arraylib
import funclib.stringslib as stringslib

#endregion
#endregion


#region Globals
_PATH = 'C:/development/python/focalpermute/data'
_EXCEL_DATA_PATH = r'C:\development\python\focalpermute\data\pam_fmm_for_plots.xlsx'
_OUTPATH = r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\My Papers\WalesRSA-MSP\matplotlib'
_MATRICES = collection(dict)
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

class EnumResultsType(Enum):
    '''specify data we want'''
    freq = 1
    distance = 2
    contingency = 3

class EnumKeys(Enum):
    '''matrix type'''
    crispDirected_crispMine = 0
    focalDirected_focalMine = 1
    crispDirected_focalMine = 2
    focalDirected_crispMine = 3
    focalDirected_crispDirected = 4
    focalMine_crispMine = 5

class EnumDataFormat(Enum):
    '''data format to specify returned data in some functions
    '''
    wide = 1 #also called unstacked
    narrow = 2 #also called stacked
    cross_matrix = 3
#endregion




#region Init data
def get_pickled_data(survey=EnumSurvey.fmm, spatial=EnumSpatial.crisp, data=EnumData.directed):
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
                a = a[1:57, 1:70] #fix array size to match other fmm arrays
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
                a = a[1:78, 1:119] #fix array size to match other fmm arrays
            else:
                a = np.load(_PATH + '/' + 'NP_PAM_VENUE_FOCAL.np').astype(float) #PAM FOCAL MINE

    return a


def bin_and_merge_excel_data():
    '''() -> numpy
    Returns the entire dataset in a single dataframe
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


#region Core Functions
def get_matrix_data(datatype=EnumResultsType.freq, survey=EnumSurvey.fmm, results_key=EnumKeys.crispDirected_crispMine):
    '''(enum, enum,enum)->ndarray or dataframe
    return data from the main matrix as defined by the enums
    '''

    topkey = ''
    pairwise_key = ''
    hkey = []
    
    for case in switch(results_key):
        if case(EnumKeys.crispDirected_crispMine):
            pairwise_key = 'crispDirected_crispMine'
            break
        if case(EnumKeys.crispDirected_focalMine):
            pairwise_key = 'crispDirected_focalMine'
            break
        if case(EnumKeys.focalDirected_crispDirected):
            pairwise_key = 'focalDirected_crispDirected'
            break
        if case(EnumKeys.focalDirected_crispMine):
            pairwise_key = 'focalDirected_crispMine'
            break
        if case(EnumKeys.focalDirected_focalMine):
            pairwise_key = 'focalDirected_focalMine'
            break
        if case(EnumKeys.focalMine_crispMine):
            pairwise_key = 'focalMine_crispMine'
            break
        if case():
            raise ValueError('Switch value case not found')

    for case in switch(survey):
        if case(EnumSurvey.fmm):
            hkey.append('fmm_')
            break
        if case(EnumSurvey.pam):
            hkey.append('pam_')
            break
        if case():
            raise ValueError('Switch value case not found')

    for case in switch(datatype):
        if case(EnumResultsType.contingency):
            hkey.append('contingency')
            break
        if case(EnumResultsType.distance):
            hkey.append('distance')
            break
        if case(EnumResultsType.freq):
            hkey.append('freq')
            break
        if case():
            raise ValueError('Switch value case not found')

    topkey = ''.join(hkey)
    return _MATRICES[topkey][pairwise_key]


def make_matrices():
    '''() -> dic
    creates the quartile matrices for all combinations of
    directed and my survey data

    It returns a dictionary of dictionaries with the distance matrices (ie quantile deviation counts)
    of tpye ndarray
    fmm_distance, pam_distance

    and the frequencies in quantile classes between the two quartile matrices: This is a dataframe
    fmm_freq, pam_freq

    and the contingency tables used for interrater analysis (kappas)
    fmm_cont, pam_cont

    Low level keys are to the underlying ndarrays:
    FMM
    crispDirected_crispMine
    focalDirected_focalMine
    crispDirected_focalMine
    focalDirected_crispMine
    focalDirected_crispDirected
    focalMine_crispMine

    PAM
    crispDirected_crispMine
    focalDirected_focalMine
    crispDirected_focalMine
    focalDirected_crispMine
    focalDirected_crispDirected
    focalMine_crispMine

    So dic['fmm_freq']['crispDirected_crispMine'] is ndarray of freq
    '''

    def get_contingency(df_freq, include_zero=True):
        '''(dataframe, bool)->ndarray
        Takes frequency dataframe and creates a contingency table
        which is used as the basic matrix for kappa inter-rater calculations
        The contingency table is an ndarray.

        Include zero will leave in the 0 column and row.
        
        This routine is used to build up contingency tables for
        the global dictionary _MATRICES
        '''
        df = df_freq.copy()
        assert isinstance(df, pd.DataFrame)
        df = df.pivot(index='this', columns='directed', values='frequency')
        df = df[df.columns].astype(float)
        out = df.as_matrix([x for x in df.columns])
        if not include_zero: out = out[1:, 1:]
        out = arraylib.np_nans_to_zero(out)
        return out


    #region Nested Functions
    def class_frequency(a, b, fmt=EnumDataFormat.narrow, drop_nans=True, **kwargs):
        '''(ndarray, ndarray, Enum, str) -> pandas.dataframe
        Takes arrays a and b (expected to be integer arrays) and
        calulates the frequency of corresponding values so:
        a=[1,2,3]
        b=[1,2,3]
        [['1,1',1]
        ['2,2',1]
        ['3,3',1]]

        It then returns the frequency of the items in a cross matrix 
        format or narrow format.

        Note that the wide format is not yet supported.

        CROSS MATRIX FORMAT
        In the matrix format rows correspond to array a, cols to row b.
        Label is ignored when cross matrix is used.

        NARROW FORMAT
        If kwargs contains label, then this will be used to label entries
        in a new pandas column called 'group'.
        Columns are 'group', 'a', 'b', 'value' if label != ''
        Columns are 'a', 'b', 'value' if label == ''

        KWARGS (only used for narrow format)
        label: group label for narrow format
        cola: label used for first column name
        colb: label used for second column name
        col_value:label used for value
        '''


        def create_freq_dataframe(freq_counts):
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


        if fmt == EnumDataFormat.wide:
            raise ValueError('Wide data format not supported yet')

        assert isinstance(a, np.ndarray)
        assert isinstance(b, np.ndarray)

        x = a.copy().astype(str)
        y = b.copy().astype(str)

        cola = kwargs.get('cola') 
        if cola  is None: cola = 'a'

        colb = kwargs.get('colb') 
        if colb is None: colb = 'b'

        col_value = kwargs.get('col_value') 
        if col_value is None: col_value = 'value'

        label = kwargs.get('label')

        z = np.char.add(np.char.add(x, [',']), y)
        freq = arraylib.np_frequencies(z) # [[val1 freq1],[val2 freq2] ...]
            

        if fmt == EnumDataFormat.cross_matrix:
            df = create_freq_dataframe(freq) #row, col
        elif fmt == EnumDataFormat.narrow:
            if label is None:
                df = pd.DataFrame(columns=(cola, colb, col_value))
            else:
                df = pd.DataFrame(columns=('group', cola, colb, col_value))
        else:
            raise ValueError('Unsupported data format specified.')
        row = ''
        col = ''
        for coords, n in freq:
            row, col = coords.split(',')
            if fmt == EnumDataFormat.cross_matrix:
                df[col][row] = n #dataframe is col row, preallocated dataframe size
            else:
                if not drop_nans or (drop_nans and (col + row).lower().find('nan') == -1):
                    if label is None:
                        build_row = [row, col, n]
                    else:
                        build_row = [label, row, col, n]
                    df.loc[len(df)] = build_row #dataframe rows added dynamically

        return df


    def check_array(a, b):
        '''(ndarray,ndarray)
        perform array checks raising error if problem
        '''
        if a.shape != b.shape:
            raise ValueError('Array shapes did not match.')


    def bin_array_quartile(nd, quantile=None):
        '''(ndarray) -> ndarray
        puts array values into quartile bins, leaving zeros as zero
        '''
        if quantile is None: quantile = [25, 50, 75] 
        a = np.copy(nd)
        return statslib.quantile_bin(a, quantile, zero_as_zero=True)
    #endregion


    results = collection(dict)
    fmm_distance = {}
    pam_distance = {}

    fmm_freq = {}
    pam_freq = {}
    
    fmm_contingency = {}
    pam_contingency = {}

    tertile = [float(100)/3, float(200)/3] #pam crisp my data has no 1st and 2nd quantiles the same.

    #FMM
    a = bin_array_quartile(get_pickled_data(EnumSurvey.fmm, EnumSpatial.crisp, EnumData.directed))
    b = bin_array_quartile(get_pickled_data(EnumSurvey.fmm, EnumSpatial.crisp, EnumData.mine))
    check_array(a, b)
    fmm_distance['crispDirected_crispMine'] = arraylib.np_difference(a, b)
    fmm_freq['crispDirected_crispMine'] = class_frequency(a, b, 
                    cola='directed', colb='this', col_value='frequency', label='crispDirected_crispMine'
                    )
    fmm_contingency['crispDirected_crispMine'] = get_contingency(fmm_freq['crispDirected_crispMine'], True)


    a = bin_array_quartile(get_pickled_data(EnumSurvey.fmm, EnumSpatial.focal, EnumData.directed))
    b = bin_array_quartile(get_pickled_data(EnumSurvey.fmm, EnumSpatial.focal, EnumData.mine))
    check_array(a, b)
    fmm_distance['focalDirected_focalMine'] = arraylib.np_difference(a, b)
    fmm_freq['focalDirected_focalMine'] = class_frequency(a, b,
                    cola='directed', colb='this', col_value='frequency', label='focalDirected_focalMine'
                    )
    fmm_contingency['focalDirected_focalMine'] = get_contingency(fmm_freq['focalDirected_focalMine'], True)


    a = bin_array_quartile(get_pickled_data(EnumSurvey.fmm, EnumSpatial.crisp, EnumData.directed))
    b = bin_array_quartile(get_pickled_data(EnumSurvey.fmm, EnumSpatial.focal, EnumData.mine))
    check_array(a, b)
    fmm_distance['crispDirected_focalMine'] = arraylib.np_difference(a, b)
    fmm_freq['crispDirected_focalMine'] = class_frequency(a, b,
                    cola='directed', colb='this', col_value='frequency', label='crispDirected_focalMine'
                    )
    fmm_contingency['crispDirected_focalMine'] = get_contingency(fmm_freq['crispDirected_focalMine'], True)


    a = bin_array_quartile(get_pickled_data(EnumSurvey.fmm, EnumSpatial.focal, EnumData.directed))
    b = bin_array_quartile(get_pickled_data(EnumSurvey.fmm, EnumSpatial.crisp, EnumData.mine))
    check_array(a, b)
    fmm_distance['focalDirected_crispMine'] = arraylib.np_difference(a, b)
    fmm_freq['focalDirected_crispMine'] = class_frequency(a, b,
                    cola='directed', colb='this', col_value='frequency', label='focalDirected_crispMine'
                    )
    fmm_contingency['focalDirected_crispMine'] = get_contingency(fmm_freq['focalDirected_crispMine'], True)


    a = bin_array_quartile(get_pickled_data(EnumSurvey.fmm, EnumSpatial.focal, EnumData.directed))
    b = bin_array_quartile(get_pickled_data(EnumSurvey.fmm, EnumSpatial.crisp, EnumData.directed))
    check_array(a, b)
    fmm_distance['focalDirected_crispDirected'] = arraylib.np_difference(a, b)
    fmm_freq['focalDirected_crispDirected'] = class_frequency(a, b,
                    cola='directed', colb='this', col_value='frequency', label='focalDirected_crispDirected'
                    )
    fmm_contingency['focalDirected_crispDirected'] = get_contingency(fmm_freq['focalDirected_crispDirected'], True)


    a = bin_array_quartile(get_pickled_data(EnumSurvey.fmm, EnumSpatial.focal, EnumData.mine))
    b = bin_array_quartile(get_pickled_data(EnumSurvey.fmm, EnumSpatial.crisp, EnumData.mine))
    check_array(a, b)
    fmm_distance['focalMine_crispMine'] = arraylib.np_difference(a, b)
    fmm_freq['focalMine_crispMine'] = class_frequency(a, b,
                    cola='directed', colb='this', col_value='frequency', label='focalMine_crispMine'
                    )
    fmm_contingency['focalMine_crispMine'] = get_contingency(fmm_freq['focalMine_crispMine'], True)


    results['fmm_distance'] = fmm_distance
    results['fmm_freq'] = fmm_freq
    results['fmm_contingency'] = fmm_contingency

    #PAM 
    a = bin_array_quartile(get_pickled_data(EnumSurvey.pam, EnumSpatial.crisp, EnumData.directed), tertile) #Tertile as not enough of my crisp classes
    b = bin_array_quartile(get_pickled_data(EnumSurvey.pam, EnumSpatial.crisp, EnumData.mine), tertile)
    check_array(a, b)
    pam_distance['crispDirected_crispMine'] = arraylib.np_difference(a, b)
    pam_freq['crispDirected_crispMine'] = class_frequency(a, b,
                    cola='directed', colb='this', col_value='frequency', label='crispDirected_crispMine'
                    )
    pam_contingency['crispDirected_crispMine'] = get_contingency(pam_freq['crispDirected_crispMine'], True)


    a = bin_array_quartile(get_pickled_data(EnumSurvey.pam, EnumSpatial.focal, EnumData.directed))
    b = bin_array_quartile(get_pickled_data(EnumSurvey.pam, EnumSpatial.focal, EnumData.mine))
    check_array(a, b)
    pam_distance['focalDirected_focalMine'] = arraylib.np_difference(a, b)
    pam_freq['focalDirected_focalMine'] = class_frequency(a, b,
                    cola='directed', colb='this', col_value='frequency', label='focalDirected_focalMine'
                    )
    pam_contingency['focalDirected_focalMine'] = get_contingency(pam_freq['focalDirected_focalMine'], True)


    a = bin_array_quartile(get_pickled_data(EnumSurvey.pam, EnumSpatial.crisp, EnumData.directed))
    b = bin_array_quartile(get_pickled_data(EnumSurvey.pam, EnumSpatial.focal, EnumData.mine))
    check_array(a, b)
    pam_distance['crispDirected_focalMine'] = arraylib.np_difference(a, b)
    pam_freq['crispDirected_focalMine'] = class_frequency(a, b,
                    cola='directed', colb='this', col_value='frequency', label='crispDirected_focalMine'
                    )
    pam_contingency['crispDirected_focalMine'] = get_contingency(pam_freq['crispDirected_focalMine'], True)


    #use tertile for pam crisp mine otherwise quantile gives blank for 2nd quantile
    a = bin_array_quartile(get_pickled_data(EnumSurvey.pam, EnumSpatial.focal, EnumData.directed), tertile)
    b = bin_array_quartile(get_pickled_data(EnumSurvey.pam, EnumSpatial.crisp, EnumData.mine), tertile)
    check_array(a, b)
    pam_distance['focalDirected_crispMine'] = arraylib.np_difference(a, b)
    pam_freq['focalDirected_crispMine'] = class_frequency(a, b,
                    cola='directed', colb='this', col_value='frequency', label='focalDirected_crispMine'
                    )
    pam_contingency['focalDirected_crispMine'] = get_contingency(pam_freq['focalDirected_crispMine'], True)


    a = bin_array_quartile(get_pickled_data(EnumSurvey.pam, EnumSpatial.focal, EnumData.directed))
    b = bin_array_quartile(get_pickled_data(EnumSurvey.pam, EnumSpatial.crisp, EnumData.directed))
    check_array(a, b)
    pam_distance['focalDirected_crispDirected'] = arraylib.np_difference(a, b)
    pam_freq['focalDirected_crispDirected'] = class_frequency(a, b,
                    cola='directed', colb='this', col_value='frequency', label='focalDirected_crispDirected'
                    )
    pam_contingency['focalDirected_crispDirected'] = get_contingency(pam_freq['focalDirected_crispDirected'], True)


    a = bin_array_quartile(get_pickled_data(EnumSurvey.pam, EnumSpatial.focal, EnumData.mine), tertile)
    b = bin_array_quartile(get_pickled_data(EnumSurvey.pam, EnumSpatial.crisp, EnumData.mine), tertile)
    check_array(a, b)
    pam_distance['focalMine_crispMine'] = arraylib.np_difference(a, b)
    pam_freq['focalMine_crispMine'] = class_frequency(a, b,
                    cola='directed', colb='this', col_value='frequency', label='focalMine_crispMine'
                    )
    pam_contingency['focalMine_crispMine'] = get_contingency(pam_freq['focalMine_crispMine'], True)


    results['pam_distance'] = pam_distance
    results['pam_freq'] = pam_freq
    results['pam_contingency'] = pam_contingency
    return results


def kappas():
    '''()->void
    writes out kappas for median differences

    fmm_freq, pam_freq
    Low level keys are to the underlying ndarrays:
    crispDirected_crispMine
    focalDirected_focalMine
    '''

    def trim_zeros(a):
        '''(ndarray)->ndarray
        ugly fix to trim zero row and column from contingency ndarrays
        since refactoring code
        '''
        return a[1:, 1:]

    res = []
    
    #FMM
    res.append('FMM FREQ - crispDirected_crispMine - Has Zero')
    data = get_matrix_data(EnumResultsType.contingency, EnumSurvey.fmm, EnumKeys.crispDirected_crispMine)
    res.append(str(ir.cohens_kappa(data, wt='linear', return_results=True)))
    
    res.append('FMM FREQ - crispDirected_crispMine - No Zero')
    data = trim_zeros(get_matrix_data(EnumResultsType.contingency, EnumSurvey.fmm, EnumKeys.crispDirected_crispMine))
    res.append(str(ir.cohens_kappa(data, wt='linear', return_results=True)))

    res.append('FMM FREQ - focalDirected_focalMine - Has Zero')
    data = get_matrix_data(EnumResultsType.contingency, EnumSurvey.fmm, EnumKeys.focalDirected_focalMine)
    res.append(str(ir.cohens_kappa(data, wt='linear', return_results=True)))

    res.append('FMM FREQ - focalDirected_focalMine - No Zero')
    data = trim_zeros(get_matrix_data(EnumResultsType.contingency, EnumSurvey.fmm, EnumKeys.focalDirected_focalMine))
    res.append(str(ir.cohens_kappa(data, wt='linear', return_results=True)))


    #PAM
    res.append('PAM FREQ - crispDirected_crispMine - Has Zero')
    data = get_matrix_data(EnumResultsType.contingency, EnumSurvey.pam, EnumKeys.crispDirected_crispMine)
    res.append(str(ir.cohens_kappa(data, wt='linear', return_results=True)))

    res.append('PAM FREQ - crispDirected_crispMine - No Zero')
    data = trim_zeros(get_matrix_data(EnumResultsType.contingency, EnumSurvey.pam, EnumKeys.crispDirected_crispMine))
    res.append(str(ir.cohens_kappa(data, wt='linear', return_results=True)))

    res.append('PAM FREQ - focalDirected_focalMine - Has Zero')
    data = get_matrix_data(EnumResultsType.contingency, EnumSurvey.pam, EnumKeys.focalDirected_focalMine)
    res.append(str(ir.cohens_kappa(data, wt='linear', return_results=True)))

    res.append('PAM FREQ - focalDirected_focalMine - No Zero')
    data = trim_zeros(get_matrix_data(EnumResultsType.contingency, EnumSurvey.pam, EnumKeys.focalDirected_focalMine))
    res.append(str(ir.cohens_kappa(data, wt='linear', return_results=True)))

    iolib.write_to_file(res, prefix='Kappa', open_in_npp=True)
#endregion



#Tier-0
_MATRICES = make_matrices()
#endregion
