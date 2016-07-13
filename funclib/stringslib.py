'''string manipulations and related helper functions'''

#base imports
import time
import numbers

#my imports
import funclib.numericslib

def datetime_stamp(datetimesep=''):
    '''(str) -> str
    Returns clean date-time stamp for file names etc
    e.g 01 June 2016 11:23 would be 201606011123
    str is optional seperator between the date and time
    '''
    fmtstr = '%Y%m%d' + datetimesep + '%H%m%S'
    return time.strftime(fmtstr)

def read_number(test, default=0):
    '''(any,number) -> number
    Return test if test is a number, or default if s is not a number
    '''
    if isinstance(test, str):
        if funclib.numericslib.is_float(test):
            return float(test)
        else:
            return default
    elif isinstance(test, numbers.Number):
        return test
    else:   #not a string or not a number
        return default
