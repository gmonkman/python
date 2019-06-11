'''main init file for package opencvlib'''
import os.path as _path
import atexit as _atexit
from sqlalchemy.orm import sessionmaker as _sessmake
from sqlalchemy.orm import Session as _Session
import dblib.alchemylib as _alc

import mmodb.ini as ini

__all__ = ['ini', 'model']

print('Trying to connect to database %s.%s ....' % (ini.server, ini.dbname))
cnnstr = _alc.ConnectionString(ini.server, ini.dbname, ini.user, ini.password, use_integrated=ini.is_integrated).mssql_connection_string()
_alc.create_engine_mssql(cnnstr)
ENGINE = _alc.ENGINE
SESSION_MAKER = _sessmake()
SESSION_MAKER.configure(bind=ENGINE, autocommit=False)
SESSION = SESSION_MAKER()
assert isinstance(SESSION, _Session) #try and get intellisense to pick this up


def close_engine():
    try:
        SESSION.commit()
        ENGINE.dispose()
    except:
        pass

_atexit.register((close_engine))
