# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''This module provides routines to expand word lists with alternate versions of words
'''
import re as _re

from text2digits import text2digits as _t2d

import funclib.stringslib as _stringslib
import funclib.baselib as _baselib
from funclib.stringslib import to_ascii, newline_del_multi, filter_alphanumeric1, non_breaking_space2space
from nlp.re import fix_multi_spaces
import nlp.stopwords as _stopwords



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


def base_substitutons(s):
    '''a set of base substitutions to improve sentence detection
    This includes substituting sentence delimiters to the full stop
    and then removing repeated full stops'''
    #careful with urls
    s = non_breaking_space2space(s)
    s = s.replace('/', ' or ')
    s = s.replace('\\', ' or ') #escaped
    s = s.replace('|', ' or ') #escaped
    s = s.replace(' & ', ' and ')
    s = s.replace('+', ' plus ')
    s = s.replace('@', ' at ')

    #sentence delimiters
    s = s.replace(';', '. ')
    s = s.replace('?', '. ')
    s = s.replace(',', '. ')
    s = s.replace('!', '. ')
    s = s.replace(':', '. ')

    s = _re.fix_repeat_spaces(s)
    s = _re.fix_repeat_char(s, '.')
    return s


def stop_words(s, not_a_stop_word=('the')):
    '''(str) -> str
    clean stop words'''
    stop_words = _stopwords.get(not_a_stop_word)
    word_tokens = word_tokenize(s)
    f = [w for w in word_tokens if not w in stop_words]
    return f


def txt2nr(s):
    '''convert text to digits'''
    T = _t2d.Text2Digits()
    return T.convert(s)

