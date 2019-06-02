# pylint: skip-file
'''string manipulations and related helper functions'''

# base imports
import re as _re
import time
import numbers
import random as _random
import string as _string
import datetime as _datetime
# my imports
import funclib.numericslib
from funclib.numericslib import round_normal as _rndnorm



ascii_punctuation = ['!', '"', '#', '$', '%', '&', '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '¦', '}', '~', "'"]
ascii_punctuation_strict = ['!', '"', '(', ')', ',', '-', '.', ':', ';', '?', "'"]
ascii_and = ['&', '+']
ascii_or = ['|']


def plus_minus():
    '''get plus minus'''
    return u"\u00B1"


def non_breaking_space2space(s, replace_with=' '):
    '''replace non breaking spaces'''
    return s.replace(s, replace_with)


class Visible():
    visible_strict_with_space = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '
    visible_strict_sans_space = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'


    @staticmethod
    def ord_dict(with_space=False):
        '''(bool) -> dict
        Get dictionary of printable chars
        with their ord number as the key
        '''
        s = Visible.visible_strict_with_space if with_space else Visible.visible_strict_sans_space
        dic = {ord(value): value for value in s}
        return dic


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


def rndstr(l):
    '''(int) -> str
    Return random alphanumeric string of length l

    l:
        string length

    Example:
        >>>rndstr(3)
        A12
        >>>rndstr(5)
        DeG12
    '''
    return  ''.join(_random.choice(_string.ascii_uppercase + _string.ascii_lowercase + _string.digits) for _ in range(l))


def filter_alphanumeric1(s, encoding='ascii', strict=False, allow_cr=True, allow_lf=True, exclude=(), include=(), replace_ampersand='and', remove_single_quote=False, remove_double_quote=False, exclude_numbers=False, strip=False, fix_nbs=True):
    '''(str|bytes, bool, bool, bool, bool, tuple, tuple) -> str
    Pass a whole string/bytes, does the whole string!

    to_ascii: replace foreign letters to ASCII ones, e.g, umlat to u
    strict: only letters and numbers are returned, space is allowed
    allow_cr, allow_lf: include or exclude cr lf
    exclude,include : tuple(str,..), force true or false for passed chars
    replace_ampersand: replace "&" with the argument
    remove_single_quote: remove single quote from passed string
    remove_double_quote: remove double quote from passed string

    Example:
    >>>filter_alphanumeric('asd^!2', strict=True)
    asd2
    '''
    if not s: return s

    if isinstance(s, bytes):
        s = s.decode(encoding, 'ignore')

    if fix_nbs:
        s = non_breaking_space2space(s, ' ')

    if exclude_numbers:
        lst = list(exclude)
        _ = [lst.extend([i]) for i in range(10)]

    if remove_single_quote:
        s = s.replace("'", "")
    if remove_double_quote:
        s = s.replace('"', '')
    if replace_ampersand:
        s = s.replace('&', replace_ampersand)

    build = []
    for c in s:
        keep = filter_alphanumeric(c, strict, allow_cr, allow_lf, exclude, include)
        if keep:
            build.append(c)
    out = ''.join(build)
    if strip:
        out = out.lstrip().rstrip()
    return out



def filter_numeric1(s, encoding='ascii'):
    '''(str, str) -> str
    Filter out everything but digits from s

    Parameters:
        s: str to process
        encoding: a vald encoding string, e.g. 'utf8' or 'ascii' if isinstance(s, bytes)
    '''
    if isinstance(s, bytes):
        s = s.decode(encoding, 'ignore')
    out = [c for c in s if filter_numeric(c)]
    return ''.join(out)


def filter_numeric(char):
    '''(char(1)) -> bool
    As filter_alphanumeric, but just digits.
    Expects a length 1 string

    Example:
    >>>filter_numeric('1')
    True

    >>>filter_numeric('a')
    False
    '''
    return 48 <= ord(char) <= 57


# region files and paths related
def filter_alphanumeric(char, strict=False, allow_cr=True, allow_lf=True, exclude=(), include=()):
    '''(char(1), bool, bool, bool, bool, tuple, tuple) -> bool
    Use as a helper function for custom string filters.

    Note: Accepts a single char. Use filter_alphanumeric1 for varchar

    for example in scrapy item processors

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
    if not char: return char
    if char in exclude: return False
    if char in include: return True

    if allow_cr and ord(char) == 13: return True
    if allow_lf and ord(char) == 10: return True

    if not allow_cr and ord(char) == 13: return False
    if not allow_lf and ord(char) == 10: return False

    if not char: return char
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


def get_between(s, first, last):
    '''(str, str, str) -> str
    Gets text between first and last, searching from the left

    s:
        String to search
    first:
        first substring
    last:
        last substring
    '''
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ''


def get_between_r(s, first, last ):
    '''(str, str, str) -> str
    Gets text between first and last, searching from the right

    s:
        String to search
    first:
        first substring
    last:
        last substring
    '''
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ''

def to_ascii(s):
    '''(byte|str) -> str

    Takes a string or bytes representation of
    a string and returns an ascii encoded
    string.
    '''
    if isinstance(s, bytes):
        return s.decode('ascii', 'ignore')

    return s.encode('ascii', 'ignore').decode('ascii')


def newline_del_multi(s):
    '''replaces multiple newlines with single one'''
    s = s.replace('\r', '\n')
    s = _re.sub('\n+','\n', s)
    return s


# endregion


#time stuff
def time_pretty(seconds):
    '''(float) -> str
    Return a prettified time interval
    for printing
    '''
    sign_string = '-' if seconds < 0 else ''
    seconds = abs(_rndnorm(seconds))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%s%dd %dh %dm %ds' % (sign_string, days, hours, minutes, seconds)
    if hours > 0:
        return '%s%dh %dm %ds' % (sign_string, hours, minutes, seconds)
    if minutes > 0:
        return '%s%dm %ds' % (sign_string, minutes, seconds)

    return '%s%ds' % (sign_string, seconds)


def date_str_to_iso(s, fmt='%d/%m/%Y %H:%M'):
    '''Return ISO formatted date as string
    Set fmt according to string input, as described at
    http://strftime.org/

    The default set is uk format, eg 1/12/2019 12:23

    Example:
    >>>date_str_to_iso('1/5/2019 12:13')
    '20190501 12:13:00'
    '''
    return   _datetime.datetime.strptime(s, fmt).strftime('%Y%m%d %H:%M:%S')
