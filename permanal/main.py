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

#third party
import scipy
import scipy.stats
import fuckit

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

ITERATIONS = funclib.read_number(raw_input('Input iterations, enter zero to input SEM proportion:'), 0)
SEM = 0

if ITERATIONS == 0:
    SEM = funclib.read_number(raw_input('Input standard error of mean proportion (0.01 recommended):'), 0.01)
    if SEM <= 0:
        raise ValueError('You must provide sensible values for iteration number or SEM proportion')

EXCLUDE_ZEROS = bool(funclib.read_number(raw_input("Exclude zero pairs (0 = include zero pairs, 1 = exclude zero pairs):"), 0))

#Opend the csv data
MY_DATA = open('data\\allNew.csv', 'rb')
#MY_DATA = open('data\\tmp.csv', 'rb')

SCORES = []
FMM_SCORES = []
FMM_YEAR = []
PAM_SCORES = []
PAM_DAYS = []

try:
    DICT_READER = csv.DictReader(MY_DATA, fieldnames=csv.reader(MY_DATA).next())
    for row in DICT_READER:
        SCORES.append(float(row['Scores']))
        #FMM record
        if funclib.read_number(row['IsFMM']) == 1:
            if funclib.is_float(row['yearhwL']) and funclib.is_float(row['Scores']):
                FMM_SCORES.append(float(row['Scores']))
                FMM_YEAR.append(float(row['yearhwL']))
        #PAM record
        if funclib.read_number(row['IsPaM']) == 1:
            if funclib.is_float(row['Scores']) and funclib.is_float(row['days_pa_km']):
                PAM_SCORES.append(float(row['Scores']))
                PAM_DAYS.append(float(row['days_pa_km']))
finally:
    MY_DATA.close

#Now do the stats work
PAM_CORRS = [['tau', 'p']]
FMM_CORRS = [['tau', 'p']]
FINAL_ITERS_PAM = [0]
FINAL_ITERS_FMM = [0]
FMM_GREATER = [0]
PAM_GREATER = [0]

if EXCLUDE_ZEROS:
    funclib.list_delete_value_pairs(PAM_SCORES, PAM_DAYS)
    funclib.list_delete_value_pairs(FMM_SCORES, FMM_YEAR)

if bool(int(RUN) & EnumData.pam.value):
    TAU, CONF = scipy.stats.kendalltau(PAM_SCORES, PAM_DAYS)
    PAM_CORRS.append([TAU, CONF])
    PAM_CORRS.extend(statslib.permuted_correlation(PAM_SCORES, PAM_DAYS, test_stat=TAU, out_greater_than_test_stat=PAM_GREATER, iterations=ITERATIONS, sem_mean_proportion=SEM, exclude_zero_pairs=EXCLUDE_ZEROS, out_final_iters=FINAL_ITERS_PAM))
    PAM_SUMMARY = 'Completed PAM after ' + str(FINAL_ITERS_PAM[0]) + ' iterations. p=' + str(round(PAM_GREATER[0]/FINAL_ITERS_PAM[0], 5))
    iolib.writecsv(get_file_name(EnumData.pam), PAM_CORRS, inner_as_rows=False)
    iolib.write_to_eof(get_file_name(EnumData.pam), PAM_SUMMARY)
    print PAM_SUMMARY

if bool(int(RUN) & EnumData.fmm.value):
    TAU, CONF = scipy.stats.kendalltau(FMM_SCORES, FMM_YEAR)
    FMM_CORRS.append([TAU, CONF])
    FMM_CORRS.extend(statslib.permuted_correlation(FMM_SCORES, FMM_YEAR, test_stat=TAU, out_greater_than_test_stat=FMM_GREATER, iterations=ITERATIONS, sem_mean_proportion=SEM, exclude_zero_pairs=EXCLUDE_ZEROS, out_final_iters=FINAL_ITERS_FMM))
    FMM_SUMMARY = 'Completed FMM after ' + str(FINAL_ITERS_FMM[0]) + ' iterations. p=' + str(round(FMM_GREATER[0]/FINAL_ITERS_FMM[0], 5))
    print FMM_SUMMARY
    iolib.writecsv(get_file_name(EnumData.fmm), FMM_CORRS, inner_as_rows=False)
    iolib.write_to_eof(get_file_name(EnumData.fmm), FMM_SUMMARY)

with fuckit:
    subprocess.check_call(['explorer', '.\\data'])