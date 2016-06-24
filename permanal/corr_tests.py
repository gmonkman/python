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
import pandas as pd
import numpy as np

#My Libs
from enum import Enum
import statslib
import funclib
import iolib

def do_tests():
    datafile = 'data\\allNew.csv'
    results = results = [['test_type', 'desc', 'varname1', 'varname2','exclude zeros', 'teststat', 'p']]
    #Do PAM
    dic = statslib.correlation_test_from_csv(datafile, 'DaysPAFina', 'VenueCnt')
    results = [['Kendall', 'PAM', 'DaysPAFina', 'VenueCnt', 0, dic['teststat'], dic['p']]]
    
    dic = statslib.correlation_test_from_csv(datafile, 'DaysPAFina', 'VenueCnt')
    results.append([['Kendall', 'PAM', 'days_pa_km', 'VenueCnt', 0, dic['teststat'], dic['p']]])

    dic = statslib.correlation_test_from_csv(datafile, 'DaysPAFina', 'VenueCnt')
    results.append([['Kendall', 'PAM', 'days_pa_km', 'VenueCnt', 0, dic['teststat'], dic['p']]])
