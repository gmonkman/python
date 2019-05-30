# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''This module provides routines to expand word lists with alternate versions of words
'''
import re as _re
import funclib.stringslib as _stringslib
import funclib.baselib as _baselib
from funclib.stringslib import to_ascii

from text2digits import text2digits as _t2d


#See https://blog.scrapinghub.com/2015/11/09/parse-natural-language-dates-with-dateparser
#for a (probably) better DateParser
def to_numerics(s):
    '''str->str

    Take a string, convert text to numbers

    Example:
    to_numerics('forty five')
    '45'
    '''
    try:
        s = w2n.word_to_num(s)
    except Exception as _:
        pass
    T = _t2d.Text2Digits()

    s = T(s)


def strip_urls_list(l, subst=' '):
    '''(list, str) -> str
    strip urls from a string
    l:list of strings
    subst:replacement
    '''
    if isinstance(l, str):
        raise ValueError('Expected iterable, got str')
    return [_re.sub(r'http\S+', '', s) for s in l]


def to_ascii_list(l):
    '''(list, str) -> str
    convert list elements to ascii
    l:iterable of strings
    '''
    if isinstance(l, str):
        raise ValueError('Expected iterable, got str')
    return [to_ascii(s) for s in l]