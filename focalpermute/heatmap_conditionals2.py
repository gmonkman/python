# pylint: disable=too-few-public-methods,too-many-statements, unused-import, unused-variable, no-member, dangerous-default-value, invalid-name
'''produce heatmap from the conditionals'''
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
import matplotlib as mpl
from matplotlib import ticker
import matplotlib.gridspec as gridspec

#region Mine
import mediandistance as md
import funclib.statslib as statslib
import funclib.arraylib as arraylib
import plotlib.seabornlib as seabornlib
from funclib.stringslib import add_right
from enum import Enum
#endregion
#endregion


#region Global declarations
_RESULTS_PATH = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/WalesRSA-MSP/matplotlib'
#endregion


def save_plot(fname, dpi=300):
    '''(str)->void
    Save plot with fname name.
    The file extension should dictate the file type.
    '''
    s = add_right(_RESULTS_PATH) + fname
    plt.savefig(s, bbox_inches='tight', pad_inches=0.0, dpi=dpi) #save removing white space around the figure


def process_array(a):
    '''(ndarray)->ndarray, ndarray, ndarray, dic
    processing prior to display

    we want conditional grid probs. by row - ie by directed data
    we want the marginals by column, ie my data as marginals by directed data are all equal because of median
    we want the row marginals to break down into frequency of zeros vs. everything else

    [conditionals, marginals by row, marginals by column, {'zero':x 'nonzero':y}]
    '''


    def zeros(a):
        '''(iterable)->dic {'zero':zero cnt, 'nonzero':nonzero cnt}
        '''
        if isinstance(a, np.ndarray):
            b = a.flatten()
        else:
            b = np.array(arraylib.list_flatten(a))
        assert isinstance(b, np.ndarray)
            
        zero = b[-1]
        nonzero = sum(float(x) for x in b)
        nonzero -= zero
        zero = (zero/(nonzero+zero))*100
        nonzero = 100 - zero
        return {'zero':zero, 'nonzero':nonzero}


    b = a.T #Directed is now on the Y axis
    b = b[::-1] #reverse array

    #Now
    # 0 1 2 3 4 Mine
    #4          
    #3          
    #2          
    #1          
    #0          
    #Dir

    x = statslib.contingency_conditional(b, bycol=True)
    empty, col_marg, empty1 = arraylib.np_conditional_array_split(x, has_by_column=True, has_by_row=False)
    y = statslib.contingency_conditional(b, bycol=False)
    conditionals, empty, row_marg = arraylib.np_conditional_array_split(y, has_by_column=False, has_by_row=True)
    zero_proportions = zeros(row_marg)                         
    return conditionals, row_marg, col_marg, zero_proportions

sns.set(font_scale=1, style='whitegrid')

zero_y = 0.08
zero_x = 0.2
ticks4 = ['4', '3', '2', '1', '0']
ticks3 = ['3', '2', '1', '0']
cmap = mpl.colors.ListedColormap(['#999999', '#EEEEEE'])
heatmapconfig_main = {'annot':False, 'linewidths':0.01, 'linecolor':'#000000', 'fmt':'0.2f'}
heatmapconfig_marg = {'annot':False, 'linewidths':0.01, 'linecolor':'#000000', 'fmt':'0.2f'}
pal = seabornlib.cubhelix_cmap(reverse=True)

plt.close('all')


fig, a = plt.subplots()
assert isinstance(fig, plt.Figure)
fig.set_size_inches(1, 1)


#region fmm_crisp
nd_data = md.get_matrix_data(md.EnumResultsType.contingency, md.EnumSurvey.fmm, md.EnumKeys.crispDirected_crispMine)
conditionals, row_marg, col_marg, zero = process_array(nd_data)

#conditionals has directed by rows (i.e. on y axis), as independent need to transpose so it is on the x
A = np.flip(np.transpose(conditionals[4:]),0)
B = np.flip(np.transpose(conditionals[3:4]),0)
C = np.flip(np.transpose(conditionals[2:3]),0)
D = np.flip(np.transpose(conditionals[1:2]),0)
E = np.flip(np.transpose(conditionals[0:1]),0)
conditionals = np.hstack([A,B,C,D,E])

ax = sns.heatmap(conditionals, annot=heatmapconfig_main['annot'], linewidths=heatmapconfig_main['linewidths'], linecolor=heatmapconfig_main['linecolor'], fmt=heatmapconfig_main['fmt'], robust=True, cmap=pal, square=True, yticklabels=[], xticklabels=[], cbar=False)
save_plot('heatmap_fmm_crisp.tif')
plt.show()
plt.close('all')
#endregion


fig, a = plt.subplots()
assert isinstance(fig, plt.Figure)
fig.set_size_inches(1, 1)


#region fmm_focal
nd_data = md.get_matrix_data(md.EnumResultsType.contingency, md.EnumSurvey.fmm, md.EnumKeys.focalDirected_focalMine)
conditionals, row_marg, col_marg, zero = process_array(nd_data)
conditionals = conditionals[0:5,1:6]    #BUG problem somewhere, process_array adding a row of nans, and col of zeros, so slice it out
#conditionals has directed by rows (i.e. on y axis), as independent need to transpose so it is on the x
A = np.flip(np.transpose(conditionals[4:]),0)
B = np.flip(np.transpose(conditionals[3:4]),0)
C = np.flip(np.transpose(conditionals[2:3]),0)
D = np.flip(np.transpose(conditionals[1:2]),0)
E = np.flip(np.transpose(conditionals[0:1]),0)
conditionals = np.hstack([A,B,C,D,E])

ax = sns.heatmap(conditionals, annot=heatmapconfig_main['annot'], linewidths=heatmapconfig_main['linewidths'], linecolor=heatmapconfig_main['linecolor'], fmt=heatmapconfig_main['fmt'], robust=True, cmap=pal, square=True, yticklabels=[], xticklabels=[], cbar=False)
save_plot('heatmap_fmm_focal.tif')
plt.show()
plt.close('all')
#endregion


fig, a = plt.subplots()
assert isinstance(fig, plt.Figure)
fig.set_size_inches(1, 1)


#region pam_crisp
nd_data = md.get_matrix_data(md.EnumResultsType.contingency, md.EnumSurvey.pam, md.EnumKeys.crispDirected_crispMine)
conditionals, row_marg, col_marg, zero = process_array(nd_data)

#conditionals has directed by rows (i.e. on y axis), as independent need to transpose so it is on the x
A = np.flip(np.transpose(conditionals[3:4]),0)
B = np.flip(np.transpose(conditionals[2:3]),0)
C = np.flip(np.transpose(conditionals[1:2]),0)
D = np.flip(np.transpose(conditionals[0:1]),0)
conditionals = np.hstack([A,B,C,D])

ax = sns.heatmap(conditionals, annot=heatmapconfig_main['annot'], linewidths=heatmapconfig_main['linewidths'], linecolor=heatmapconfig_main['linecolor'], fmt=heatmapconfig_main['fmt'], robust=True, cmap=pal, square=True, yticklabels=[], xticklabels=[], cbar=False)
save_plot('heatmap_pam_crisp.tif')
plt.show()
plt.close('all')
#endregion


fig, a = plt.subplots()
assert isinstance(fig, plt.Figure)
fig.set_size_inches(1, 1)


#region pam_focal
nd_data = md.get_matrix_data(md.EnumResultsType.contingency, md.EnumSurvey.pam, md.EnumKeys.focalDirected_focalMine)
conditionals, row_marg, col_marg, zero = process_array(nd_data)

#conditionals has directed by rows (i.e. on y axis), as independent need to transpose so it is on the x
A = np.flip(np.transpose(conditionals[4:]),0)
B = np.flip(np.transpose(conditionals[3:4]),0)
C = np.flip(np.transpose(conditionals[2:3]),0)
D = np.flip(np.transpose(conditionals[1:2]),0)
E = np.flip(np.transpose(conditionals[0:1]),0)
conditionals = np.hstack([A,B,C,D,E])

ax = sns.heatmap(conditionals, annot=heatmapconfig_main['annot'], linewidths=heatmapconfig_main['linewidths'], linecolor=heatmapconfig_main['linecolor'], fmt=heatmapconfig_main['fmt'], robust=True, cmap=pal, square=True, yticklabels=[], xticklabels=[], cbar=False)
save_plot('heatmap_pam_focal.tif')
plt.show()
plt.close('all')
#endregion
