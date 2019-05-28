# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''my custom processors'''
import base64 as _base64
import unicodedata as _unicodedata
import funclib.stringslib as _stringslib
from bs4 import BeautifulSoup as _Soup


ISO_DATE_DEFAULT = '19000101 00:00:00'

#Processors
class Clean_xa0():
    '''replace nonprinting spaces with space'''
    def __call__(self, values):
        return [_stringslib.trim(_unicodedata.normalize('NFKD', s))  for s in values]


class CleanStrict():
    '''leave only ascii alpha numerics
    This also strips CR and LF and all punctuation

    values = ['ab','d!','?e']
    >>>CleanStrict(values)
    ['ab','d','e']
    '''
    def __call__(self, values):
        if values:
            l = lambda x: _stringslib._filter_alphanumeric(x, strict=True, allow_cr=False, allow_lf=False, include=(' '))
            if len(values) == 1: #single string in list
                return ["".join([c for c in values[0] if l(c)])]
            return ["".join([c for c in val if l(c)]) for val in values]

        return []


class CleanStrict1():
    '''As clean strict, but uses the later version
    which is also used my nlp module - use to ensure
    same outputs.

    We need to allow carriage returns for paragraph detection.

    values = ['ab','d!','?e']
    >>>CleanStrict1(values)
    ['ab','d','e']
    '''
    def __call__(self, allow_cr, values):
        if values:
            l = lambda x: _stringslib.filter_alphanumeric1(x, strict=True, allow_cr=allow_cr, allow_lf=False, include=(' '))
            if len(values) == 1: #single string in list
                return ["".join([c for c in values[0] if l(c)])]
            return ["".join([c for c in val if l(c)]) for val in values]
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


class AnglingAddictsPostDateAsISO():
    '''
    Process angling addicts post date

    Date format expected is '%d %b %Y, %H:%M'
    '''
    def __call__(self, v):
        if v:
            try:
                s = _stringslib.filter_alphanumeric1(v[0], strict=True, allow_cr=False, allow_lf=False, strip=True, include=(':'))
                s = _stringslib.date_str_to_iso(s, '%d %b %Y %H:%M')
            except Exception as _:
                s = ISO_DATE_DEFAULT

            return s

        return ISO_DATE_DEFAULT


class HTML2Txt():
    '''turn html to text, turning <br> to newlines
    '''
    def __call__(self, v):
        if v:
            try:
                #could process further here, for example lower() it all, but caps will be used for sentence and proper name detection
                s = _Soup(v[0], 'html.parser').get_text('\n')
                s = _stringslib.newline_del_multi(s).lstrip().rstrip()
                if not s:
                    s = ''
            except Exception as _:
                s = ''
            return s

        return ''


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
                return s
            except Exception as _:
                return 'unknown'
        return 'unknown'


def lst2val(l):
    if isinstance(l, list):
        return l[0]
    return l
