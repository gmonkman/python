# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, anomalous-backslash-in-string
#TODO Move this whole thing to stringslib
'''regular expression based functions'''
import re as _re


def fix_repeat_spaces(s, tab_and_newlines_are_spaces=False):
    '''(str, bool) -> str
    Remove repeated spaces
    tab_and_newlines_are_spaces: consider tab and newlines as spaces
    Example:
    >>>fix_repeat_spaces('The  fox \n\t is dead', True)
    'The fox is dead'

    >>>fix_repeat_spaces('The  fox \n\t is dead', False)
    'The fox is \n\t is dead'
    '''
    if tab_and_newlines_are_spaces:
        return _re.sub('\s{2,}', ' ', s)
    return _re.sub(' +', ' ', s)


def fix_repeat_char(s, char, tab_and_newlines_are_spaces=False):
    '''(str, str) -> str
    remove repeated chars

    Example:
    >>>fix_repeat_char('!!!!', '!')
    !
    '''
    if tab_and_newlines_are_spaces:
        return _re.sub(r'\s{2,}', ' ', s)
    expr = '%s+' % char
    return _re.sub(expr, char, s)


def get_indices(s, find):
    '''(str, str) -> list
    Get indices of find in s

    Example:
    >>>get_indices('asdf 12 12 as 12', '12')
    [5, 8, 14]
    '''
    exp = '\\b%s\\b' % find
    return [m.start(0) for m in _re.finditer(exp, s)]


def replace_whole_word(s, find_, replacement_):
    '''replace whole word in string s
    Example:
    >>>replace_whole_word('this is shite', 'is', 'was')
    this was shite
    '''
    return _re.sub(r'\b' + find_ + r'\b', replacement_, s)