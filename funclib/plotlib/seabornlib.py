from __future__ import print_function, division

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import kendalltau
import seaborn as sns

from enum import Enum
from funclib import baselib



#region classes
class EnumPalette(Enum):
    grey1 = 1
#endregion


x = np.linspace(0, 10, 1000)
plt.plot(x, np.sin(x), x, np.cos(x))


def palette(palette=EnumPalette.grey1):
    '''(EnumPalette) -> list
    
    '''
    default = ["#EEEEEE", "#E8E8E8", "#E3E3E3", "#DEDEDE", "#D9D9D9", "#D3D3D3", "#CECECE", "#C9C9C9", "#C4C4C4", "#BFBFBF"] #grey1
    for case in switch(palette):
        if case(EnumPalette.grey1):
            return ["#EEEEEE", "#E8E8E8", "#E3E3E3", "#DEDEDE", "#D9D9D9", "#D3D3D3", "#CECECE", "#C9C9C9", "#C4C4C4", "#BFBFBF"]
            break
        if case():
            return default


#region graphs

def bivariate_histogram(x, y):
    '''(ndarray, ndarray) -> void
    bivariate historgram
    '''
    rs = np.random.RandomState(11)
    x = rs.gamma(2, size=1000)
    y = -.5 * x + rs.normal(size=1000)

    sns.set(style="ticks")
    sns.jointplot(x, y, kind="hex", stat_func=kendalltau, color="#4CB391")
    v=100    
#endregion
