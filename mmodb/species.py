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


def get_species_as_dict_all():
    '''get species as a dict
    where the keys are the "proper" name
    and the values are lists of alias names

    Converts to lower() as loaded
    '''
    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_all')).fetchall()
    out = {}
    for r in rows:
        if out.get(r[0]):
            out[r[0]] += _clean([r[1]])
        else:
            out[r[0]] = _clean([r[1]])
    return out


def get_species_as_dict_unspecified():
    '''get species as a dict
    where the keys are the "proper" name
    and the values are lists of alias names

    Converts to lower() as loaded
    '''
    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_unspecified')).fetchall()
    out = {}
    for r in rows:
        if out.get(r[0]):
            out[r[0]] += _clean([r[1]])
        else:
            out[r[0]] = _clean([r[1]])
    return out


def get_species_as_dict_sans_unspecified():
    '''get species as a dict
    where the keys are the "proper" name
    and the values are lists of alias names

    Converts to lower() as loaded
    '''
    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_sans_unspecified')).fetchall()
    out = {}
    for r in rows:
        if out.get(r[0]):
            out[r[0]] += _clean([r[1]])
        else:
            out[r[0]] = _clean([r[1]])
    return out


def get_species_flatfish():
    '''gets the speciesid and aliases of all flatfish'''

    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_flatfish')).fetchall()
    out = {}
    for r in rows:
        if out.get(r[0]):
            out[r[0]] += _clean([r[1]])
        else:
            out[r[0]] = _clean([r[1]])
    return out


def get_species_skates_rays():
    '''gets the speciesid and aliases of all skates and rays'''

    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_skates_rays')).fetchall()
    out = {}
    for r in rows:
        if out.get(r[0]):
            out[r[0]] += _clean([r[1]])
        else:
            out[r[0]] = _clean([r[1]])
    return out

def get_species_sole():
    '''gets the speciesid and aliases of all sole'''

    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_sole')).fetchall()
    out = {}
    for r in rows:
        if out.get(r[0]):
            out[r[0]] += _clean([r[1]])
        else:
            out[r[0]] = _clean([r[1]])
    return out


def get_species_mullet():
    '''gets the speciesid and aliases of all mullet'''

    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_mullet')).fetchall()
    out = {}
    for r in rows:
        if out.get(r[0]):
            out[r[0]] += _clean([r[1]])
        else:
            out[r[0]] = _clean([r[1]])
    return out


def get_species_bream():
    '''gets the speciesid and aliases of all mullet'''

    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_bream')).fetchall()
    out = {}
    for r in rows:
        if out.get(r[0]):
            out[r[0]] += _clean([r[1]])
        else:
            out[r[0]] = _clean([r[1]])
    return out