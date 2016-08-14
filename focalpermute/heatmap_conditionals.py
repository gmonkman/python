# pylint: disable=too-few-public-methods,too-many-statements, unused-import, unused-variable, no-member, dangerous-default-value, redefined-variable-type
'''produce heatmap from the conditionals'''
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
import matplotlib.gridspec as gridspec

#region Mine
import mediandistance as md
import funclib.statslib as statslib
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
    sns.set(font_scale=1, style='white')

    def save_plot(fname):
        '''(str)->void
        Save plot with fname name.
        The file extension should dictate the file type.
        '''
        s = add_right(_RESULTS_PATH) + fname
        plt.savefig(s, bbox_inches='tight', dpi=300)
    

    def get_data(a):
        '''(ndarray)->ndarrays
        a is contingency with row and col marginals
        which we need to chop out to plot
        returns [conditionals, bycol_marginals]

        Currently im only passing in arrays with marginals by columns
        '''
        rows = a.shape[0]
        cols = a.shape[1]
        
        conditionals = a[0:int(a.shape[0])-1, 0:int(a.shape[1])]
        bycol_marginals = a[int(a.shape[0])-1:int(a.shape[0]), :]
        return [conditionals, bycol_marginals]

    raise ValueError('Check your marginals they dont look right')

    plt.close('all')

    fig = plt.figure(figsize=(8, 8))

    outer_grid = gridspec.GridSpec(2, 2)
    top_left_cell = outer_grid[0, 0]
    top_right_cell = outer_grid[0, 1]
    bottom_left_cell = outer_grid[1, 0]
    bottom_right_cell = outer_grid[1, 1]

    tlc_inner = gridspec.GridSpecFromSubplotSpec(2, 2, top_left_cell, height_ratios=[5, 1], width_ratios=[13.5, 1])
    trc_inner = gridspec.GridSpecFromSubplotSpec(2, 2, top_right_cell, height_ratios=[5, 1], width_ratios=[13.5, 1])
    blc_inner = gridspec.GridSpecFromSubplotSpec(2, 2, bottom_left_cell, height_ratios=[5, 1], width_ratios=[9, 1])
    brc_inner = gridspec.GridSpecFromSubplotSpec(2, 2, bottom_right_cell, height_ratios=[5, 1], width_ratios=[13.5, 1])

    # From here we can plot using inner_grid's SubplotSpecs
    nd_data = md.get_matrix_data(md.EnumResultsType.contingency, md.EnumSurvey.fmm, md.EnumKeys.crispDirected_crispMine)
    nd_data = statslib.contingency_conditional(nd_data, bycol=True)
    conditionals, col_marg = get_data(nd_data)
    ax00_0 = plt.subplot(tlc_inner[0, :])
    ax00_1 = plt.subplot(tlc_inner[1, 0])
    sns.heatmap(conditionals, annot=False, fmt='0.2f', square=True, cbar=True, ax=ax00_0)
    sns.heatmap(col_marg, annot=True, fmt='0.2f', square=True, cbar=False, ax=ax00_1)
    ax00_0.set_title('FMM crisp vs. crisp')
    #labels
    ax00_0.axes.get_xaxis().set_ticks([]) #always turn off
    ax00_1.axes.get_xaxis().set_ticks([])
    ax00_1.axes.get_yaxis().set_ticks([0.2])
    ax00_1.axes.get_yaxis().set_ticklabels(['Marg.'])


    nd_data = md.get_matrix_data(md.EnumResultsType.contingency, md.EnumSurvey.fmm, md.EnumKeys.focalDirected_focalMine)
    nd_data = statslib.contingency_conditional(nd_data, bycol=True)
    conditionals, col_marg = get_data(nd_data)
    ax01_0 = plt.subplot(trc_inner[0, :])
    ax01_1 = plt.subplot(trc_inner[1, 0])
    sns.heatmap(conditionals, annot=False, fmt='0.2f', square=True, ax=ax01_0)
    sns.heatmap(col_marg, annot=True, fmt='0.2f', square=True, cbar=False, ax=ax01_1)
    ax01_0.set_title('FMM focal vs. focal')
    #labels
    ax01_0.axes.get_xaxis().set_ticks([]) #always turn off
    ax01_0.axes.get_yaxis().set_ticks([])
    ax01_1.axes.get_xaxis().set_ticks([])
    ax01_1.axes.get_yaxis().set_ticks([])


    nd_data = md.get_matrix_data(md.EnumResultsType.contingency, md.EnumSurvey.pam, md.EnumKeys.crispDirected_crispMine)
    nd_data = statslib.contingency_conditional(nd_data, bycol=True)
    conditionals, col_marg = get_data(nd_data)
    ax10_0 = plt.subplot(blc_inner[0, :])
    ax10_1 = plt.subplot(blc_inner[1, 0])
    sns.heatmap(conditionals, annot=False, fmt='0.2f', square=True, ax=ax10_0)
    sns.heatmap(col_marg, annot=True, fmt='0.2f', square=True, cbar=False, ax=ax10_1)
    ax10_0.set_title('PAM crisp vs. crisp')
    #labels
    ax10_0.axes.get_xaxis().set_ticks([]) #always turn off
    ax10_1.axes.get_yaxis().set_ticks([0.2])
    ax10_1.axes.get_yaxis().set_ticklabels(['Marg.'])


    nd_data = md.get_matrix_data(md.EnumResultsType.contingency, md.EnumSurvey.pam, md.EnumKeys.focalDirected_focalMine)
    nd_data = statslib.contingency_conditional(nd_data, bycol=True)
    conditionals, col_marg = get_data(nd_data)
    ax11_0 = plt.subplot(brc_inner[0, :])
    ax11_1 = plt.subplot(brc_inner[1, 0])
    sns.heatmap(conditionals, annot=False, fmt='0.2f', square=True, ax=ax11_0)
    sns.heatmap(col_marg, annot=True, fmt='0.2f', square=True, cbar=False, ax=ax11_1)
    ax11_0.set_title('PAM focal vs. focal')
    #labels
    ax11_0.axes.get_xaxis().set_ticks([])  #always turn off
    ax11_0.axes.get_yaxis().set_ticks([])
    ax11_1.axes.get_yaxis().set_ticks([])

    plt.show()
