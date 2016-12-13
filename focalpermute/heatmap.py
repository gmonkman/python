# pylint: disable=too-few-public-methods,too-many-statements, unused-import, unused-variable, no-member, dangerous-default-value, redefined-variable-type
'''produce facetgrid heatmap'''
from __future__ import absolute_import
#region imports
#standard
import itertools

#custom
import pandas as pd
import numpy as np
import seaborn as sns
import xlwings
import matplotlib.pyplot as plt
from matplotlib import ticker

#region Mine
from . import mediandistance
from funclib.stringslib import add_right
from enum import Enum
#endregion
#endregion




#region Enums
class EnumData(Enum):
    '''fmm or pam
    '''
    fmm = 0
    pam = 1
#endregion




#region Global declarations
_RESULTS_PATH = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/matplotlib'

_KEEP = {'crispDirected_crispMine':'Crisp vs crisp', 
         'focalDirected_focalMine':'Focal vs focal', 
         'crispDirected_focalMine':'Crisp dir. vs focal this', 
         'focalDirected_crispMine':'Focal dir. vs crisp this'}
#endregion




#region Get Data
def _get_fmm_data():
    '''(void)-> DataFrame
    Returns dataframe with all FMM frequency data in narrow format
    '''
    results = mediandistance.make_matrices()
    fmm_freq = pd.DataFrame(columns=('group', 'directed', 'this', 'frequency'))
    for d in results['fmm_freq']:
        if d in _KEEP.keys(): #filter out selfies
            fmm_freq = pd.concat([fmm_freq, results['fmm_freq'][d]])
    
    for d in _KEEP:
        qry = {d:_KEEP[d]}
        fmm_freq['group'].replace(qry, inplace=True)
    return fmm_freq


def _get_pam_data():
    '''(void)-> DataFrame
    Returns dataframe with all PAM frequency data in narrow format
    '''
    results = mediandistance.make_matrices()
    pam_freq = pd.DataFrame(columns=('group', 'directed', 'this', 'frequency'))
    for d in results['pam_freq']:
        if d in _KEEP.keys(): #filter out selfies
            pam_freq = pd.concat([pam_freq, results['pam_freq'][d]])
    
    for d in _KEEP: #change labels to be heatmap title friendly
        qry = {d:_KEEP[d]}
        pam_freq['group'].replace(qry, inplace=True)
    return pam_freq
#endregion




def plot(edata=EnumData.fmm):
    '''(EnumData)->void
    plot all the median frequency graphs
    '''

    def save_plot(fname):
        '''(str)->void
        Save plot with fname name.
        The file extension should dictate the file type.
        '''
        s = add_right(_RESULTS_PATH) + fname
        plt.savefig(s, bbox_inches='tight', dpi=300)


    def facet_heatmap(data, **kws):
        '''setup facet grid
        '''
        assert isinstance(data, pd.DataFrame)
        data = data.pivot(index='this', columns='directed', values='frequency')
        data = data[data.columns].astype(float)
        data = data.reindex(index=data.index[::-1])
        data = data.fillna(0)
        #yticklabels=['0', '1', '2', '3', '4'], xticklabels=['0', '1', '2', '3', '4']

        g = sns.heatmap(data, cmap='Blues', annot=True, linewidths=0.1, fmt='0.0f', **kws)  # <-- Pass kwargs to heatmap
        g.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
        g.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))

    data = _get_fmm_data() if edata == EnumData.fmm else _get_pam_data()

    with sns.plotting_context(font_scale=0):
        g = sns.FacetGrid(data, col='group', col_wrap=2, size=2, aspect=1.2)

    g = (g.map_dataframe(facet_heatmap, vmin=0).set_axis_labels('Quartile (this)', 'Quartile (directed)'))
    #g.fig.subplots_adjust(right=.9)
    g.set_titles(col_template="{col_name}", fontweight='bold', fontsize=12)

    s = 'fmm_median_heatmap.tif' if edata == EnumData.fmm else 'pam_median_heatmap.tif'
    save_plot(s)
    #plt.show()
    



#region Tier 1
plot(EnumData.fmm)
plt.close('all')
plot(EnumData.pam)
#endregion
