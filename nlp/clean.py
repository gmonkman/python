# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''This module provides routines to expand word lists with alternate versions of words
'''
import re as _re
from warnings import warn as _warn

from text2digits import text2digits as _t2d
import funclib.baselib as _baselib
from funclib.stringslib import to_ascii, newline_del_multi, filter_alphanumeric1, non_breaking_space2space
import nlp.relib as _relib
import nlp.stopwords as _stopwords


def strip_urls_list(l, subst=' '):
    '''(list, str) -> str
    strip urls from a string
    l:list of strings
    subst:replacement
    '''
    if isinstance(l, str):
        raise ValueError('Expected iterable, got str')
    return [_re.sub(r'http\S+', '', s) for s in l]


def strip_urls_str(s, subst=' '):
    '''(list, str) -> str
    strip urls from a string
    l:list of strings
    subst:replacement
    '''
    if not isinstance(s, str):
        raise ValueError('Expected str, got %s' % typs(s))
    return _re.sub(r'http\S+', '', s)

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

    s = _relib.fix_repeat_spaces(s)
    s = _relib.fix_repeat_char(s, '.')
    return s


def txt2nr(s):
    '''convert text to digits'''
    T = _t2d.Text2Digits()
    return T.convert(s)


def sep_num_from_words(s):
    '''seperate words from number'''
    return _re.sub(r"([0-9]+(\.[0-9]+)?)",r" \1 ", s).strip()


def clean(s, tolower=False):
    '''str, set|None
    apply multiple clean funcs to s
    '''
    #the order of this matters
    if not s: return ''
    assert isinstance(s, str)
    s = non_breaking_space2space(s)
    s = strip_urls_str(s)
    s = sep_num_from_words(s)
    s = base_substitutons(s) #base substitutions would make urls unidentifiable
    s = s.replace("'", "")
    s = s.replace('"', '')
    s = s.replace('\n ', '\n')
    s = s.replace(' \n', '\n')    
    s = nlpclean.newline_del_multi(s)
    s = nlpclean.txt2nr(s)
    if tolower: s = s.lower()
    return s
