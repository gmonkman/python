# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''my custom processors'''

import unicodedata as _unicodedata



import funclib.stringslib as _stringslib



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
        else:
            return []

class VoteForOrAgainst():
    '''Custom rule to check
    if voted maingly for or against'''
    def __call__(self, values):
        for v in values:
            assert isinstance(v, str)
            if ' for ' in v:
                return ['voted for']
            elif ' against ' in v:
                return ['voted against']
            else:
                return ['Unknown']
