# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''basic metrics on sentences/words'''


import funclib.stringslib as _stringslib
from nltk.corpus import wordnet as _wordnet

def _clean_str(s):
    if s:
        s = s.replace('\n', ' ')
        s = s.replace(' & ', ' and ')
        s = s.strip()
    return s


def word_length_mean(s):
    '''(str) -> float|None
    Return mean word length using crude split() only

    Examples:
    >>>word_length_mean('asdf asdfgh')
    2

    >>>word_length_mean('')
    None
    '''
    assert isinstance(s, str), 's should be a string. Got %s' % type(s)
    s = _clean_str(s)
    words = s.split()
    if words:
        return sum(len(word) for word in words) / len(words)
    return None


def word_count(s):
    '''(str) -> int
    Count words in string using crude split()
    '''
    assert isinstance(s, str), 's should be a string. Got %s' % type(s)
    if s:
        s = _clean_str(s)
        return len(s.split())
    return 0


def nonalpha_density_by_char(s, dont_count_numbers=True):
    '''(str, bool) -> float|None
    Density of non-alphanumeric characters in a string, by
    total character count. ie. len(alpha count) / len(s)

    An all nonalpha string returns float("inf")

    Parameters:
        s: the string to check
        numeric_is_nonalpha: is a number counted as alpha

    Example:
    >>>nonalpha_density_by_char('!!ABCD')
    0.333

    >>>nonalpha_density_by_char('!!')
    inf
    '''
    assert isinstance(s, str), 's should be a string. Got %s' % type(s)
    if not s: return None
    s = _clean_str(s)
    alphas = _stringslib.filter_alphanumeric1(s, remove_single_quote=False, strict=True, remove_double_quote=False, allow_cr=False, allow_lf=False, exclude_numbers=dont_count_numbers)
    if alphas:
        return (len(s) - len(alphas)) / len(s)
    return float('inf')


def nonalpha_density_by_word(s):
    '''(str) -> float

    Returns nr non alpha chars per valid word, using
    a wordnet lookup.

    Returns float("inf") if there are alphas but no words

    Example:
    >>>nonalpha_density_by_word('This is valid!!!!!')
    '''
    assert isinstance(s, str), 's should be a string. Got %s' % type(s)
    if not s: return None
    s = _clean_str(s)
    alphas = _stringslib.filter_alphanumeric1(s, remove_single_quote=False, strict=True, remove_double_quote=False, allow_cr=False, allow_lf=False, exclude_numbers=True)
    if alphas:
        nonalpha_nr = len(s) - len(alphas)
        words = alphas.split() #alphas should have the shit removed from it, eg "valid!!!" will be "valid"
        return (len(s) - len(alphas)) / sum([1 for w in words if _wordnet.synsets(w)])
    return float("inf")


def word_density(s):
    '''(str) -> float

    Returns density of valid words in string s using
    a wordnet lookup

    Examples:
    >>>word_density('This asdasf is valid')
    0.75
    >>>word_density('awert asdasf')
    0
    >>>word_density('perfect sentence')
    1
    '''
    assert isinstance(s, str), 's should be a string. Got %s' % type(s)
    if not s: return 0
    s = _clean_str(s)
    if s:
        alphas = _stringslib.filter_alphanumeric1(s, remove_single_quote=False, strict=True, remove_double_quote=False, allow_cr=False, allow_lf=False, exclude_numbers=True)
        if alphas:
            words = alphas.split()
            return sum([1 for w in words if _wordnet.synsets(word_count)]) / len(words)
    return 0


def alpha_density(s, dont_count_numbers=True):
    '''(str, bool) -> float|None
    Density of strict alpha characters (a-Z) in s
    Just recipricol of nonalpha_density_by_char

    Parameters:
        s: the string to check
        numeric_is_nonalpha: is a number counted as alpha

    Example:
    >>>nonalpha_density_by_char('!!ABCD')
    0.6666
    '''
    assert isinstance(s, str), 's should be a string. Got %s' % type(s)
    if s:
        return 1 / nonalpha_density_by_char(s, dont_count_numbers)
    return None


def  digit_density(s):
    '''(str) -> float
    Density of digits (i.e. 0-9) in s
    '''
    if s:
        s = _clean_str(s)
        if s:
            return len(_stringslib.filter_numeric1(s)) / len(s)
        return 0

    return None

