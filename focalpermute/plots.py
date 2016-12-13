#pylint: skip-file
'''Produce graphs for paper'''
from __future__ import print_function
from __future__ import absolute_import
#region Imports
#region base
import math
#endregion

#region custom
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib as mpl
import numpy
import pandas


import seaborn as sns

import xlwings #dont delete this - call it from immediate sometimes
#endregion

#region mine
from enum import Enum
import funclib.iolib as iolib
import funclib.statslib as statslib
import funclib.arraylib as arraylib
import funclib.stringslib as stringslib
from . import focalpermute as fp
#endregion

#endregion




#region Globals
_PATH = r'C:\development\python\focalpermute\data\cleaned'
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
    hdrs = ['survey', 'spatial_method', 'venue', 'survey_value'] #not used, but

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
    hdrs = ['survey', 'spatial_method', 'venue', 'survey_value'] #not used, but
    dic = get_paired_data(EnumSurvey.fmm, EnumSpatial.crisp)
    mine = dic['mine']
    y = dic['directed']
    survey = numpy.array(['fmm']*len(mine))
    spatial_method = numpy.array(['crisp']*len(mine))
    df_fmm = pandas.DataFrame({hdrs[0]:survey, hdrs[1]:spatial_method, hdrs[2]:mine, hdrs[3]:y})

    dic = get_paired_data(EnumSurvey.pam, EnumSpatial.crisp)
    mine = dic['mine']
    y = dic['directed']
    survey = numpy.array(['pam']*len(mine))
    spatial_method = numpy.array(['crisp']*len(mine))
    df_crisp = pandas.concat([df_fmm, pandas.DataFrame({hdrs[0]:survey, hdrs[1]:spatial_method, hdrs[2]:mine, hdrs[3]:y})])
    return df_crisp
#endregion

def get_all_data_from_excel():
    '''() -> pandas.DataFrame
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
    df_fmm_crisp['venue_binned'] = statslib.quantile_bin(df_fmm_crisp['venue'] , bins, True)
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



#region Show Graphs
def plot_crisp():
    df_all = get_all_data_from_excel()
    df_crisp = df_all.query('spatial_method=="crisp"')

    #crisp
    ax = sns.boxplot(x='venue', y='y_winsorize', hue='survey', data=df_crisp, linewidth=1.1,
                            palette={'fmm': '#FFFFFF', 'pam': '#E7E7E7'})

    #region Axis
    plt.xlabel('Venue density km' + r'$^-$' + r'$^2$')
    plt.ylabel('Directed survey intensity')
    plt.ylim(0,35)

    ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.tick_params(axis='both', which='major', direction='out', length=5)
    sns.despine(top=True, right=True)
    #endregion

    #region Legend
    leg = plt.legend()
    leg.remove()
    #endregion

    #region plotsize
    fig.set_size_inches(8, 5, forward=True)
    #endregion

def plot_focal():
    df_all = get_all_data_from_excel()
    df_focal = df_all.query('spatial_method=="focal"')
    
    fig, (ax1, ax2) = plt.subplots(1,2, sharex=True, figsize=(6,8))
    
    ax = sns.jointplot(x="venue", y="y_log10", data=df_focal, kind="hex")

    #jg = sns.JointGrid(x="venue", y="y_log10", data=df_focal, space=0, dropna=True, ylim=(0,2), xlim=(0,5.5))
    #scatter = jg.plot_joint(plt.scatter, s=40, edgecolor='white', color='#1F1F1F', linewidth=1)
    #marginal = jg.plot_marginals(sns.distplot, kde=False, color='#1F1F1F')
    #marginal = jg.plot_marginals(sns.kdeplot, shade=True, color='#1F1F1F')
    
    #regionAxis format
    #scatter.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    #scatter.tick_params(axis='both', which='major', direction='out', length=5)
    
    ax.set_axis_labels('Venue density km' + r'$^-$' + r'$^2$', 'Directed survey intensity')
    ax.ax_joint
    #sns.set_size_inches(8, 5, forward=True)
    sns.despine(top=True, right=True)

    print(type(ax))
 #endregion


def quantile():
    df_all = get_all_data_from_excel()
    df_focal_fmm = df_all.query('spatial_method=="focal" and survey=="fmm" and y>0 and venue>0')
    df_focal_pam = df_all.query('spatial_method=="focal" and survey=="pam" and y>0 and venue>0')
    df_fmm = df_all.query('spatial_method != "focal" and survey=="fmm" and y>0 and venue>0')
    df_pam = df_all.query('spatial_method != "focal" and survey=="pam" and y>0 and venue>0')
    df_all_no_zero = df_all.query('y>0 and venue>0')

    mod = smf.quantreg('venue_log10 ~ y_log10', df_focal_fmm)
    res = mod.fit(q=0.5)
    print(res.summary())



#fig = plt.figure(figsize=(1, 4))
#ax = fig.add_axes([0.09, 0.06, 0.2, 0.84])
#cmap = mpl.colors.ListedColormap(['#555555','#999999'])
#bounds = [0.00001, 50,100]
#norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
#cb2 = mpl.colorbar.ColorbarBase(ax, cmap=cmap, norm=norm, spacing='proportional', orientation='vertical')
#ax.text(0.2,0.9,'Test', fontsize=12, transform=ax.transAxes, rotation=90)

#plt.show()



