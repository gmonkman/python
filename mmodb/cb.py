# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''special funcs relating to species'''
from sqlalchemy.sql import text as _text

import mmodb as _mmodb
import mmodb.model as _model
import funclib.iolib as _iolib
import funclib.stringslib as _stringslib


def _clean(lst):
    '''clean list'''
    return  [_stringslib.filter_alphanumeric1(s, strict=True, remove_double_quote=True, remove_single_quote=True).lower() for s in lst]



def get_cb():
    '''get species as a dict
    where the keys are the "proper" name
    and the values are lists of alias names

    Converts to lower() as loaded
    '''
    rows = _mmodb.SESSION.execute(_text('select distinct cb.boat from cb')).fetchall()
    return _read_to_list(rows)


def _read_rows_to_dict(rows):
    '''read rows'''
    out = {}
    for r in rows:
        key = r[0].lower()
        if out.get(key):
            out[key] += _clean([r[1]])
        else:
            out[key] = _clean([r[1]])
    return out


def _read_to_list(rows):
    '''read rows'''
    out = []
    for r in rows:
        out += _clean([r[0]])
    return out