# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''special funcs relating to species'''
from sqlalchemy.sql import text

import mmodb as _mmodb
import mmodb.model as _model
import funclib.iolib as _iolib




def get_species_as_dict():
    '''get species as a dict
    where the keys are the "proper" name
    and the values are lists of alias names
    '''
    rows = _mmodb.SESSION.query(_text('select speciesid, species_aliasid from v_species_all')).fetchall()
    out = {}
    for r in rows:
        out[r[0]] = r[1]
    return out

