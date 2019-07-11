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
from warnings import warn as _warn

import sqlalchemy
from sqlalchemy import text as _text


from gazetteerdb.model import Gazetteer
import gazetteerdb as _gazetteerdb
import gazetteer.name_entities as _name_entities
from funclib.numericslib import round_normal as _rnd
import nlp.clean as _clean
assert isinstance(_gazetteerdb.SESSION, sqlalchemy.orm.Session)


def lookup(name, ifca='', as_str=False, include_any_ifca=False, include_name_in_output=False):
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
            if include_name_in_output:
                f = [','.join((name, str(w.gazetteerid), w.name, str(_rnd(w.x, 4)), str(_rnd(w.y, 4)), w.ifca)) for w in rows]
            else:
                f = [','.join((str(w.gazetteerid), w.name, str(_rnd(w.x, 4)), str(_rnd(w.y, 4)), w.ifca)) for w in rows]
            return '\t'.join(f)
        if include_name_in_output:
            return '%s,NOT FOUND' % name
        return 'NOT FOUND'

    return rows




def add(source, name, x, y, feature_class='', feature_class1='', unique_only=False):
    '''(str, str, str, float, float, bool) -> int|None
    add an entry to the gazetteer, returns the added id
    otherwise returns none if nothing added

    NB:IFCA is set automatically

    Example:
    >>>add('GGM', 'Hartley Skier', -1.4572, 55.0745, unique_only=True)
    123534
    '''
    #an sql server trigger assigns the ifca automatically and adds a record to the gazetteer_geog table
    cln = _clean.clean(name)
    sql = "select 1 as one from gazetteer where name='%s'" % cln
    
    if unique_only:
        row = _gazetteerdb.SESSION.execute(_text(sql)).fetchall()
        if row: return None

    row = _gazetteerdb.SESSION.execute(_text('select max(id) + 1 as id from gazetteer')).fetchall()
    
    G = Gazetteer(source=source, name=name, feature_class=feature_class, feature_class1=feature_class1, x=x, y=y, x_rnd=_rnd(x, 1), y_rnd=_rnd(y, 1), id=row[0][0], name_cleaned=cln)
    _gazetteerdb.SESSION.add(G)
    try:
        _gazetteerdb.SESSION.commit()
    except Exception as e:
        try:
            _warn('Add failed, error:\t%s' % e)
            _gazetteerdb.SESSION.rollback()
        except:
            pass
    else:
        try:
            row = _gazetteerdb.SESSION.execute(_text("select max(gazetteerid) AS 'Identity' from gazetteer")).fetchall()
        except:
            return None

    return row[0][0]
    


if __name__ == '__main__':
    #lookup('sutton', as_str=True)
    #lookup('chilling spit', 'eastern', as_str=True)
    #id_ = add('GGM', 'Hartley Skier', -1.4572, 55.0745, unique_only=True)
    #print(id)
    pass
