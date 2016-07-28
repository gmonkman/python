from __future__ import print_function, division

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import kendalltau
import seaborn as sns


x = np.linspace(0, 10, 1000)
plt.plot(x, np.sin(x), x, np.cos(x))

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
    
