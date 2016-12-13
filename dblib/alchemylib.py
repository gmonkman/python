#pylint: disable=C0302, too-many-branches, dangerous-default-value, line-too-long, no-member, expression-not-assigned, locally-disabled, not-context-manager
'''helper function for database connections
including sqlalchemy
'''
import os

import sqlalchemy.pool as pool
from sqlalchemy import create_engine
import fuckit

from funclib.baselib import isPython2
from enum import Enum
from funclib.baselib import isPython3

if isPython2():
    from urllib import quote_plus
else:
    from urllib.parse import quote_plus

ENGINE = None

#TODO Expand supported connection types - enumeration
class DBType(Enum):
    '''database types'''
    mssql = 1

class MSSQLODBCDriver(Enum):
    '''database types'''
    mssqlserver = 1
    mssqlserver2000 = 2
    mssqlserver2005 = 3
    mssqlserver2008 = 4
    mssqlserver2012 = 5

class Consumer(Enum):
    '''consumers'''
    SQLAlchemy = 1
    sqlacodegen = 2

class createdb(object):
    '''(sqlalchemy connection)->void
    create the image db
    '''
    db = None

    pass

#TODO Expand supported connection types in get_connection_string

class connection_string(object):
    def __init__(self, server='', dbname='', user='', pw='', fileptr=''):
        self.server = server
        self.dbname = dbname
        self.user = user
        self.pw = pw
        self.fileptr = fileptr

    def _get_mssql_prefix(db_type=MSSQLODBCDriver.mssqlserver2012):
        if db_type == MSSQLODBCDriver.mssqlserver2005:
            return 'SQL Server Native Client'
        elif db_type == MSSQLODBCDriver.mssqlserver2008:
            return 'SQL Server Native Client 10.0'
        elif db_type == MSSQLODBCDriver.mssqlserver2012:
            return 'SQL Server Native Client 11.0'
        else:
            return 'SQL Server'

    def mssql_connection_string(self, driver=MSSQLODBCDriver.mssqlserver2012):
        '''connection_string getter for create_engine'''
        drv = quote_plus(connection_string._get_mssql_prefix(driver))
        cnstr = '%s:%s@%s/%s?driver=%s' % (self.user, self.pw, self.server, self.dbname, drv)
        cnstr = 'mssql+pyodbc://' + cnstr
        return cnstr

    def sqlite_connection_string(self, filename=''):
        '''(str)->str
        Connection strin getter for create_engine
        1) If file name is provided it uses that
        2) otherwise it uses self.fileptr
        3) if both our empty it returns an in memory connection
        returns the correctly formatted sqlite connection
        string for sqlalchemy to open its connection
        '''
        if filename == '' and self.fileptr == '' :
            s = 'sqlite://'
        elif filename == '':
            s = os.path.normpath(self.fileptr)
            s = os.path.abspath(s)
        else:
            s = os.path.normpath(filename)
            s = os.path.abspath(s)
        return 'sqlite:///%s' % s

def create_engine_mssql(cnstr, echo=True, poolclass=pool.NullPool):
    '''(str, str, str, str)->void
    opens an SQL Server engine with cnstr
    cnstr can be got by using get_connection_string()
    '''
    global ENGINE
    ENGINE = create_engine(cnstr, echo=echo, poolclass=poolclass)



def close():
    with fuckit:
        ENGINE.dispose()



def main():
    '''
    '''
    cn = connection_string('toshiba', 'imagedb', 'sa', 'GGM290471')
    s = cn.mssql_connection_string(MSSQLODBCDriver.mssqlserver2012)
    pass

#This only executes if this script was the entry point
if __name__ == '__main__':
    main()