# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''
Add lat and long WGS80 coords from BNG coords in SQL Server gazetteer.os_locator
'''
from convertbng.util import convert_lonlat
import sqlalchemy
from sqlalchemy import and_, func


import funclib.iolib as iolib

import gazetteerdb

from gazetteerdb.model import OsOpenName

window_size = 100  # or whatever limit you like
window_idx = 0

if __name__ == '__main__':
    assert isinstance(gazetteerdb.SESSION, sqlalchemy.orm.Session)
    n = gazetteerdb.SESSION.query(OsOpenName.os_open_namesid).count()
    PP = iolib.PrintProgress(n, bar_length=20)


    while True:
        start, stop = window_size * window_idx, window_size * (window_idx + 1)
        rows = gazetteerdb.SESSION.query(OsOpenName).order_by(OsOpenName.os_open_namesid).slice(start, stop).all()
        if rows is None:
            break
        for row in rows:
            res = convert_lonlat([row.geometry_x], [row.geometry_y])
            row.x = res[0][0]
            row.y = res[1][0]
        try:
            gazetteerdb.SESSION.commit()
        except:
            gazetteerdb.SESSION.rollback()

        if len(rows) < window_size:
            break

        window_idx += 1
        PP.increment(step=window_size, show_time_left=True)
