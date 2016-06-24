# pylint: disable=too-few-public-methods
'''My library of statistics based functions'''

# base imports
import copy
import numbers

# packages
import pandas
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

def permuted_correlation(list_a, list_b, test_stat, iterations=0, sem_mean_proportion=0.01, max_iterations=1000000, method=EnumMethod.kendall, exclude_zero_pairs=False, out_final_iters=0, out_greater_than_test_stat=0):
    '''(list, list, float, int, float[ratio], int, enumeration, bool, list[byref], list[byref]) -> list
    Return a list containing multiple [n=iterations] spearman's r values
    following permutation. e_method is an enumeration member of e_method.

    test_stat is the actual x,ycalulated correlation value

    list_a and list_b should be passed in their original (paired) order
    for the exclude zero pairs to work.

    Iterations is manual number of iterations (ignores max_iterations). If iterations is zero then sem_mean_proportion (i.e. standard error/mean) is used as the stopping criteria.
    '''
    assert isinstance(list_a, list), 'list_a should be a list'
    assert isinstance(list_b, list), 'list_b should be a list'
    assert isinstance(iterations, numbers.Number), 'iterations should be an int'

    is_sem = False

    if iterations == 0 and (sem_mean_proportion <= 0):
        raise ValueError('Iterations cannot be zero when sem_mean_proportion is <= 0')

    if iterations == 0:
        iterations = max_iterations
        is_sem = True

    #remove paired zero values from both lists
    if exclude_zero_pairs:
        funclib.list_delete_value_pairs(list_a, list_b, 0)

    results = []
    justtest = []
    permuted = copy.deepcopy(list_b) #we will permute list_b put don't need to permute list_a
    cnt = 0
    for counter in range(0, int(iterations)):
        cnt += 1
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

        if teststat > test_stat:
            out_greater_than_test_stat[0] += 1

        results.append([teststat, pval])
        justtest.append([teststat])
        if is_sem:
            if len(justtest) > 1:
                sem_ratio = scipy.stats.sem(justtest)/abs(numpy.mean(justtest))
            else:
                sem_ratio = 1

            pre = '/* sem ratio:' + str(round(sem_ratio, 5)) + ' */'
            funclib.printProgress(cnt, max_iterations, prefix=pre, barLength=30)
            if sem_ratio < sem_mean_proportion:
                break
        else:
            pre = '/* iter:' + str(cnt) + ' */'
            funclib.printProgress(cnt, iterations, prefix=pre, barLength=30)

    out_final_iters[0] = cnt
    return results

def correlation_test_from_csv(file_name, col_a_name, col_b_name, ignore_paired_zeros=False, test_type=EnumMethod.kendall):
    ''' (string,string,string,EnumMethod) -> dictionary
    Assumes that the first row is headers, will fail if this is not the case.

    Returns a dict object with keys 'teststat' and 'p'

    NOTE:This opens file_name each time so dont recommend it for repeating tests.
    '''
    assert isinstance(df, pandas.DataFrame)
    df = pandas.read_csv(file_name)
    list_a = df[col_a_name].tolist()
    list_b = df[col_b_name].tolist()
    if ignore_paired_zeros:
        funclib.list_delete_value_pairs(list_a, list_b)

    for case in funclib.switch(test_type):
        if case(EnumMethod.kendall):
            teststat, pval = scipy.stats.kendalltau(list_a, list_b)
            break
        if case(EnumMethod.pearson):
            teststat, pval = scipy.stats.pearsonr(list_a, list_b)
            break
        if case(EnumMethod.spearman):
            teststat, pval = scipy.stats.spearmanr(list_a, list_b)
            break
        if case():
            raise ValueError('Enumeration member not in e_method')

    return  {'teststat':teststat, 'p':pval}

