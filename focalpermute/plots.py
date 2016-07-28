'''Produce graphs for paper'''

#custom
import math
import numpy
import pandas
import scipy.stats
import xlwings #dont delete this - call it from immediate sometimes

#mine
from enum import Enum
import funclib.iolib as iolib
import funclib.statslib as statslib
import funclib.arraylib as arraylib
import funclib.stringslib as stringslib
import focalpermute as fp


_PATH = r'C:\development\python\focalpermute\data\cleaned'


#region class enums
class EnumSurvey(Enum):
    '''enum used to select survey type - PAM or FMM'''
    pam = 1
    fmm = 2

class EnumSpatial(Enum):
    '''is it focal or crisp'''
    crisp = 1
    focal = 2
#endregion




def get_paired_data(survey=EnumSurvey.fmm, spatial=EnumSpatial.crisp):
    '''(EnumSurvey, EnumSpatial) -> dic {'mine', 'directed'}
    load arrays for test, all with zeros

    Havent bothered with No0 as wont use these in graph
    '''
    a = numpy.array([])
    b = numpy.array([])
    if survey == EnumSurvey.fmm:
        if spatial ==  EnumSpatial.crisp: #FMM Crisp
            a = numpy.load(_PATH + r'\nd_fmm_venue_0_cleaned.np')
            b = numpy.load(_PATH + r'\nd_fmm_value_0_cleaned.np')
            if a.shape != b.shape:
                raise ValueError('array shape mismatch')
        else: #FMM Focal
            a = numpy.load(_PATH + r'\nd_fmm_venue_focal_0_cleaned.np')
            b = numpy.load(_PATH + r'\nd_fmm_value_focal_0_cleaned.np')
            if a.shape != b.shape:
                raise ValueError('array shape mismatch')
    else:
        if spatial == EnumSpatial.crisp: #PAM Crisp
            a = numpy.load(_PATH + r'\nd_pam_venue_0_cleaned.np')
            b = numpy.load(_PATH + r'\nd_pam_dayspa_0_cleaned.np')
            if a.shape != b.shape:
                raise ValueError('array shape mismatch')
        else: #PAM Focal
            a = numpy.load(_PATH + r'\nd_pam_venue_focal_0_cleaned.np')
            b = numpy.load(_PATH + r'\nd_pam_dayspa_focal_0_cleaned.np')
            if a.shape != b.shape:
                raise ValueError('array shape mismatch')
                
    return {'mine':a, 'directed':b}


#focal combined because y is 
def get_focal_dataframe():
    '''() -> pandas.DataFrame'''
    hdrs = ['survey', 'spatial_method', 'venue', 'y'] #not used, but

    dic = get_paired_data(EnumSurvey.fmm, EnumSpatial.focal)
    mine = dic['mine']
    y = dic['directed']
    survey = numpy.array(['fmm']*len(mine))
    spatial_method = numpy.array(['focal']*len(mine))
    df_fmm = pandas.DataFrame({hdrs[0]:survey, hdrs[1]:spatial_method, hdrs[2]:mine, hdrs[3]:y})

    dic = get_paired_data(EnumSurvey.pam, EnumSpatial.focal)
    mine = dic['mine']
    y = dic['directed']
    survey = numpy.array(['pam']*len(mine))
    spatial_method = numpy.array(['focal']*len(mine))
    df_focal = pandas.concat([df_fmm, pandas.DataFrame({hdrs[0]:survey, hdrs[1]:spatial_method, hdrs[2]:mine, hdrs[3]:y})])
    return df_focal

#crisp combined because y is ordinal
def get_crisp_dataframe():
    '''() -> pandas.DataFrame'''
    hdrs = ['survey', 'spatial_method', 'venue', 'y'] #not used, but
    dic = get_paired_data(EnumSurvey.fmm, EnumSpatial.crisp)
    mine = dic['mine']
    y = dic['directed']
    survey = numpy.array(['fmm']*len(mine))
    spatial_method = numpy.array(['crisp']*len(mine))
    df_pam = pandas.DataFrame({hdrs[0]:survey, hdrs[1]:spatial_method, hdrs[2]:mine, hdrs[3]:y})

    dic = get_paired_data(EnumSurvey.pam, EnumSpatial.crisp)
    mine = dic['mine']
    y = dic['directed']
    survey = numpy.array(['pam']*len(mine))
    spatial_method = numpy.array(['crisp']*len(mine))
    df_pam = pandas.concat([df_pam, pandas.DataFrame({hdrs[0]:survey, hdrs[1]:spatial_method, hdrs[2]:mine, hdrs[3]:y})])
    return df_pam
#endregion