# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
from funclib import pandaslib

grey = ["#EEEEEE", "#E8E8E8", "#E3E3E3", "#DEDEDE", "#D9D9D9", "#D3D3D3", "#CECECE", "#C9C9C9", "#C4C4C4", "#BFBFBF"]
grey = ["#666666"]
sns.set(palette=grey, font='Times New Roman', font_scale=0.8, style="ticks") #, style="ticks"
PLOT_KWARGS = {'aa':True, 'linestyle':'dashed', 'c':'0.65', 'lw':1}
PLOT_REG_KWARGS = {'aa':True, 'linestyle':'solid', 'lw':1}
SCATTER_KWARGS = {'marker':'x', 's':10}
SPACER_FACTOR = 18
#sns.set_style(rc={"ytick.major.size": 50}

def make_graph_dis_undis(csv, out):
    '''(str, str) -> void
    csv: csv file with data
    out: full filename to save the graph as
    '''
    df = pd.read_csv(csv)
    #df.sort_values(by=['Species', 'Marker', 'Correction']) doesnt seem to work
    g = sns.lmplot(x='Actual length', y='Error', data=df, col='Marker', row='Correction', ci=95, x_ci='ci', n_boot=1000, size=1.4, aspect=1.4, line_kws=PLOT_REG_KWARGS, scatter_kws=SCATTER_KWARGS) #size=1, aspect=1.2
    g.set_axis_labels('tl (mm)', 'Error (mm)')

    if 'bass' in csv:
        xlim = (210, 630);ylim = (-150, 70)
        g.set(xlim=xlim, ylim=ylim, xticks=[250, 350, 450, 550], yticks=[-100, -50, 0, 50])
    else: #dab
        xlim=(90, 300); ylim=(-60, 20)
        g.set(xlim=xlim, ylim=ylim)
    ymid = (ylim[0] + ylim[1]) /2

    g.set_titles('{col_name}')
    #g.fig.subplots_adjust(wspace=0.2, hspace=0.4)

    #coords are rc
    ax00  = g.facet_axis(0, 0); ax01  = g.facet_axis(0, 1); ax02  = g.facet_axis(0, 2)
    ax10  = g.facet_axis(1, 0); ax11  = g.facet_axis(1, 1); ax12  = g.facet_axis(1, 2)
    facets = [ax00, ax01, ax02, ax10, ax11, ax12]
    ax10.set_title(''); ax11.set_title(''); ax12.set_title('')

    spacer = (max(xlim) - min(xlim)) / SPACER_FACTOR
    print('spacer %s' % spacer)
    ax02.text(xlim[1]+spacer, ymid, 'Distorted', ha='center', va='center', rotation=-90)
    ax12.text(xlim[1]+spacer, ymid, 'Undistorted', ha='center', va='center', rotation=-90)

    #write the stats to the graph
    #These results are from spss v_fid_long_form_all.spv
    if 'bass' in csv:
        ax00.text(xlim[0] + spacer, ylim[0] + (spacer/2), 'b=0.03, R$^2$=0.24') #distorted background
        ax01.text(xlim[0] + spacer, ylim[0] + (spacer/2), 'b=-0.005, R$^2$=0.001') #distorted foreground
        ax02.text(xlim[0] + spacer, ylim[0] + (spacer/2), 'b=-0.09, R$^2$=0.14') #distorted laser

        ax10.text(xlim[0] + spacer, ylim[0] + (spacer/2), 'b=0.03, R$^2$=0.13') #undistorted background
        ax11.text(xlim[0] + spacer, ylim[0] + (spacer/2), 'b=0.01 R$^2$=0.01') #undistorted foreground
        ax12.text(xlim[0] + spacer, ylim[0] + (spacer/2), 'b=-0.05, R$^2$=0.23') #undistorted laser
    else:
        ax00.text(xlim[0] + spacer, ylim[0] + (spacer/2), 'b=0.04, R$^2$=0.61') #distorted background
        ax01.text(xlim[0] + spacer, ylim[0] + (spacer/2), 'b=-0.17, R$^2$=0.80') #distorted foreground
        ax02.text(xlim[0] + spacer, ylim[0] + (spacer/2), 'b=-0.26, R$^2$=0.95') #distorted laser

        ax10.text(xlim[0] + spacer, ylim[0] + (spacer/2), 'b=0.04, R$^2$=0.67') #undistorted background
        ax11.text(xlim[0] + spacer, ylim[0] + (spacer/2), 'b=-0.08, R$^2$=0.76') #undistorted foreground
        ax12.text(xlim[0] + spacer, ylim[0] + (spacer/2), 'b=-0.09, R$^2$=0.91') #undistorted laser


    if 'bass' in csv:
        g.fig.text(0.03, 0.95, 'Seabass', transform = g.fig.transFigure, size='large')
    else:
       g.fig.text(0.03, 0.95, 'Dab', transform = g.fig.transFigure, size='large')

    #draw y=0 line
    for ax in facets:
        ax.plot([min(xlim), max(xlim)], [0, 0], **PLOT_KWARGS)

    g.despine()
    g.fig.tight_layout()
    plt.savefig(out, dpi=300)
    #plt.show()


def make_graphs_other(csv, out):
    '''(str, str) -> void
    csv: csv file with data
    out: full filename to save the graph as
    '''
    df = pd.read_csv(csv)
    #df.sort_values(by=['Species', 'Marker', 'Correction_Order']) #didnt seem to work
    g = sns.lmplot(x='Actual length', y='Error', data=df, col='Marker', row='Correction', ci=95, x_ci='ci', n_boot=1000, size=1.2, aspect=1.05, line_kws=PLOT_REG_KWARGS, sharex=True, sharey=True, scatter_kws=SCATTER_KWARGS) #size=1, aspect=1.2

    if 'bass' in csv:
        xlim = (210, 630)
        xticks = [250, 350, 450, 550]
        ylim = (-40, 70)
        yticks = [-40, -20, 0, 20, 40, 60]
    else:
        xlim = (90, 300)
        xticks = [100, 150, 200, 250]
        ylim = (-40, 70)
        yticks = [-40, -20, 0, 20, 40, 60]


    g.set(yticks=yticks, ylim=ylim, xlim=xlim, xticks=xticks)
    g.set_axis_labels('tl (mm)', 'Error (mm)')

    #g.set_titles('{col_name}{row_name}')

    #coords are rc
    ax00  = g.facet_axis(0, 0); ax01  = g.facet_axis(0, 1)
    ax10  = g.facet_axis(1, 0); ax11  = g.facet_axis(1, 1)
    ax20  = g.facet_axis(2, 0); ax21  = g.facet_axis(2, 1)
    ax30  = g.facet_axis(3, 0); ax31  = g.facet_axis(3, 1)
    ax40  = g.facet_axis(4, 0); ax41  = g.facet_axis(4, 1)
    facets = [ax00, ax10, ax20, ax30, ax40, ax01, ax11, ax21, ax31, ax41]

    for i, ax in enumerate(facets):
        ax.set_title('')
        ax.plot([min(xlim), max(xlim)], [0, 0], **PLOT_KWARGS)

    ax00.set_title('Foreground'); ax01.set_title('Laser')

    spacer = (max(xlim) - min(xlim)) / SPACER_FACTOR
    y_spacer = (max(ylim) - min(ylim)) / SPACER_FACTOR

    #write the stats to the graph
    #These results are from spss v_fid_long_form_all.spv
    if 'bass' in csv:
        ax00.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=0.04, R$^2$=0.10', size='smaller') #foreground depth
        ax01.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=0.02, R$^2$=0.05', size='smaller') #laser depth

        ax10.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=0.02, R$^2$=0.03', size='smaller') #foreground iterative
        ax11.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=0.01, R$^2$=0.01', size='smaller') #laser iterative

        ax20.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=0.02, R$^2$=0.02', size='smaller') #foreground profile
        ax21.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=-0.01, R$^2$=0.03', size='smaller') #laser profile

        ax30.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=0.0001, R$^2$<0.001', size='smaller') #foreground sensor
        ax31.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=0.004, R$^2$=0.001', size='smaller') #laser sensor

        ax40.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=0.01, R$^2$=0.01', size='smaller') #foreground calib
        ax41.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=-0.01, R$^2$=0.02', size='smaller') #laser calib

    else:

        ax00.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=0.04, R$^2$=0.35', size='smaller') #foreground depth
        ax01.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=0.02, R$^2$=-0.31', size='smaller') #laser depth

        ax10.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=0.05, R$^2$=0.43', size='smaller') #foreground iterative
        ax11.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=0.04, R$^2$=0.63', size='smaller') #laser iterative

        ax20.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=-0.01, R$^2$=0.06', size='smaller') #foreground profile
        ax21.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=-0.02, R$^2$=0.44', size='smaller') #laser profile

        ax30.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=0.01, R$^2$=0.03', size='smaller') #foreground sensor
        ax31.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=0.004, R$^2$=0.004', size='smaller') #laser sensor

        ax40.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=-0.02, R$^2$=0.22', size='smaller') #foreground calib
        ax41.text(xlim[0] + spacer, ylim[1] - (y_spacer*2), 'b=-0.03, R$^2$=0.32', size='smaller') #laser calib

    if 'dab' in csv:
        spacer = (max(xlim) - min(xlim)) / SPACER_FACTOR
        print('spacer %s' % spacer)
        ymid = (ylim[0] + ylim[1]) /2 #place right most labels
        ax01.text(xlim[1]+spacer, ymid, 'Depth', ha='center', va='center', rotation=-90)
        ax11.text(xlim[1]+spacer, ymid, 'Iterative', ha='center', va='center', rotation=-90)
        ax21.text(xlim[1]+spacer, ymid, 'Profile', ha='center', va='center', rotation=-90)
        ax31.text(xlim[1]+spacer, ymid, 'Sensor-profile', ha='center', va='center', rotation=-90)
        ax41.text(xlim[1]+spacer, ymid, 'Calib.-profile ', ha='center', va='center', rotation=-90)

    if 'bass' in csv:
        g.fig.text(0.5, 0.98, 'Seabass', transform = g.fig.transFigure, va='center', ha='center', weight='bold')
    else:
        g.fig.text(0.5, 0.98, 'Dab', transform = g.fig.transFigure, va='center', ha='center', weight='bold') #size='large'

    g.despine()
    g.fig.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches='tight')
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

    print('Bass other...')
    make_graphs_other('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/Fiducial_error_minimisation/seaborn/v_fid_long_form_bass_depth_corrs.csv', r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\My Papers\Fiducial_error_minimisation\figures\v_fid_long_form_bass_depth_corrs.png')

    print('Dab other...')
    make_graphs_other('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/Fiducial_error_minimisation/seaborn/v_fid_long_form_dab_depth_corrs.csv', r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\My Papers\Fiducial_error_minimisation\figures\v_fid_long_form_dab_depth_corrs.png')

    print('Exported All')
