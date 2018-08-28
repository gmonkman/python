'''main init for plotlib'''
from enum import Enum as _Enum

__all__ = ['matplotlib-2d', 'matplotlib-3d', 'qplot', 'seabornlib', 'stackedbargraph']



INCH = 2.54

class FigWidths(_Enum):
    minimal = 3
    half_col = 6
    single_col = 9
    one_and_a_half_col = 14
    two_col = 19


def getwidth(sz, as_inch=True):
    '''(Enum:FigWidths|float, bool)->float

    Get publication fig widths in cm or inches
    '''
    assert isinstance(sz, FigWidths)
    return sz.value/INCH if as_inch else sz.value
