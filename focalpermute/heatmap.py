'''produce facetgrid heatmap'''
#region imports
#standard
import itertools

#custom
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import xlwings

#region Mine
import mediandistance
#endregion
#endregion


_KEEP = {'crispDirected_crispMine':'Crisp vs crisp', 
         'focalDirected_focalMine':'Focal vs focal', 
         'crispDirected_focalMine':'Crisp dir. vs Focal this', 
         'focalDirected_crispMine':'Focal dir. vs crisp this'}


#region Get Data
def _get_fmm_data():
    '''(void)-> DataFrame
    Returns dataframe with all FMM frequency data in narrow format
    '''
    results = mediandistance._make_matrices()
    fmm_freq = pd.DataFrame(columns=('group', 'directed', 'this', 'frequency'))
    for d in results['fmm_freq']:
        if d in _KEEP.keys(): #filter out selfies
            fmm_freq = pd.concat([fmm_freq, results['fmm_freq'][d]])
    
    for d in _KEEP:
        qry= {d:_KEEP[d]}
        fmm_freq['group'].replace(qry, inplace=True)
    return fmm_freq


def _get_pam_data():
    '''(void)-> DataFrame
    Returns dataframe with all PAM frequency data in narrow format
    '''
    results = mediandistance._make_matrices()
    for d in results['fmm_pam']:
        pam_freq = pd.concat(pam_freq, d)
    return pam_freq
#endregion

def facet_heatmap(data, **kws):
    '''setup facet grid
    '''
    data = data.pivot(index="directed", columns='this', values='frequency')
    data = data[data.columns].astype(float)
    sns.heatmap(data, cmap='Blues', annot=True, linewidths=0.1, yticklabels=['0','1','2','3','4'], xticklabels=['0','1','2','3','4'], fmt='.0f', **kws)  # <-- Pass kwargs to heatmap


_DATA_FMM = _get_fmm_data()

with sns.plotting_context(font_scale=5.5):
    g = sns.FacetGrid(_DATA_FMM, col='group', col_wrap=2, size=3, aspect=1)

cbar_ax = g.fig.add_axes([.92, .3, .02, .4])  # <-- Create a colorbar axes

g = g.map_dataframe(facet_heatmap, cbar_ax=cbar_ax, vmin=0)  # <-- Specify the colorbar axes and limits

g.set_titles(col_template="{col_name}", fontweight='bold', fontsize=18)
g.fig.subplots_adjust(right=.9)  # <-- Add space so the colorbar doesn't overlap the plot
plt.show()