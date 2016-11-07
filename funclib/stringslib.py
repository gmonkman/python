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


#region files and paths related

def add_right(s, char='/'):
    '''(str, str) -> str
    Appends suffix to string if it doesnt exist
    '''
    s = str(s)
    if not s.endswith(char):
        return s + char
    else:
        return s

def add_left(s, char):
    '''(str, str) -> str
    Appends prefix to string if it doesnt exist
    '''
    s = str(s)
    if not s.startswith(char):
        return char + s
    else:
        return s
#endregion
