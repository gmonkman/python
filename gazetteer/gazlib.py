# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''custom funcs for interacting with the gazetteer
The gazetteer sources are:
dbo.geograph
dbo.gn_feature
dbo.LK
dbo.medin
dbo.os_gazetteer
dbo.os_open_name
dbo.ukho_gazetteer
dbo.ukho_seacover_wgs84
'''
import sqlalchemy
from sqlalchemy import and_, or_

from gazetteerdb.model import Gazetteer

import funclib.iolib as _iolib
import gazetteerdb as _gazetteerdb
import gazetteerdb.model as _model
import gazetteer.name_entities as _name_entities


assert isinstance(_gazetteerdb.SESSION, sqlalchemy.orm.Session)


def lookup(name, ifca=''):
    '''Model -> None|Query
    lookup on a Model class

    Example:
    >>>lookup(_model.t_v_geograph, name='My Place', ifca='Southern')
    '''
    if ifca:
        assert ifca.lower() in _name_entities.VALID_IFCAS
        rows = _gazetteerdb.SESSION.query(Gazetteer).filter_by(ifca=ifca, name=name)
        
    else:
        rows = _gazetteerdb.SESSION.query(Gazetteer).filter_by(name=name)
    return rows


def lookup_LK(name, ifca=''):
    '''-> None|Query
    lookup on v_LK'''
    if not ifca: ifca = True

    if ifca:
        rows = _gazetteerdb.SESSION.query(_model.t_v_LK).filter_by(ifca=ifca, name=name)
    else:
        rows = _gazetteerdb.SESSION.query(_model.t_v_geograph).filter_by(name=name)
    assert isinstance(rows, (None, sqlalchemy.orm.query.Query))
    return rows
