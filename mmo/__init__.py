'''main init file for package opencvlib'''
import dblib.alchemylib as _alc

import funclib.stringslib as _stringslib
import dblib.mssql as _mssql
import funclib.baselib as _baselib
import mmo.ini as ini

__all__ = ['ini', 'named_entities']



def clean(lst):
    '''clean list'''
    return  [_stringslib.filter_alphanumeric1(s, strict=True, remove_double_quote=True, remove_single_quote=True).lower() for s in lst]
