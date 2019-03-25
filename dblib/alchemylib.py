# pylint: disable=global-statement,no-name-in-module

'''helper function for database connections
including sqlalchemy
'''
import os as _os

import sqlalchemy.pool as _pool
from sqlalchemy import create_engine as _create_engine

from funclib.baselib import isPython2 as _isPython2
from funclib.baselib import dic_merge_two
#from funclib.baselib import isPython3 as _isPython3
from enum import Enum as _Enum


if _isPython2():
    from urllib import quote_plus
else:
    from urllib.parse import quote_plus

ENGINE = None

# TODO Expand supported connection types - enumeration


class DBType(_Enum):
    '''database types'''
    mssql = 1


class MSSQLODBCDriver(_Enum):
    '''database types'''
    mssqlserver = 1
    mssqlserver2000 = 2
    mssqlserver2005 = 3
    mssqlserver2008 = 4
    mssqlserver2012 = 5


class Consumer(_Enum):
    '''consumers'''
    SQLAlchemy = 1
    sqlacodegen = 2


# TODO Expand supported connection types in get_connection_string
class ConnectionString(object):
    '''generate connection strings for different databases'''

    def __init__(self, server='', dbname='', user='', pw='', fileptr=''):
        self.server = server
        self.dbname = dbname
        self.user = user
        self.password = pw
        self.fileptr = fileptr

    @staticmethod
    def _get_mssql_prefix(db_type=MSSQLODBCDriver.mssqlserver2012):
        if db_type == MSSQLODBCDriver.mssqlserver2005:
            return 'SQL Server Native Client'
        elif db_type == MSSQLODBCDriver.mssqlserver2008:
            return 'SQL Server Native Client 10.0'
        elif db_type == MSSQLODBCDriver.mssqlserver2012:
            return 'SQL Server Native Client 11.0'

        return 'SQL Server'

    def mssql_connection_string(self, driver=MSSQLODBCDriver.mssqlserver2012):
        '''connection_string getter for _create_engine'''
        drv = quote_plus(ConnectionString._get_mssql_prefix(driver))
        cnstr = '%s:%s@%s/%s?driver=%s' % (self.user,
                                           self.password,
                                           self.server,
                                           self.dbname,
                                           drv)
        cnstr = 'mssql+pyodbc://' + cnstr
        return cnstr

    def sqlite_connection_string(self, filename=''):
        '''(str)->str
        Connection string getter for _create_engine
        1) If file name is provided it uses that
        2) otherwise it uses self.fileptr
        3) if both are empty it returns an in memory connection
        returns the correctly formatted sqlite connection
        string for sqlalchemy to open its connection
        '''
        if filename == '' and self.fileptr == '':
            s = 'sqlite://'
        elif filename == '':
            s = _os.path.normpath(self.fileptr)
            s = _os.path.abspath(s)
        else:
            s = _os.path.normpath(filename)
            s = _os.path.abspath(s)
        return 'sqlite:///%s' % s


class MsSQLs(object):
    '''generic sql functions'''

    def __init__(self):
        pass

    # TODO test
    @staticmethod
    def exists_by_key(tablename, key_col, v):
        '''(str,str,the keyvalue)->bool
        return bool indicating if  id exists in table
        '''
        sql = "if exists(SELECT 1 as one FROM " + tablename + " WHERE " + \
            key_col + "='" + str(v) + \
            "') " "SELECT 1 as res else SELECT 0 as res"
        rows = ENGINE.execute(sql)
        for row in rows:
            return bool(row['res'])

    # TODO Test
    @staticmethod
    def exists_by_compositekey(table, dic):
        '''(str, dic)->bool
        Return true or false if a record exists in table based on multiple values
        so dic would be for e.g.
        foreignkey1.id=1, foreignkey2.id=3, id=5
        '''
        sql = []

        where = ["%s='%s' AND " % (j, k) for j, k in dic.items()]
        where[-1] = where[-1].replace('AND', '')

        sql.append('if exists(SELECT 1 as one FROM ' + table + ' ')
        sql.append(''.join(where))
        sql.append(') then ')
        sql.append('select 1 as one else select 0 as one')
        query = "".join(sql)
        rows = ENGINE.execute(query)
        for row in rows:
            return bool(row['one'])

    # TODO recode for SQL/SQLAlch
    @staticmethod
    def sql_upsert(table, keylist, **kwargs):
        '''(str, dict, **kwargs)->void
        keylist is dictionary of key fields and their values used
        to build the where.
        Pass the rest of the values in kwargs
        '''
        allargs = dic_merge_two(keylist, kwargs)
        sql_insert = []
        sql_update = []

        if MsSQLs.exists_by_compositekey(table, keylist):
            where = [" %s='%s' " % (j, k) for j, k in keylist.items()]

            update = ["%s='%s'" % (j, k) for j, k in allargs.items()]

            sql_update.append("UPDATE %s SET " % (table))
            sql_update.append(", ".join(update))
            sql_update.append(" WHERE %s" % (" AND ".join(where)))
            return "".join(sql_update)

        keys = ["%s" % k for k in allargs]
        values = ["'%s'" % v for v in allargs.values()]
        sql_insert = list()
        sql_insert.append("INSERT INTO %s (" % table)
        sql_insert.append(", ".join(keys))
        sql_insert.append(") VALUES (")
        sql_insert.append(", ".join(values))
        sql_insert.append(");")
        return "".join(sql_insert)


def create_engine_mssql(cnstr, echo=False, poolclass=_pool.NullPool):
    '''(str, str, str, str)->void
    opens an SQL Server engine with cnstr
    cnstr can be got by using the ConnectionString class
    '''
    global ENGINE
    ENGINE = _create_engine(cnstr, echo=echo, poolclass=poolclass)


def close():
    '''close up db stuff'''
    try:
        ENGINE.dispose()
    except Exception as _:
        pass


def main():
    '''entry for test code'''
    cnn = ConnectionString('toshiba', 'imagedb', 'sa', 'GGM290471')
    _ = cnn.mssql_connection_string(MSSQLODBCDriver.mssqlserver2012)


# This only executes if this script was the entry point
if __name__ == '__main__':
    main()
