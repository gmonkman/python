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


def plot():
    '''plot heatmaps
    '''
    sns.set(font_scale=1, style='whitegrid')

    zero_y = 0.08
    zero_x = 0.2
    ticks4 = ['4', '3', '2', '1', '0']
    ticks3 = ['3', '2', '1', '0']
    cmap = mpl.colors.ListedColormap(['#999999', '#EEEEEE'])
    heatmapconfig_main = {'annot':True, 'linewidths':0.02, 'linecolor':'#111111', 'fmt':'0.2f'}
    heatmapconfig_marg = {'annot':True, 'linewidths':0.02, 'linecolor':'#111111', 'fmt':'0.2f'}
    pal = seabornlib.cubhelix_cmap(reverse=True)

    def save_plot(fname):
        '''(str)->void
        Save plot with fname name.
        The file extension should dictate the file type.
        '''
        s = add_right(_RESULTS_PATH) + fname
        plt.savefig(s, bbox_inches='tight', dpi=300)
    

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


    plt.close('all')

    fig = plt.figure(figsize=(12, 12))

    outer_grid = gridspec.GridSpec(2, 2)
    top_left_cell = outer_grid[0, 0]
    top_right_cell = outer_grid[0, 1]
    bottom_left_cell = outer_grid[1, 0]
    bottom_right_cell = outer_grid[1, 1]

    tlc_inner = gridspec.GridSpecFromSubplotSpec(2, 3, top_left_cell, hspace=0.1, height_ratios=[5, 1], width_ratios=[10, 1.6, 0.75])
    trc_inner = gridspec.GridSpecFromSubplotSpec(2, 3, top_right_cell, hspace=0.1, height_ratios=[5, 1], width_ratios=[10, 1.6, 0.75])
    blc_inner = gridspec.GridSpecFromSubplotSpec(2, 3, bottom_left_cell, hspace=0.1, height_ratios=[5, 1], width_ratios=[8, 1.6, 0.75])
    brc_inner = gridspec.GridSpecFromSubplotSpec(2, 3, bottom_right_cell, hspace=0.1, height_ratios=[5, 1], width_ratios=[10, 1.6, 0.75])

    #region Top Left
    nd_data = md.get_matrix_data(md.EnumResultsType.contingency, md.EnumSurvey.fmm, md.EnumKeys.crispDirected_crispMine)
    conditionals, row_marg, col_marg, zero = process_array(nd_data)
    ax00_0 = plt.subplot(tlc_inner[0, 0:2])
    ax00_1 = plt.subplot(tlc_inner[1, 0])

    ax = sns.heatmap(conditionals, annot=heatmapconfig_main['annot'], linewidths=heatmapconfig_main['linewidths'], linecolor=heatmapconfig_main['linecolor'], fmt=heatmapconfig_main['fmt'], robust=True, cmap=pal, square=True, yticklabels=ticks4, cbar=True, ax=ax00_0)
    ax.set(ylabel='Quartile (directed)')
    ax = sns.heatmap(col_marg, annot=heatmapconfig_main['annot'], linewidths=heatmapconfig_main['linewidths'], linecolor=heatmapconfig_main['linecolor'], fmt=heatmapconfig_main['fmt'], robust=True, cmap=pal, square=True, cbar=False, ax=ax00_1)
    ax.set(xlabel='Quartile (this)')

    ax00_zeros = plt.subplot(tlc_inner[0, 2])
    bounds = [0.00001, zero['zero'], 100]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    cb = mpl.colorbar.ColorbarBase(ax00_zeros, cmap=cmap, norm=norm, spacing='proportional', orientation='vertical')
    ax00_zeros.text(zero_x, 0.95, 'Non-zero', fontsize=12, transform=ax00_zeros.transAxes, rotation=90)
    ax00_zeros.text(zero_x, zero_y, 'zero', fontsize=12, transform=ax00_zeros.transAxes, rotation=90)
    ax00_1.text(-0.1, 0.5, 'Marginals', fontsize=11, transform=ax00_1.transAxes, rotation=90, horizontalalignment='left', verticalalignment='center')

    for label in cb.ax.xaxis.get_ticklabels(): label.set_visible(False)
    
    ax00_0.set_title('FMM crisp vs. crisp')
    ax00_0.axes.get_xaxis().set_ticks([]) #always turn off
    ax00_1.axes.get_yaxis().set_ticks([])
    #endregion


    #region Top Right
    nd_data = md.get_matrix_data(md.EnumResultsType.contingency, md.EnumSurvey.fmm, md.EnumKeys.focalDirected_focalMine)
    conditionals, row_marg, col_marg, zero = process_array(nd_data)
    ax01_0 = plt.subplot(trc_inner[0, 0:2])
    ax01_1 = plt.subplot(trc_inner[1, 0])
    ax01_zeros = plt.subplot(trc_inner[0, 2])
    sns.heatmap(conditionals, annot=heatmapconfig_main['annot'], linewidths=heatmapconfig_main['linewidths'], linecolor=heatmapconfig_main['linecolor'], fmt=heatmapconfig_main['fmt'], robust=True, cmap=pal, yticklabels=ticks4, square=True, ax=ax01_0)
    ax = sns.heatmap(col_marg, annot=heatmapconfig_main['annot'], linewidths=heatmapconfig_main['linewidths'], linecolor=heatmapconfig_main['linecolor'], fmt=heatmapconfig_main['fmt'], square=True, robust=True, cmap=pal, cbar=False, ax=ax01_1)
    ax.set(xlabel='Quartile (this)')

    ax01_zeros = plt.subplot(trc_inner[0, 2]) #zerosubplot
    bounds = [0.00001, zero['zero'], 100]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    cb = mpl.colorbar.ColorbarBase(ax01_zeros, cmap=cmap, norm=norm, spacing='proportional', orientation='vertical')
    ax01_zeros.text(zero_x, 0.95, 'Non-zero', fontsize=12, transform=ax01_zeros.transAxes, rotation=90)
    ax01_zeros.text(zero_x, zero_y, 'zero', fontsize=12, transform=ax01_zeros.transAxes, rotation=90)

    ax01_0.set_title('FMM focal vs. focal')
    ax01_0.axes.get_xaxis().set_ticks([]) #always turn off
    ax01_1.axes.get_yaxis().set_ticks([])
    #endregion


    #region Bottom Left
    nd_data = md.get_matrix_data(md.EnumResultsType.contingency, md.EnumSurvey.pam, md.EnumKeys.crispDirected_crispMine)
    conditionals, row_marg, col_marg, zero = process_array(nd_data)
    ax10_0 = plt.subplot(blc_inner[0, 0:2])
    ax10_1 = plt.subplot(blc_inner[1, 0])
    ax10_zeros = plt.subplot(blc_inner[0, 2])

    ax = sns.heatmap(conditionals, annot=heatmapconfig_main['annot'], linewidths=heatmapconfig_main['linewidths'], linecolor=heatmapconfig_main['linecolor'], fmt=heatmapconfig_main['fmt'], robust=True, cmap=pal, yticklabels=ticks3, square=True, ax=ax10_0)
    ax.set(ylabel='Tertile (directed)')
    ax = sns.heatmap(col_marg, annot=heatmapconfig_main['annot'], linewidths=heatmapconfig_main['linewidths'], linecolor=heatmapconfig_main['linecolor'], fmt=heatmapconfig_main['fmt'], cmap=pal, square=True, cbar=False, ax=ax10_1)
    ax.set(xlabel='Tertile (this)')
    
    ax10_zeros = plt.subplot(blc_inner[0, 2]) #zerosubplot
    bounds = [0.00001, zero['zero'], 100]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    cb = mpl.colorbar.ColorbarBase(ax10_zeros, cmap=cmap, norm=norm, spacing='proportional', orientation='vertical')
    ax10_zeros.text(zero_x, 0.95, 'Non-zero', fontsize=12, transform=ax10_zeros.transAxes, rotation=90)
    ax10_zeros.text(zero_x, zero_y, 'zero', fontsize=12, transform=ax10_zeros.transAxes, rotation=90)
    ax10_1.text(-0.1, 0.5, 'Marginals', fontsize=11, transform=ax10_1.transAxes, rotation=90, horizontalalignment='left', verticalalignment='center')

    ax10_0.set_title('PAM crisp vs. crisp')
    ax10_0.axes.get_xaxis().set_ticks([])
    ax10_1.axes.get_yaxis().set_ticks([])
    #endregion


    #region Bottom Right
    nd_data = md.get_matrix_data(md.EnumResultsType.contingency, md.EnumSurvey.pam, md.EnumKeys.focalDirected_focalMine)
    conditionals, row_marg, col_marg, zero = process_array(nd_data)
    ax11_0 = plt.subplot(brc_inner[0, 0:2])
    ax11_1 = plt.subplot(brc_inner[1, 0])
    ax11_zeros = plt.subplot(brc_inner[0, 2])
    ax = sns.heatmap(conditionals, annot=heatmapconfig_main['annot'], linewidths=heatmapconfig_main['linewidths'], linecolor=heatmapconfig_main['linecolor'], fmt=heatmapconfig_main['fmt'], robust=True, cmap=pal, square=True, yticklabels=ticks4, ax=ax11_0)
    ax = sns.heatmap(col_marg, annot=heatmapconfig_main['annot'], linewidths=heatmapconfig_main['linewidths'], linecolor=heatmapconfig_main['linecolor'], fmt=heatmapconfig_main['fmt'], cmap=pal, square=True, cbar=False, ax=ax11_1)
    ax.set(xlabel='Quartile (this)')

    ax11_zeros = plt.subplot(brc_inner[0, 2]) #zerosubplot
    bounds = [0.00001, zero['zero'], 100]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    cb = mpl.colorbar.ColorbarBase(ax11_zeros, cmap=cmap, norm=norm, spacing='proportional', orientation='vertical')
    ax11_zeros.text(zero_x, 0.95, 'Non-zero', fontsize=12, transform=ax11_zeros.transAxes, rotation=90)
    ax11_zeros.text(zero_x, zero_y, 'zero', fontsize=12, transform=ax11_zeros.transAxes, rotation=90)

    ax11_0.set_title('PAM focal vs. focal')
    ax11_0.axes.get_xaxis().set_ticks([])  #always turn off
    #ax11_0.axes.get_yaxis().set_ticks([])
    ax11_1.axes.get_yaxis().set_ticks([])
    #endregion

    save_plot('heatmap_conditionals.png')
    plt.show()




plot()
