'''main init file for package opencvlib'''
import os.path as _path
import atexit as _atexit
from sqlalchemy.orm import sessionmaker as _sessmake

import dblib.alchemylib as _alc

import mmodb.ini as ini

__all__ = ['ini', 'mag', 'model']

print('Trying to connect to database %s.%s ....' % (ini.server, ini.dbname))
cnnstr = _alc.ConnectionString(ini.server, ini.dbname, ini.user, ini.password, use_integrated=ini.is_integrated)
_alc.create_engine_mssql(cnnstr)
ENGINE = _alc.ENGINE
SESSION = _sessmake()
SESSION.configure(bind=ENGINE, autocommit=False)



def close_engine():
    try:
        ENGINE.dispose()
    except:
        pass

_atexit.register((close_engine))