# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''This module provides routines to expand word lists with alternate versions of words
'''
import funclib.stringslib as _stringslib
import funclib.baselib as _baselib

from text2digits import t2d



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
    T = t2d.Text2Digits()

    s = t2d(s)

