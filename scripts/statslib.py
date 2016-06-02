# pylint: disable=too-few-public-methods
'''My library of statistics based functions'''

# base imports
import copy
import numbers

# packages
import numpy
import scipy
import scipy.stats

# mine
from enum import Enum
import funclib

class EnumMethod(Enum):
    '''enum used to select the type of correlation analysis'''
    kendall = 1
    spearman = 2
    pearson = 3

def permuted_correlation(list_a, list_b, iterations, method=EnumMethod.kendall, exclude_zero_pairs=False):
    '''(list,list,int,e_method) -> list
    Return a list containing multiple [n=iterations] spearman's r values
    following permutation. e_method is an enumeration member of e_method.

    list_a and list_b should be passed in their original (paired) order
    for the exclude zero pairs to work.
    '''
    assert isinstance(list_a, list), 'list_a should be a list'
    assert isinstance(list_b, list), 'list_b should be a list'
    assert isinstance(iterations, numbers.Number), 'iterations should be an int'

    #remove paired zero values from both lists
    if exclude_zero_pairs:
        funclib.list_delete_value_pairs(funclib.list_delete_value_pairs(list_a, list_b, 0))

    results = []
    permuted = copy.deepcopy(list_b) #we will permute list_b put don't need to permute list_a
    cnt = 0
    for counter in range(0, int(iterations)):
        cnt += 1
        funclib.printProgress(cnt, iterations)
        permuted = numpy.random.permutation(permuted)
        for case in funclib.switch(method):
            if case(EnumMethod.kendall):
                teststat, pval = scipy.stats.kendalltau(list_a, permuted)
                break
            if case(EnumMethod.pearson):
                teststat, pval = scipy.stats.pearsonr(list_a, permuted)
                break
            if case(EnumMethod.spearman):
                teststat, pval = scipy.stats.spearmanr(list_a, permuted)
                break
            if case():
                raise ValueError('Enumeration member not in e_method')
        results.append([teststat, pval])

    return results
