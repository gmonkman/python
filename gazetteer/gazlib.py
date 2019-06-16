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
from sqlalchemy import text as _text

from gazetteerdb.model import Gazetteer

import funclib.iolib as _iolib
import gazetteerdb as _gazetteerdb
import gazetteerdb.model as _model
import gazetteer.name_entities as _name_entities
from funclib.numericslib import round_normal as _rnd
import nlp.clean as _clean
assert isinstance(_gazetteerdb.SESSION, sqlalchemy.orm.Session)


def lookup(name, ifca='', as_str=False, include_any_ifca=False):
    '''Model -> None|Query
    lookup on a Model class.

    ifca:lookup on ifca, if empty, any ifca is matched
    as_list: return a formatted list, not an SQLAlchemy rows object
    include_any_ifca: if there is no match with an ifca lookup, try any match

    Example:
    >>>lookup(_model.t_v_geograph, name='My Place', ifca='Southern', include_any_ifca=False)
    '''
    name = name.lower()

    if ifca:
        ifca = ifca.lower()
        assert ifca in _name_entities.VALID_IFCAS
        rows = _gazetteerdb.SESSION.query(Gazetteer).filter_by(ifca=ifca, name=name)
        if rows.count() == 0:
            rows = _gazetteerdb.SESSION.query(Gazetteer).filter_by(name=name)
    else:
        rows = _gazetteerdb.SESSION.query(Gazetteer).filter_by(name=name)
    
    if as_str:
        if rows.count() > 0:
            f = [(w.gazetteerid, w.name, w.ifca).__repr__() for w in rows]
            return '\t'.join(f)
        else:
            return 'NOT FOUND'
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



def add(source, name, feature_class, x, y):
    '''add an entry to the gazetteer'''
    #an sql server trigger assigns the ifca automatically and adds a record to the gazetteer_geog table
    row = _gazetterdb.SESSION.query(_text('select max(id) + 1 as id from gazetteer')).fetchall()
    cln = _clean.clean(name)
    G = Gazetteer(source=source, name=name, feature_class='', feature_class1='', x=x, y=y, x_rnd=_rnd(x,1), y_rnd=_rnd(y,1), id=row[0], name_cleaned=cln)
    _gazetterdb.SESSION.add(G)
    _gazetteerdb.SESSION.commit()


if __name__ == '__main__':
    lookup('sutton', as_str=True)
    lookup('chilling spit', 'eastern', as_str=True)
    pass
