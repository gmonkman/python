# pylint: disable=pointless-statement
'''Main program to calculate correlation distribution
of my FMM and PAM data with my point coincident data
by 1km^2 grids.
Kendall's correlation coefficent is used
'''

#base
import csv

#third party
import scipy
import scipy.stats

#My Libs
import statslib
import funclib
import iolib

ITERATIONS = funclib.read_number(raw_input('Input iterations:'), 1000)
EXCLUDE_ZEROS = bool(funclib.read_number(raw_input("Exclude zero pairs (0 = include zero pairs, 1 = exclude zero pairs):"), 0))
MY_DATA = open('data\\all.csv', 'rb')
DICT_READER = csv.DictReader(MY_DATA, fieldnames=csv.reader(MY_DATA).next())
SCORES = []
FMM_SCORES = []
FMM_YEAR = []
PAM_SCORES = []
PAM_DAYS = []


try:
    for row in DICT_READER:
        SCORES.append(float(row['Scores']))
        #FMM record
        if funclib.is_float(row['YEAR']) and funclib.is_float(row['Scores']):
            FMM_SCORES.append(float(row['Scores']))
            FMM_YEAR.append(float(row['YEAR']))
        #PAM record
        if funclib.is_float(row['Scores']) and funclib.is_float(row['days_pa_km']):
            PAM_SCORES.append(float(row['Scores']))
            PAM_DAYS.append(float(row['days_pa_km']))
finally:
    MY_DATA.close

#Now do the stats work
PAM_CORRS = [['tau', 'p']]
FMM_CORRS = [['tau', 'p']]

TAU, CONF = scipy.stats.kendalltau(PAM_SCORES, PAM_DAYS)
PAM_CORRS.append([TAU, CONF])
PAM_CORRS.extend(statslib.permuted_correlation(PAM_SCORES, PAM_DAYS, ITERATIONS, exclude_zero_pairs=EXCLUDE_ZEROS))

TAU, CONF = scipy.stats.kendalltau(FMM_SCORES, FMM_YEAR)
FMM_CORRS.append([TAU, CONF])
FMM_CORRS.extend(statslib.permuted_correlation(FMM_SCORES, FMM_YEAR, ITERATIONS, exclude_zero_pairs=EXCLUDE_ZEROS))

iolib.writecsv('data\\pam_results.csv', PAM_CORRS, inner_as_rows=False)
iolib.writecsv('data\\fmm_results.csv', FMM_CORRS, inner_as_rows=False)
