# pylint: disable=too-few-public-methods,too-many-statements, unused-import, unused-variable, no-member,dangerous-default-value

'''My library of statistics based functions'''

# base imports
import copy
import itertools
import numbers

# packages
import pandas
import pandas.rpy.common as com
import numpy
import scipy
import scipy.stats
import rpy2.robjects as ro
import statsmodels.stats

# mine
from enum import Enum
from funclib.baselib import switch
import funclib.baselib as baselib
import funclib.iolib as iolib
import funclib.arraylib as arraylib


#region Enuerations
class EnumMethod(Enum):
    '''enum used to select the type of correlation analysis'''
    kendall = 1
    spearman = 2
    pearson = 3

class EnumStatsEngine(Enum):
    '''enum used to select the engine used to calculate stats'''
    r = 1
    scipy = 2
#endregion



#region Correlations
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
    permuted = copy.deepcopy(list_b) #we will permute list_b but don't need to permute list_a
    cnt = 0
    for counter in range(0, int(iterations)):
        cnt += 1
        permuted = numpy.random.permutation(permuted)

        for case in switch(method):
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
        iolib.print_progress(cnt, iterations, prefix=pre, bar_length=30)

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

    for case in baselib.switch(test_type):
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
                tmpstr = 'cor.test(cordf$' + col_a_name + ',cordf$' + col_b_name + ', method="pearson")'
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
                tmpstr = 'cor.test(cordf$' + col_a_name + ',cordf$' + col_b_name + ', method="spearman")'
                result = ro.r(tmpstr)
                teststat = result[3][0]
                pval = result[2][0]
            else:
                teststat, pval = scipy.stats.spearmanr(list_a, list_b)
            break
        if case():
            raise ValueError('Enumeration member not in e_method')

    return  {'teststat':teststat, 'p':pval}




def correlation(a, b, method=EnumMethod.kendall, engine=EnumStatsEngine.scipy):
    '''(list|ndarray, list|ndarray, enumeration, enumeration) -> dict
    Returns a dictionary: {'teststat':teststat, 'p':pval}
    method: is an enumeration member of EnumMethod
    engine: is an enumeration method
    scipy cant cope with nans. Matched nans will be removed if a and b are numpy arrays
    '''
    
    if isinstance(a, numpy.ndarray) or isinstance(b, numpy.ndarray):
        if  isinstance(a, numpy.ndarray) is False or isinstance(b, numpy.ndarray) is False:
            raise ValueError('If numpy arrays are used, both must be ndarray types')

        if a.shape != b.shape:
            raise ValueError('Numpy array shapes must match exactly')

        #scipy doesnt like nans. We drop out paired nans, leaving
        #all other pairings the same
        if arraylib.np_contains_nan(a) and arraylib.np_contains_nan(b):
            dic = arraylib.np_delete_paired_nans_flattened(a, b)
        else:
            dic = {'a':a, 'b':b}

        #we have unmatched nans, ie a nan in one array
        #with a scalar in the other
        #this is an error state - could modify later to exclude
        #all values from both arrays where there is any nan
        if arraylib.np_contains_nan(dic['a']):
            raise ValueError('Numpy array a contains NaNs')

        if arraylib.np_contains_nan(dic['b']):
            raise ValueError('Numpy array b contains NaNs')

        lst_a = dic['a'].flatten().tolist()
        lst_b = dic['b'].flatten().tolist()
    else:
        if  isinstance(a, list) is False or isinstance(b, list) is False:
            raise ValueError('If lists are used, both must be list types')
        lst_a = copy.deepcopy(a)
        lst_b = copy.deepcopy(b)

    if len(lst_a) != len(lst_b):
        raise ValueError('Array lengths must match exactly')
    
    assert isinstance(lst_a, list)
    assert isinstance(lst_b, list)

    for case in baselib.switch(method):
        if case(EnumMethod.kendall):
            if engine == EnumStatsEngine.r:
                df = pandas.DataFrame({'a':lst_a, 'b':lst_b})
                df_r = com.convert_to_r_dataframe(df)
                ro.globalenv['cordf'] = df_r
                tmpstr = 'cor.test(cordf$a, cordf$b, method="kendall")'
                result = ro.r(tmpstr)
                teststat = result[3][0]
                pval = result[2][0]
            else:
                teststat, pval = scipy.stats.kendalltau(lst_a, lst_b)
            break
        if case(EnumMethod.pearson):
            if engine == EnumStatsEngine.r:
                df = pandas.DataFrame({'a':lst_a, 'b':lst_b})
                df_r = com.convert_to_r_dataframe(df)
                ro.globalenv['cordf'] = df_r
                tmpstr = 'cor.test(cordf$a, cordf$b, method="pearson")'
                result = ro.r(tmpstr)
                teststat = result[3][0]
                pval = result[2][0]
            else:
                teststat, pval = scipy.stats.pearsonr(lst_a, lst_b)
            break
        if case(EnumMethod.spearman):
            if engine == EnumStatsEngine.r:
                df = pandas.DataFrame({'a':lst_a, 'b':lst_b})
                df_r = com.convert_to_r_dataframe(df)
                ro.globalenv['cordf'] = df_r
                tmpstr = 'cor.test(cordf$a, cordf$b, method="spearman")'
                result = ro.r(tmpstr)
                teststat = result[3][0]
                pval = result[2][0]
            else:
                teststat, pval = scipy.stats.spearmanr(lst_a, lst_b)
            break
        if case():
            raise ValueError('Enumeration member not in e_method')

    return  {'teststat':teststat, 'p':pval}




def permuted_teststat_check(csvfile, test_col, stat_value_to_check):
    '''(str, int, int, float) -> dic ({'p', 'n', 'more_extreme_n', 'teststat'})
    csvfile: full data file file name
    start_row: row with first line of data (0 based!), pass None if there is are no headers
    test_col: column with test stats, note this is a 0 based index, first column would be indexed as 0.
    stat_value_to_check: the unpermuted test stat result

    Returns a dictionary object:
    'p':   probability of getting this result by chance alone
    'n':   number of values checked
    'more_extreme_n': number of values more extreme than stat_value_to_check
    '''
    col = [test_col]
    df = pandas.read_csv(csvfile, usecols=col)
    assert isinstance(df, pandas.DataFrame)
    
    if stat_value_to_check >= 0:
        res = (df.iloc[0:] > stat_value_to_check).sum()
    else:
        res = (df.iloc[0:] < stat_value_to_check).sum()
    
    return {'p':float(res[0])/(df.iloc[0:]).count()[0], 'n':(df.iloc[0:]).count()[0], 'more_extreme_n':res[0]}




def permuted_teststat_check1(teststats, stat_value_to_check):
    '''(tuple|list) -> dic ({'p', 'n', 'more_extreme_n', 'teststat'})
    teststats is an iterable 
    stat_value_to_check: the unpermuted test stat result

    Returns a dictionary object:
    'p':   probability of getting this result by chance alone
    'n':   number of values checked
    'more_extreme_n': number of values more extreme than stat_value_to_check
    '''
    v = 0
    p = 0
    if stat_value_to_check >= 0:
        for v in teststats:
            if v > stat_value_to_check:
                p += 1
    else:
        for v in teststats:
            if v < stat_value_to_check:
                p += 1
    
    return {'p':float(p)/len(teststats), 'n':len(teststats), 'more_extreme_n':p}




def focal_permutation(x, y, teststat, iters=1000):
    '''(ndarray, ndarray) -> dic
    Perform 3x3 mean and then a permutation correlation test on two 2D arrays
    Calculates p
    dic  {'p':,'more_extreme_n':}
    '''
    
    taus = []
    #only need to do focal mean once on y as this doesnt need to be permuted each time
    y = arraylib.np_focal_mean(y, False)

    for cnt in range(iters):       
        pre = '/* iter:' + str(cnt+1) + ' */'

        #just permute one of them
        a = arraylib.np_permute_2d(x)
        a = arraylib.np_focal_mean(a, False)

        #use scipy - p will be wrong, but the taus will be right
        res = correlation(a, y, engine=EnumStatsEngine.scipy)
        taus.append(res['teststat'])

        iolib.print_progress(cnt+1, iters, prefix=pre, bar_length=30)

    dic = permuted_teststat_check1(taus, teststat)
    return {'p':dic['p'], 'more_extreme_n':dic['more_extreme_n']}
#endregion



#region Binning and recoding
def quantile_bin(nd, percentiles=None, zero_as_zero=False):
    '''(ndarray, list, list, boolean) -> ndarray
    
    percentiles is list of percentiles, defaults to [25, 50, 100]

    Returned array has elements with labels substituted.
    Array
    of floats, nans ignored in calculations and returned as nans
    '''


    def get_quantile_ranges(nd, percentiles, exclude_zeros=False, use_scipy=True):
        '''(ndarray like, listlike, bool) -> list
        get the full intervals
        percentiles=[25,50,75] would give quartiles

        Returns array of arrays size percentiles+1 x 3.
        [[0,1.1,bins[0]
          1.1,2.2,bins[1]]
          where the first two figures in the inner list of the numerical ranges
          for the data in array nd. The last figure is a number which represents the percentile
          to which the range belongs (starts at 1).
          For example: percentiles=[25,50,75] 
          0%-25%=1 25%-50%=2 50%-75%=3 75%-100%=4

          If zeros are excluded they are assigned as 0.


        if exclue_zeros is true, then zeros will be excluded from quantile calculations
        '''
        assert isinstance(percentiles, list)
        #assert isinstance(nd, numpy.ndarray)
    
        ret = []
        a = numpy.array(nd).flatten() #default dtype is float
        assert isinstance(a, numpy.ndarray)

        if exclude_zeros:
            numpy.place(a, a == 0, numpy.nan)

        a = arraylib.np_delete_zeros(a)
        labels = range(1, len(percentiles)+2) #[25,50,75] -> [1,2,3,4]
    
        percentiles.sort()
        ranges = [scipy.stats.scoreatpercentile(a, x) for x in percentiles] if use_scipy else numpy.percentile(a, percentiles)
    
        for ind, item in enumerate(ranges):
            if ind == 0:
                ret.append([a.min() - 0.00001, item, labels[ind]])
            else:
                ret.append([ranges[ind-1], item, labels[ind]])
    
        #add last category
        ret.append([ranges[-1], a.max() + 0.00001, len(labels)])

        return ret


    def get_bin_label(x, ranges, zero_as_zero=False):
        '''(numeric, list, bool) -> string
        Uses the structure return by _get_quantile_ranges

        Zero as zero forces zeros to be excluded from all
        quantile calculations and put under their own label of 0
        '''
        assigned = False
        for ind, item in enumerate(ranges):
            if x == 0 and zero_as_zero:
                ret = 0
                assigned = True
                break
            elif numpy.isnan(x):
                ret = numpy.nan
                assigned = True
                break
            elif item[0] < x <= item[1]:
                ret = item[2] #this is the label index eg 'High'
                assigned = True
                break
    
        if not assigned:
            raise ValueError('Failed to assign bin label')
        return ret


    if percentiles is None: percentiles = [25, 50, 100]
    if nd.dtype != float:
        raise ValueError('Array should be of type float. Try recasting using ndarray.astype(float)')

    qr = get_quantile_ranges(nd, percentiles, zero_as_zero)
    out = numpy.copy(nd)
    func = numpy.vectorize(get_bin_label, excluded=['ranges', 'zero_as_zero'])
    out = func(out, ranges=qr, zero_as_zero=zero_as_zero)
    
    return out
#endregion




#region Contingency
def contingency_conditional(a, bycol=True):
    '''(ndarray, bool)->ndarray
    calculates conditional contingency by rows or columns
    as specified by bycol

    Also adds a marginal row (bycol=False) or marginal col (bycol=True)
    '''
    assert isinstance(a, np.ndarray)
    b = contigency_joint(a)
    assert isinstance(b, np.ndarray)
    marg_rows, marg_cols = stats.contingency.margins(b)   

    if bycol:
        b[:,:-1] = marg_cols #add marginal col
        for i in range(int(b.shape[1])-1): #loop through each col and use the column marginal to calculate conditional
            b[0:-1, i:i+1] = b[0:-1, i:i+1]/b[-1, i:i+1]
    else:
        b[:-1,:] = marg_rows
        for i in range(int(b.shape[0])-1):
            b[i:i+1, 0:-1] = b[i:i+1, 0:-1]/b[i:i+1, -1]
    return b


def contigency_joint(a):
    '''(ndarray, bool)->ndarray
    calculates conditional contingency by rows or columns
    as specified by bycol
    '''
    assert isinstance(a, np.ndarray)
    b = a.astype(float)
    return b/sum(b)
#endregion