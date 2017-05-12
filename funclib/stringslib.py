# pylint: skip-file
'''string manipulations and related helper functions'''

# base imports
import time
import numbers

# my imports
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
    else:  # not a string or not a number
        return default


# region files and paths related
def filter_alphanumeric(char, to_ascii=True, strict=False, allow_cr=True, allow_lf=True, exclude=(), include=(), replace_ampersand='and'):
    '''(str, bool, bool, bool, bool, tuple, tuple) -> bool
    Use as a helper function for custom string filters
    for example in scrapy item processors

    to_ascii : bool
        replace foreign letters to ASCII ones, e.g, umlat to u

    strict : bool
        only letters and numbers are returned

    allow_cr, allow_lf : bool
        include or exclude cr lf

    exclude,include : tuple(str,..)
        force true or false for passed chars

    Example:
    l = lambda x: _filter_alphanumeric(x, strict=True)
    s = [c for c in 'abcef' if l(c)]

    '''
    if char in exclude: return False
    if char in include: return True

    if replace_ampersand:
        char = char.replace('&', 'and')
    if to_ascii:
        char = char.encode('ascii', 'ignore')

    if allow_cr and ord(char) == 13: return char
    if allow_lf and ord(char) == 10: return char


    if strict:
        return 48 <= ord(char) <= 57 or 65 <= ord(char) <= 90 or 97 <= ord(char) <= 122 or ord(char) == 32 #32 is space
    else:
        return 32 <= ord(char) <= 126



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


def trim(s, trim=' '):
    '''(str,str) -> str
    remove leading and trailing chars

    trim('12asc12','12)
    >>>'asc'
    '''
    assert isinstance(s,str)


    while s[0:len(trim)] == trim:
        s = s.lstrip(trim)

    while s[len(s)-len(trim):len(s)] == trim:
        s = s.rstrip(trim)

    return s


def rreplace(s, match, replacewith, cnt=1):
    '''(str,str,str,int)->str'''
    return replacewith.join(s.rsplit(match, cnt))
# endregion
