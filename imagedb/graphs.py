# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from funclib import pandaslib

sns.set(color_codes=True)


def make_graph(csv, out):
    '''(str, str) -> void
    csv: csv file with data
    out: full filename to save the graph as
    '''
    df = pd.read_csv(csv, delimiter='\t')
    g = sns.lmplot(x='Actual length', y='MBE', data=df, col='Marker', row='Correction', ci=95, x_ci='ci', n_boot=1000, size=2, aspect=1.4) #size=1, aspect=1.2
    g.set_axis_labels('Actual length (mm)', 'MBE (mm)')
    g.set(xlim=(90, 300), ylim=(-60, 20))
    g.set_titles('{col_name}')
    g.fig.subplots_adjust(wspace=0.2, hspace=0.4)
    g.despine()
    plt.show()



if __name__ == "__main__":
    #These are created from SQL Server imagedb project, fid_long_form_all.sql
    #The exported fields and values were manually renamed in the exported data

    #First we create distorted and undistorted for fg, bg and laser. This is because background doesnt have all corrections
    #So we split it up so that the facetgrid doesnt have missing graphs
    make_graph('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/Fiducial_error_minimisation/seaborn/v_fid_long_form_bass_uncorrected_undistorted.csv', r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\My Papers\Fiducial_error_minimisation\figures\v_fid_long_form_bass_uncorrected_undistorted.tiff')
    make_graph('C:/Users/Graham Monkman/OneDrive/Documents/PHD/My Papers/Fiducial_error_minimisation/seaborn/v_fid_long_form_dab_uncorrected_undistorted.csv', r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\My Papers\Fiducial_error_minimisation\figures\v_fid_long_form_dab_uncorrected_undistorted.tiff')



