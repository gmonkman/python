# pylint: disable=pointless-statement
'''Main program to calculate correlation distribution
of my FMM and PAM data with my point coincident data
by 1km^2 grids.
Kendall's correlation coefficent is used
'''

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

#My Libs
from enum import Enum
import statslib
import funclib
import iolib

class EnumData(Enum):
    '''enum used to tell functions if we have FMM or PAM data'''
    pam = 1
    fmm = 2

#path hardcoded
def get_file_name(fmm_or_pam=EnumData.pam):
    '''(EnumData) -> str
    Gets the save file name for output
    '''
    if ITERATIONS > 0:
        suffix = 'i' + str(int(ITERATIONS))  + ('_No0.csv' if EXCLUDE_ZEROS else '.csv')
    else:
        suffix = 'sem' + str(SEM) +  ('_No0.csv' if EXCLUDE_ZEROS else '.csv')

    if fmm_or_pam == EnumData.pam:
        return 'data\\' + 'pam_results_' + suffix
    else:
        return 'data\\' + 'fmm_results_' + suffix

RUN = funclib.read_number(raw_input('Run tests for PAM (1), FMM (2) or Both (3):'), EnumData.pam.value + EnumData.fmm.value)
if RUN == 0:
    sys.exit()

ITERATIONS = funclib.read_number(raw_input('Input iterations'), 10)

#Now do the stats work
results = [['tau', 'p']]
df =  df = pandas.read_csv('.\\data\\fmm.csv')

if bool(int(RUN) & EnumData.pam.value):
    TAU, CONF = statslib.correlation_test_from_csv(df, scipy.stats.kendalltau(PAM_SCORES, PAM_DAYS))
    SUMMARY.append([funclib.datetime_stamp(), 'PAM Kendall on Scores vs days_pa_km', TAU, CONF])
    PAM_CORRS.append([TAU, CONF])
    PAM_CORRS.extend(statslib.permuted_correlation(PAM_SCORES, PAM_DAYS, test_stat=TAU, out_greater_than_test_stat=PAM_GREATER, iterations=ITERATIONS, sem_mean_proportion=SEM, exclude_zero_pairs=EXCLUDE_ZEROS, out_final_iters=FINAL_ITERS_PAM))
    PAM_SUMMARY = 'Completed PAM after ' + str(FINAL_ITERS_PAM[0]) + ' iterations. p=' + str(round(PAM_GREATER[0]/float(FINAL_ITERS_PAM[0]), 5))
    iolib.writecsv(get_file_name(EnumData.pam), PAM_CORRS, inner_as_rows=False)
    iolib.write_to_eof(get_file_name(EnumData.pam), PAM_SUMMARY)
    print PAM_SUMMARY


if bool(int(RUN) & EnumData.fmm.value):
    TAU, CONF = scipy.stats.kendalltau(FMM_SCORES_YEARHWL, FMM_YEARHWL)
    SUMMARY.append([funclib.datetime_stamp(), 'FMM Kendall on SCORES vs YearHWL', TAU, CONF])

    TAU, CONF = scipy.stats.kendalltau(FMM_SCORES_VALUE, FMM_VALUE)
    SUMMARY.append([funclib.datetime_stamp(), 'FMM Kendall on SCORES vs Value', TAU, CONF])

    TAU, CONF = scipy.stats.kendalltau(FMM_SCORES_YEAR, FMM_YEAR)
    SUMMARY.append([funclib.datetime_stamp(), 'FMM Kendall on SCORES vs YEAR', TAU, CONF])

    FMM_CORRS.append([TAU, CONF])
    #CHANGE THIS LINE TO USE MATRIX OF CHOICE
    FMM_CORRS.extend(statslib.permuted_correlation(FMM_SCORES_YEAR, FMM_YEAR, test_stat=TAU, out_greater_than_test_stat=FMM_GREATER, iterations=ITERATIONS, sem_mean_proportion=SEM, exclude_zero_pairs=EXCLUDE_ZEROS, out_final_iters=FINAL_ITERS_FMM))
    FMM_SUMMARY = 'Completed FMM after ' + str(FINAL_ITERS_FMM[0]) + ' iterations. p=' + str(round(FMM_GREATER[0]/float(FINAL_ITERS_FMM[0]), 5))
    print FMM_SUMMARY
    iolib.writecsv(get_file_name(EnumData.fmm), FMM_CORRS, inner_as_rows=False)
    iolib.write_to_eof(get_file_name(EnumData.fmm), FMM_SUMMARY)

#venuecnt correlation to summary
TAU, CONF = scipy.stats.kendalltau(FMM_VENUECNT_YEARHWL, FMM_YEARHWL_VC)
SUMMARY.append([funclib.datetime_stamp(), 'FMM Kendall on VenueCnt vs YearHWL', TAU, CONF])

TAU, CONF = scipy.stats.kendalltau(FMM_VENUECNT_VALUE, FMM_VALUE_VC)
SUMMARY.append([funclib.datetime_stamp(), 'FMM Kendall on VenueCnt vs Value', TAU, CONF])

TAU, CONF = scipy.stats.kendalltau(FMM_VENUECNT_YEAR, FMM_YEAR_VC)
SUMMARY.append([funclib.datetime_stamp(), 'FMM Kendall on VenueCnt vs Year', TAU, CONF])

STATFILE = '.\\data\\Stats' + funclib.datetime_stamp() + '.csv'
iolib.writecsv(STATFILE, SUMMARY, inner_as_rows=False)

with fuckit:
    subprocess.check_call(['explorer', '.\\data'])
