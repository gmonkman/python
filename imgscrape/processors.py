# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''my custom processors'''
from warnings import warn as _warn
import base64 as _base64
import unicodedata as _unicodedata
import funclib.stringslib as _stringslib
from bs4 import BeautifulSoup as _Soup
import nlp.clean as _clean




ISO_DATE_DEFAULT = '19000101 00:00:00'

#Processors
class Clean_xa0():
    '''replace nonprinting spaces with space'''
    def __call__(self, values):
        return [_stringslib.trim(_unicodedata.normalize('NFKD', s))  for s in values]


class Clean2Ascii():
    '''Remove crlf, retain ASCII, remove quotes
    values = ['a\nb','d!','?e']
    >>>Clean2Ascii(values)
    ['ab','d!','?e']
    '''
    def __call__(self, values):
        if values:
            if isinstance(values, list):
                s = " ".join(values)
            else:
                s = values
            return [_stringslib.filter_alphanumeric1(s, allow_cr=False, allow_lf=False, remove_double_quote=True, remove_single_quote=True, strip=True)]
        return []



class CleanStrict():
    '''leave only ascii alpha numerics
    This also strips CR and LF and all punctuation

    values = ['ab','d!','?e']
    >>>CleanStrict(values)
    ['ab','d','e']
    '''
    def __call__(self, values):
        if values:
            l = lambda x: _stringslib.filter_alphanumeric(x, strict=True, allow_cr=False, allow_lf=False, include=(' '))
            if len(values) == 1: #single string in list
                return ["".join([c for c in values[0] if l(c)])]
            return ["".join([c for c in val if l(c)]) for val in values]
        return []


class CleanStrict1():
    '''As clean strict, but uses the later version
    which is also used by nlp module - use to ensure
    same outputs. Removes crlf, and punctuation, leaves spaces

    We need to allow carriage returns for paragraph detection.

    values = ['ab','d!','?e']
    >>>CleanStrict1(values)
    ['ab','d','e']
    '''
    def __call__(self, allow_cr, values):
        if values:
            if isinstance(values, list):
                s = " ".join(values)
            else:
                s = values
            return [_stringslib.filter_alphanumeric1(s, strict=True, allow_cr=True, allow_lf=True, include=(' '))]
        return []


class VoteForOrAgainst():
    '''Custom rule to check
    if voted maingly for or against'''
    def __call__(self, values):
        for v in values:
            assert isinstance(v, str)
            if ' for ' in v:
                return ['voted for']

            if ' against ' in v:
                return ['voted against']

            return ['Unknown']


class UKDateAsISO():
    '''
    Get date as ISO.

    Expected format is UK, i.e. '%d/%m/%Y %H:%M'
    '''
    def __call__(self, v):
        if v:
            try: #dont fail if we get an invalid date
                s = _stringslib.date_str_to_iso(v)
            except Exception as _:
                s = ISO_DATE_DEFAULT
            return s
        return ISO_DATE_DEFAULT


class PostDateAsISO():
    '''
    Process angling addicts post date.

    Also does a strict clean to ascii,
   leaveing ":"  "/" and "-" but not ","
    '''
    def __init__(self, date_fmt='%x %H:%M'):
        self.date_fmt = date_fmt

    def __call__(self, v):
        if v:
            try:
                s = _stringslib.filter_alphanumeric1(v[0], strict=True, allow_cr=False, allow_lf=False, strip=True, include=(':', '/', '-'))
                return _stringslib.date_str_to_iso(s, self.date_fmt)
            except Exception as e:
                _warn('PostDateAsISO failed, using %s. Error was %s' % (ISO_DATE_DEFAULT, e))
                s = ISO_DATE_DEFAULT

            return s

        return ISO_DATE_DEFAULT



class HTML2Txt():
    '''turn html to text, turning <br> to newlines
    '''
    def __call__(self, v):
        #list or string is muddled, but just use it for now - really all these functions should work with a list and not strings, and they should return lists
        #could process further here, for example lower() it all, but caps will be used for sentence and proper name detection
        s = _Soup(v[0], 'html.parser').get_text('\n')
        s = _clean.to_ascii(s)
        s = _clean.strip_urls_list((s,))
        s = _stringslib.newline_del_multi(s[0]).lstrip().rstrip()
        return s


class ListToValue():
    '''convert lists to values
    '''
    def __call__(self, v):
        if isinstance(v, list):
            return v[0]
        return v


class Encode64():
    '''encode a string'''
    def __call__(self, v):
        if v:
            try:
                v = lst2val(v)
                s = _stringslib.filter_alphanumeric1(_base64.urlsafe_b64encode(bytes(v, 'utf8')), remove_single_quote=True, remove_double_quote=True, strip=True)
                return s[0:50]
            except Exception as _:
                return 'unknown'
        return 'unknown'


def lst2val(l):
    '''list to val'''
    if isinstance(l, list):
        return l[0]
    return l
