# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
from funclib import pandaslib

grey = ["#EEEEEE", "#E8E8E8", "#E3E3E3", "#DEDEDE", "#D9D9D9", "#D3D3D3", "#CECECE", "#C9C9C9", "#C4C4C4", "#BFBFBF"]
grey = ["#666666"]
sns.set(palette=grey, font='Times New Roman') #, style="ticks"
PLOT_KWARGS = {'aa':True, 'linestyle':'dashed', 'c':'0.7', 'lw':1}
PLOT_REG_KWARGS = {'aa':True, 'linestyle':'solid', 'lw':1}
SCATTER_KWARGS = {'marker':'x', 's':10}
#sns.set_style(rc={"ytick.major.size": 50}

def make_graph_dis_undis(csv, out):
    '''(str, str) -> void
    csv: csv file with data
    out: full filename to save the graph as
    '''
    df = pd.read_csv(csv)
    g = sns.lmplot(x='Actual length', y='Error', data=df, col='Marker', row='Correction', ci=95, x_ci='ci', n_boot=1000, size=2, aspect=1.4, line_kws=PLOT_REG_KWARGS, scatter_kws=SCATTER_KWARGS) #size=1, aspect=1.2
    g.set_axis_labels('Actual length (mm)', 'Error (mm)')

    if 'bass' in csv:
        xlim = (210, 630);ylim = (-150, 70)
        g.set(xlim=xlim, ylim=ylim, xticks=[250, 300, 350, 400, 450, 500, 550, 600], yticks=[-125, -100, -75, -50, -25, 0, 25, 50])
    else: #dab
        xlim=(90, 300); ylim=(-60, 20)
        g.set(xlim=xlim, ylim=ylim)
    ymid = (ylim[0] + ylim[1]) /2

    g.set_titles('{col_name}')
    #g.fig.subplots_adjust(wspace=0.2, hspace=0.4)
    g.fig.tight_layout()
    g.despine()

    #coords are rc
    ax00  = g.facet_axis(0, 0); ax01  = g.facet_axis(0, 1); ax02  = g.facet_axis(0, 2)
    ax10  = g.facet_axis(1, 0); ax11  = g.facet_axis(1, 1); ax12  = g.facet_axis(1, 2)
    facets = [ax00, ax01, ax02, ax10, ax11, ax12]
    ax10.set_title(''); ax11.set_title(''); ax12.set_title('')

    ax02.text(xlim[1], ymid, 'Distorted', ha='center', va='center', rotation=-90)
    ax12.text(xlim[1], ymid, 'Undistorted', ha='center', va='center', rotation=-90)

    for ax in facets:
        ax.plot([min(xlim), max(xlim)], [0, 0], **PLOT_KWARGS)

    plt.savefig(out, dpi=300)
    #plt.show()


def make_graphs_other(csv, out):
    '''(str, str) -> void
    csv: csv file with data
    out: full filename to save the graph as
    '''
    df = pd.read_csv(csv)
    g = sns.lmplot(x='Actual length', y='Error', data=df, col='Marker', row='Correction', ci=95, x_ci='ci', n_boot=1000, size=2, aspect=1.4, line_kws=PLOT_REG_KWARGS, scatter_kws=SCATTER_KWARGS) #size=1, aspect=1.2
    g.set_axis_labels('Actual length (mm)', 'Error (mm)')
    if 'bass' in csv:
        xlim = (210, 630);ylim = (-150, 70)
        g.set(xlim=xlim, ylim=ylim, xticks=[250, 300, 350, 400, 450, 500, 550, 600], yticks=[-125, -100, -75, -50, -25, 0, 25, 50])
    else: #dab
        xlim=(90, 300); ylim=(-60, 20)
        g.set(xlim=xlim, ylim=ylim)
    ymid = (ylim[0] + ylim[1]) /2

    g.set_titles('{col_name}')
    #g.fig.subplots_adjust(wspace=0.2, hspace=0.4)
    g.fig.tight_layout()
    g.despine()

    #coords are rc
    ax00  = g.facet_axis(0, 0); ax01  = g.facet_axis(0, 1)
    ax10  = g.facet_axis(1, 0); ax11  = g.facet_axis(1, 1)
    ax20  = g.facet_axis(2, 0); ax21  = g.facet_axis(2, 1)
    ax30  = g.facet_axis(3, 0); ax31  = g.facet_axis(3, 1)
    ax40  = g.facet_axis(4, 0); ax41  = g.facet_axis(4, 1)
    ax10.set_title('');ax11.set_title('')
    ax20.set_title('');ax21.set_title('')
    ax30.set_title('');ax31.set_title('')
    ax40.set_title('');ax41.set_title('')
    facets = [ax00, ax01, ax10, ax11, ax20, ax21, ax30, ax31, ax40, ax41]
    for ax in facets:
        ax.plot([min(xlim), max(xlim)], [0, 0], **PLOT_KWARGS)

    assert isinstance(ax40, mpl.axes.Subplot)
    ax01.text(xlim[1], ymid, 'Depth', ha='center', va='center', rotation=-90)
    ax11.text(xlim[1], ymid, 'Iterative', ha='center', va='center', rotation=-90)
    ax21.text(xlim[1], ymid, 'Profile', ha='center', va='center', rotation=-90)
    ax31.text(xlim[1], ymid, 'Sensor-profile', ha='center', va='center', rotation=-90)
    ax41.text(xlim[1], ymid, 'Calib.-profile ', ha='center', va='center', rotation=-90)
    plt.savefig(out, dpi=300)
    #plt.show()


if __name__ == "__main__":
    #These are created from SQL Server imagedb project, fid_long_form_all.sql
    #The exported fields and values were manually renamed in the exported data

    #First we create distorted and undistorted for fg, bg and laser. This is because background doesnt have all corrections
    #So we split it up so that the facetgrid doesnt have missing graphs
    print('Bass uncorrected undistorted ....')
    make_graph_dis_undis('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/Fiducial_error_minimisation/seaborn/v_fid_long_form_bass_uncorrected_undistorted.csv', r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\My Papers\Fiducial_error_minimisation\figures\v_fid_long_form_bass_uncorrected_undistorted.png')
    print('Dab uncorrected undistorted ....')
    make_graph_dis_undis('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/Fiducial_error_minimisation/seaborn/v_fid_long_form_dab_uncorrected_undistorted.csv', r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\My Papers\Fiducial_error_minimisation\figures\v_fid_long_form_dab_uncorrected_undistorted.png')

    print('Bass depth corrs ....')
    make_graphs_other('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/Fiducial_error_minimisation/seaborn/v_fid_long_form_bass_depth_corrs.csv', r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\My Papers\Fiducial_error_minimisation\figures\v_fid_long_form_bass_depth_corrs.tiff')
    print('Dab depth corrs ....')
    make_graphs_other('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/Fiducial_error_minimisation/seaborn/v_fid_long_form_dab_depth_corrs.csv', r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\My Papers\Fiducial_error_minimisation\figures\v_fid_long_form_dab_depth_corrs.tiff')

    print('Exported All')
