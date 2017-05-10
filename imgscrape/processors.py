# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''my custom processors'''

import unicodedata as _unicodedata



import funclib.stringslib as _stringslib



#Processors
class Clean_xa0():
    '''replace nonprinting spaces with space'''
    def __call__(self, values):
        return [_stringslib.trim(_unicodedata.normalize('NFKD', s))  for s in values]
