'''create and work with my main image db database'''
import sqlalchemy.pool as pool
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from enum import Enum

import fuckit



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
        '''connection_string getter'''
        drv = quote_plus(connection_string._get_mssql_prefix(driver))
        cnstr = '%s:%s@%s/%s?driver=%s' % (self.user, self.pw, self.server, self.dbname, drv)
        cnstr = 'mssql+pyodbc://' + cnstr
        return cnstr



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