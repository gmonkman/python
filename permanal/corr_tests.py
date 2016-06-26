#base
import csv
import subprocess
import sys
import datetime
import copy

#third party
import scipy
import scipy.stats
import fuckit
import pandas
import numpy
import pandas.rpy.common as com
import rpy2.robjects as ro

#My Libs
from enum import Enum
import statslib
import funclib
import iolib

def do_tests():
    pamfile = pandas.read_csv('data\\pam.csv')
    fmmfile = pandas.read_csv('data\\fmm.csv')
    fmmfilenonzero = pandas.read_csv('data\\fmmnonzero.csv')
    pamfilenonzero = pandas.read_csv('data\\pamnonzero.csv')
    assert isinstance(pamfile, pandas.DataFrame)
    assert isinstance(fmmfile, pandas.DataFrame)
    assert isinstance(fmmfilenonzero, pandas.DataFrame)
    assert isinstance(pamfilenonzero, pandas.DataFrame)

    #folder to save results
    outdir = '.\\output\\'

    results = [['test_type', 'desc', 'varname1', 'varname2', 'exclude zeros', 'teststat', 'p']]

    iterations = funclib.read_number(raw_input('Input iterations. Enter 0 to not run permutation tests:'), 0)

    #FMM no zero pairs
    out = [0]
    dic = statslib.correlation_test_from_csv(fmmfilenonzero, 'VALUE', 'VenueCnt', statslib.EnumMethod.kendall, statslib.EnumStatsEngine.r)
    results.append(['Kendall', 'FMM No Zeros', 'VALUE', 'VenueCnt', 0, dic['teststat'], dic['p']])
    if iterations > 0:
        venuecnt = fmmfilenonzero['VenueCnt'].tolist()
        value = fmmfilenonzero['VALUE'].tolist()
        corr_results = statslib.permuted_correlation(venuecnt, value, dic['teststat'], iterations, statslib.EnumMethod.kendall, out)
        file_name = outdir + 'fmmNo0_' + funclib.datetime_stamp() + '.csv'
        iolib.writecsv(file_name, corr_results, inner_as_rows=False)

    #FMM
    out = [0]
    dic = statslib.correlation_test_from_csv(fmmfile, 'VALUE', 'VenueCnt', statslib.EnumMethod.kendall, statslib.EnumStatsEngine.r)
    results.append(['Kendall', 'FMM All data', 'VALUE', 'VenueCnt', 0, dic['teststat'], dic['p']])
    if iterations > 0:
        venuecnt = fmmfile['VenueCnt'].tolist()
        value = fmmfile['VALUE'].tolist()
        corr_results = statslib.permuted_correlation(venuecnt, value, dic['teststat'], iterations, statslib.EnumMethod.kendall, out)
        file_name = outdir + 'fmm_' + funclib.datetime_stamp() + '.csv'
        iolib.writecsv(file_name, corr_results, inner_as_rows=False)

    #Do PAM
    out = [0]
    dic = statslib.correlation_test_from_csv(pamfile, 'days_pa_km', 'VenueCnt', statslib.EnumMethod.kendall, statslib.EnumStatsEngine.r)
    results.append(['Kendall', 'PAM All data', 'days_pa_km', 'VenueCnt', 0, dic['teststat'], dic['p']])
    if iterations > 0:
        venuecnt = pamfile['VenueCnt'].tolist()
        dayspakm = pamfile['days_pa_km'].tolist()
        corr_results = statslib.permuted_correlation(venuecnt, dayspakm, dic['teststat'], iterations, statslib.EnumMethod.kendall, out)
        file_name = outdir + 'pam_' + funclib.datetime_stamp() + '.csv'
        iolib.writecsv(file_name, corr_results, inner_as_rows=False)
    
    #exclude zeros
    out = [0]
    dic = statslib.correlation_test_from_csv(pamfilenonzero, 'days_pa_km', 'VenueCnt', statslib.EnumMethod.kendall, statslib.EnumStatsEngine.r)
    results.append(['Kendall', 'PAM No Zeros', 'days_pa_km', 'VenueCnt', 0, dic['teststat'], dic['p']])
    if iterations > 0:
        venuecnt = pamfilenonzero['VenueCnt'].tolist()
        dayspakm = pamfilenonzero['days_pa_km'].tolist()
        corr_results = statslib.permuted_correlation(venuecnt, dayspakm, dic['teststat'], iterations, statslib.EnumMethod.kendall, out)
        file_name = outdir + 'pamNo0_' + funclib.datetime_stamp() + '.csv'
        iolib.writecsv(file_name, corr_results, inner_as_rows=False)

    #write results to file
    fileout = outdir + 'corr_tests_' + funclib.datetime_stamp() + '.csv'
    iolib.writecsv(fileout, results, inner_as_rows=False)

    with fuckit:
        subprocess.check_call(['explorer', '.\\output'])

do_tests()
sys.exit()