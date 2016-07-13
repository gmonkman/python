# pylint: disable=too-few-public-methods

'''My library of statistics based functions'''

# base imports
import copy
import numbers

# packages
import pandas
import pandas.rpy.common as com
import numpy
import scipy
import scipy.stats
import rpy2.robjects as ro


# mine
from enum import Enum
import funclib.baselib

class EnumMethod(Enum):
    '''enum used to select the type of correlation analysis'''
    kendall = 1
    spearman = 2
    pearson = 3

class EnumStatsEngine(Enum):
    '''enum used to select the engine used to calculate stats'''
    r = 1
    scipy = 2

def permuted_correlation(list_a, list_b, test_stat, iterations=0, method=EnumMethod.kendall, out_greater_than_test_stat=0):
    '''(list, list, float, int, enumeration, list[byref], list[byref], enumeration) -> list
    Return a list containing multiple [n=iterations] of correlation test statistic and p values
    following permutation. e_method is an enumeration member of e_method.

    test_stat is the actual x,y calulated correlation value

    list_a and list_b should be passed in their original (paired) order
    for the exclude zero pairs to work.

    Iterations is manual number of iterations (ignores max_iterations).
    '''
    assert isinstance(list_a, list), 'list_a should be a list'
    assert isinstance(list_b, list), 'list_b should be a list'
    assert isinstance(iterations, numbers.Number), 'iterations should be an int'

    if iterations == 0:
        raise ValueError('Iterations cannot be zero')

    results = []
    justtest = []
    permuted = copy.deepcopy(list_b) #we will permute list_b put don't need to permute list_a
    cnt = 0
    for counter in range(0, int(iterations)):
        cnt += 1
        permuted = numpy.random.permutation(permuted)

        for case in funclib.baselib.switch(method):
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
        pre = '/* iter:' + str(cnt) + ' */'
        funclib.iolib.print_progress(cnt, iterations, prefix=pre, bar_length=30)

    return results

def correlation_test_from_csv(file_name_or_dataframe, col_a_name, col_b_name, test_type=EnumMethod.kendall, engine=EnumStatsEngine.scipy):
    ''' (string|pandas.dataframe,string,string,EnumMethod,EnumStatsEngine) -> dictionary
    Assumes that the first row is headers, will fail if this is not the case.

    Returns a dict object with keys 'teststat' and 'p'

    NOTE:This opens file_name each time so dont recommend it for repeating tests.
    '''
    if isinstance(file_name_or_dataframe, str):
        df = pandas.read_csv(file_name_or_dataframe)
    else:
        df = file_name_or_dataframe
    assert isinstance(df, pandas.DataFrame)

    list_a = df[col_a_name].tolist()
    list_b = df[col_b_name].tolist()

    for case in funclib.baselib.switch(test_type):
        if case(EnumMethod.kendall):
            if engine == EnumStatsEngine.r:
                df_r = com.convert_to_r_dataframe(df)
                ro.globalenv['cordf'] = df_r
                tmpstr = 'cor.test(cordf$' + col_a_name + ',cordf$' + col_b_name + ', method="kendall")'
                result = ro.r(tmpstr)
                teststat = result[3][0]
                pval = result[2][0]
            else:
                teststat, pval = scipy.stats.kendalltau(list_a, list_b)
            break
        if case(EnumMethod.pearson):
            if engine == EnumStatsEngine.r:
                df_r = com.convert_to_r_dataframe(df)
                ro.globalenv['cordf'] = df_r
                tmpstr = 'cor.test(cordf$' + col_a_name + ',cordf$' + col_b_name + ', method="kendall")'
                result = ro.r(tmpstr)
                teststat = result[3][0]
                pval = result[2][0]
            else:
                teststat, pval = scipy.stats.pearsonr(list_a, list_b)
            break
        if case(EnumMethod.spearman):
            if engine == EnumStatsEngine.r:
                df_r = com.convert_to_r_dataframe(df)
                ro.globalenv['cordf'] = df_r
                tmpstr = 'cor.test(cordf$' + col_a_name + ',cordf$' + col_b_name + ', method="kendall")'
                result = ro.r(tmpstr)
                teststat = result[3][0]
                pval = result[2][0]
            else:
                teststat, pval = scipy.stats.spearmanr(list_a, list_b)
            break
        if case():
            raise ValueError('Enumeration member not in e_method')

    return  {'teststat':teststat, 'p':pval}
