# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, anomalous-backslash-in-string
#TODO Move this whole thing to stringslib
'''regular expression based functions'''
import re as _re
import funclib.stringslib as _stringslib


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


def fix_repeat_char(s, char):
    '''(str, str) -> str
    remove repeated chars

    Example:
    >>>fix_repeat_char('!!!!', '!')
    !
    '''
    expr = r'\%s{2,}' % char
    return _re.sub(expr, char, s)


def has_word(sentence, word):
    '''str, str
    Is word in s
    '''
    src = r'(?=.*\b%s\b)' % word
    exp = _re.compile(src, _re.IGNORECASE)
    mtc = exp.search(sentence)
    if mtc: return True
    return False



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


def replace_all_punctuation_with_char(s, char):
    '''replace all punc with fullstop'''
    return _re.sub(r'[^\w\s]', char, s)

def SentenceHasTextAndNumber(sentence, word, no_left_boudary=True, no_right_boundary=True):
    '''str, str->bool
    Does word appear in sentence with a number
    sentence:the sentence
    word: word strint  to match, can be a phrase
    no_left_boundary, no_right_boundary: allow numbers to be detected if not on a word boundary where a word boundary is a whitespace char.

    '''
    s = r'(?=.*\b%s\b)(?=.*%s(?:[1-9](?:\d{0,10})(?:,\d{10})*(?:\.\d*[1-9])?|0?\.\d*[1-9]|0)%s)' % (word, r'' if no_left_boundary else r'\b', r'' if no_right_boudary else r'\b')
    reg = _re.compile(s, _re.IGNORECASE)
    mtc = reg.search(sentence)
    return True if mtc else False

def SentenceIsMatchAndHasNumeric(sentence, word, otherwords=(), no_left_boudary=True, no_right_boundary=True):
    '''check if sentence has number, thetext and any of otherwords'''
    if not any([has_word(sentence, w) for w in otherwords]):
        return False
    return SentenceHasTextAndNumber(sentence, word, no_left_boudary, no_right_boundary)

def SentenceHasTextMulti(sentence, words):
    return any([has_word(sentence, w) for w in words])


def CheckDistanceAnyNumber(sentence, word, distance, anyorder=True):
    '''(str, str, int, bool)
    does word appear within <distance> words of a numberic
    '''
    a = r"\b(?:[1-9](?:\d{0,10})(?:,\d{10})*(?:\.\d*[1-9])?|0?\.\d*[1-9]|0)\W+(?:\w+\W+){0,%s}?%s\b" % (distance, word)
    #print(a)
    b = r"\b%s\W+(?:\w+\W+){0,%s}(?:[1-9](?:\d{0,10})(?:,\d{10})*(?:\.\d*[1-9])?|0?\.\d*[1-9]|0)\b" % (word, distance)
    reFL = _re.compile(a, _re.IGNORECASE)
    reLF = _re.compile(b, _re.IGNORECASE)
    m = reFL.search(sentence)
    n = reLF.search(sentence)
    if anyorder:
        if m or n:
            return True
        return False
        
    if m:
        return True
    return False


def CheckDistanceAnyNumberMultiText(sentence, words, distance, anyorder=True):
    return any([CheckDistanceAnyNumber(sentence, w, distance, anyorder) for w in words])