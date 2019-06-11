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
    return _read_rows(rows)


def get_species_as_dict_unspecified():
    '''get species as a dict
    where the keys are the "proper" name
    and the values are lists of alias names

    Converts to lower() as loaded
    '''
    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_unspecified')).fetchall()
    return _read_rows(rows)

def get_species_as_dict_sans_unspecified():
    '''get species as a dict
    where the keys are the "proper" name
    and the values are lists of alias names

    Converts to lower() as loaded
    '''
    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_sans_unspecified')).fetchall()
    return _read_rows(rows)

def get_species_flatfish():
    '''gets the speciesid and aliases of all flatfish'''
    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_flatfish')).fetchall()
    return _read_rows(rows)

def get_species_skates_rays():
    '''gets the speciesid and aliases of all skates and rays'''
    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_skates_rays')).fetchall()
    return _read_rows(rows)

def get_species_sole():
    '''gets the speciesid and aliases of all sole'''
    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_sole')).fetchall()
    return _read_rows(rows)

def get_species_mullet():
    '''gets the speciesid and aliases of all mullet'''
    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_mullet')).fetchall()
    return _read_rows(rows)

def get_species_bream():
    '''gets the speciesid and aliases of all mullet'''
    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_bream')).fetchall()
    return _read_rows(rows)



def get_species_flatfish_unspecified():
    '''gets the speciesid and aliases of all flatfish'''
    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_flatfish_unspecified')).fetchall()
    return _read_rows(rows)

def get_species_skates_rays_unspecified():
    '''gets the speciesid and aliases of all skates and rays'''
    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_skates_rays_unspecified')).fetchall()
    return _read_rows(rows)

def get_species_sole_unspecified():
    '''gets the speciesid and aliases of all sole'''
    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_sole_unspecified')).fetchall()
    return _read_rows(rows)

def get_species_mullet_unspecified():
    '''gets the speciesid and aliases of all mullet'''
    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_mullet_unspecified')).fetchall()
    return _read_rows(rows)

def get_species_bream_unspecified():
    '''gets the speciesid and aliases of all mullet'''
    rows = _mmodb.SESSION.execute(_text('select speciesid, species_aliasid from v_species_bream_unspecified')).fetchall()
    return _read_rows(rows)





def _read_rows(rows):
    '''read rows'''
    out = {}
    for r in rows:
        key = r[0].lower()
        if out.get(key):
            out[key] += _clean([r[1]])
        else:
            out[key] = _clean([r[1]])
    return out
