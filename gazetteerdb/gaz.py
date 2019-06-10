# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''special funcs relating to gazetteer'''
from sqlalchemy.sql import text as _text

import gazetteerdb as _gazetteerdb
import gazetteerdb.model as _model
import funclib.iolib as _iolib
import funclib.stringslib as _stringslib


def _clean(lst):
    '''clean list'''
    return  [_stringslib.filter_alphanumeric1(s, strict=True, remove_double_quote=True, remove_single_quote=True).lower() for s in lst]


def get_by_ifca(ifca):
    '''get ifca
    ifca can be str or list
    '''

    if isinstance(ifca, str): ifca = [ifca]

    ss = "' union select '".join(ifca)
    ss = "select '" + ss + "') "
    sql = 'select max(gazetteerid),ifca, name from gazetteer where ifca in (' + ss + ' and (eng_dist_m=0 and coast_dist_m < 1000) or eng_dist_m > 0 group by name, ifca'
    rows = _gazetteerdb.SESSION.execute(_text(sql)).fetchall()
    return _read_rows(rows)


def get_all_as_set():
    sql = 'select name from gazetteer where coast_dist_m > 1000 and eng_dist_m=0'
    rows = _gazetteerdb.SESSION.execute(_text(sql)).fetchall()
    out = {row[0] for row in rows}
    return out


def _read_rows(rows):
    '''read rows'''
    out = {}
    for r in rows:
        key = r[2].lower()
        if out.get(key):
            out[key] += [r[2].lower()]
        else:
            out[key] = [r[2].lower()]
    return out
