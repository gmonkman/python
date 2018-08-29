# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''helper funcs for matplotlib'''
from enum import Enum as _Enum
import pandas as _pd

INCH = 2.54


class FigWidthsCM(_Enum):
    minimal = 3
    single_col = 9
    one_and_a_half_col = 14
    two_col = 19


class FigWidthsInch(_Enum):
    minimal = 1.181
    two_thirds_col = 2.362
    single_col = 3.543
    one_and_a_half_col = 5.512
    two_col = 7.480



def yaxis_hideticklabels(ax):
    '''hide tick labels'''
    labels = [item.get_text() for item in ax.get_yticklabels()]
    empty_string_labels = ['']*len(labels)
    ax.set_yticklabels(empty_string_labels)


def xaxis_hideticklabels(ax):
    '''hide tick labels'''
    labels = [item.get_text() for item in ax.get_xticklabels()]
    empty_string_labels = ['']*len(labels)
    ax.set_xticklabels(empty_string_labels)


def yaxis_hidelabel(ax):
    ax.yaxis.label.set_visible(False)


def xaxis_hidelabel(ax):
    ax.xaxis.label.set_visible(False)


def label_pts(x, y, lbls, ax):
    '''(list|ndarray, list|ndarray, list|ndarray, matplotlib.Axes)->None
    Label points
    '''
    a = _pd.concat({'x': x, 'y': y, 'val': lbls}, axis=1)
    for i, point in a.iterrows():
        ax.text(point['x'], point['y'], str(point['val']))


def legend_remove(ax):
    '''remove legend'''
    ax.legend_.remove()


def xaxis_scale(ax, x1, x2):
    '''set xaxis scale'''
    ax.set_xlim(x1, x2)

def yaxis_scale(ax, y1, y2):
    '''set yaxis scale'''
    ax.set_ylim(y1, y2)


def legend_pos(ax, pos, x=None, y=None):
    raise NotImplementedError('See https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot')
    #Example of hiding the legend, then adding in with custom labels, this will get rid of the title as well
    #g = sns.lineplot(x='Angle', y='MV adjusted error %', hue='CNN', style='CNN', data=df, legend=False)
    #g.legend(g.lines, ('nas', 'res', 'ssd'), bbox_to_anchor=(0,1.02,1,0.2), loc="center left", mode="expand", borderaxespad=0, ncol=3, title='')


def cm2inch1(v):
    '''(int|float)->int|float
    '''
    return v / INCH