#pylint:
'''Calculate the all median distances'''

#region Imports
#region base
import math
#endregion

#region custom
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import numpy
import pandas
import xlwings #dont delete this - call it from immediate sometimes
#endregion

#region mine
from enum import Enum
import funclib.iolib as iolib
import funclib.statslib as statslib
import funclib.arraylib as arraylib
import funclib.stringslib as stringslib
import focalpermute as fp
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
                a = numpy.load(_PATH + '/NP_FMM_VALUE.np').astype(float) #FMM CRISP DIRECTED
            else:
                a = numpy.load(_PATH + '/NP_FMM_VENUE.np').astype(float) #FMM CRISP MINE
                a = a[0:56, 0:69]
        else:
            if data == EnumData.directed:
                a = numpy.load(_PATH + '/np_fmm_value_focal.np').astype(float) #FMM FOCAL DIRECTED
            else:
                a = numpy.load(_PATH + '/NP_FMM_VENUE_FOCAL.np').astype(float) #FMM FOCAL MINE
                a = numpy.delete(a, 69, 1)
    else:
        if spatial == EnumSpatial.crisp:
            if data == EnumData.directed:
                a = numpy.load(_PATH + '/' + 'NP_PAM_DAYSPAKM.np').astype(float) #PAM CRISP DIRECTED
            else:
                a = numpy.load(_PATH + '/' + 'PAMSansPAMVCntRaster.np').astype(float) #PAM CRISP MINE
        else:
            if data == EnumData.directed:
                a = numpy.load(_PATH + '/' + 'np_pam_dayspa_focal.np').astype(float) #PAM FOCAL DIRECTED
            else:
                a = numpy.load(_PATH + '/' + 'NP_PAM_VENUE_FOCAL.np').astype(float) #PAM FOCAL MINE

    return a


def bin_excel_data():
    '''() -> numpy
    Returns the entire datasetin a single dataframe
    from previously exported excel dataset
    Includes column with 3.29 winsorized values by the
    4 stratifications fmm-focal fmm-crisp pam-focal pam-crisp
    '''
    bins = [25, 50, 75]
    df = pandas.read_excel(_EXCEL_DATA_PATH)
    assert isinstance(df, pandas.DataFrame)
    
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

    df_binned = pandas.concat([df_fmm_crisp, df_fmm_focal, df_pam_crisp, df_pam_focal])

    return df_binned
#endregion


def bin_array_quartile(nd):
    '''(ndarray) -> void
    puts array values into quartile bins, leaving zeros as zero
    nd is 'byref'
    '''
    nd = statslib.quantile_bin(nd, [25, 50, 75], zero_as_zero=True)

