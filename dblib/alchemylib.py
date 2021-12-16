# pylint: disable=global-statement,no-name-in-module
"""This module contains helper functions
for database connections using the
sqlalchemy engine.

Example of opening ENGINE:
>>>cnn = ConnectionString('toshiba', 'imagedb', 'sa', 'GGM290471')
>>>create_engine_mssql(cnn.mssql_connection_string(cnn.mssql_connection_string()))

Typical use would be to simply get the connection string
which is then used with SQL Alchemy and an Alchemy ORM
model generated with sqlcodegen.

For example:
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import session
import dblib.alchemylib as alc

CNSTR = alc.ConnectionString("toshiba", "imagedb", "sa", "GGM290471")
alc.create_engine_mssql(CNSTR.mssql_connection_string())
DBSESS = sessionmaker(bind=alc.ENGINE, autoflush=True, autocommit=True, expire_on_commit=True)
_SESS = _DBSESS()
assert isinstance(_SESSION, session.Session)

Example read and update with SQL Alchemy (auto commit assumed)
from model import Contact [the ORM model created with sqlcodegen]
row = _SESS.query(SampleLength).filter_by(id=999).first()
row.contact = 'Joe Blogs'
"""
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
ENGINE_SQLITE = None



class DBType(_Enum):
    """database types"""
    mssql = 1
    sqlite = 2


class MSSQLODBCDriver(_Enum):
    """database types"""
    mssqlserver = 1
    mssqlserver2000 = 2
    mssqlserver2005 = 3
    mssqlserver2008 = 4
    mssqlserver2012 = 5


class Consumer(_Enum):
    """consumers"""
    SQLAlchemy = 1
    sqlacodegen = 2


# TODO Expand supported connection types in get_connection_string
class ConnectionString:
    """generate connection strings for different databases

    Example (MSSQL Connection String):
    >>>alchemylib.ConnectionString('(local)', 'mydb', 'sa', 'password', use_integrated=True).mssql_connection_string()
    """

    def __init__(self, server='', dbname='', user='', pw='', fileptr='', use_integrated=False):
        self.server = server
        self.dbname = dbname
        self.user = user
        self.password = pw
        self.fileptr = fileptr
        self.use_integrated = use_integrated

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
        """connection_string getter for _create_engine"""
        drv = quote_plus(ConnectionString._get_mssql_prefix(driver))
        if self.use_integrated:
            #https://github.com/zzzeek/sqlalchemy/blob/master/lib/sqlalchemy/dialects/mssql/pyodbc.py
            cnstr = '%s:%s@%s/%s?driver=%s' % ('', '', self.server,
                                               self.dbname,
                                               drv)
        else:
            cnstr = '%s:%s@%s/%s?driver=%s' % (self.user,
                                               self.password,
                                               self.server,
                                               self.dbname,
                                               drv)
        cnstr = 'mssql+pyodbc://' + cnstr
        return cnstr

    def sqlite_connection_string(self, filename=''):
        """(str)->str
        Connection string getter for _create_engine
        1) If file name is provided it uses that
        2) otherwise it uses self.fileptr
        3) if both are empty it returns an in memory connection
        returns the correctly formatted sqlite connection
        string for sqlalchemy to open its connection
        """
        if filename == '' and self.fileptr == '':
            s = 'sqlite://'
        elif filename == '':
            s = _os.path.normpath(self.fileptr)
            s = _os.path.abspath(s)
        else:
            s = _os.path.normpath(filename)
            s = _os.path.abspath(s)
        return 'sqlite:///%s' % s


class MsSQLs:
    """generic sql functions"""

    def __init__(self):
        pass

    # TODO test
    @staticmethod
    def exists_by_key(tablename, key_col, v):
        """(str,str,the keyvalue)->bool
        return bool indicating if  id exists in table
        """
        sql = "if exists(SELECT 1 as one FROM " + tablename + " WHERE " + \
            key_col + "='" + str(v) + \
            "') " "SELECT 1 as res else SELECT 0 as res"
        rows = ENGINE.execute(sql)
        for row in rows:
            return bool(row['res'])

    # TODO Test
    @staticmethod
    def exists_by_compositekey(table, dic):
        """(str, dic)->bool
        Return true or false if a record exists in table based on multiple values
        so dic would be for e.g.
        foreignkey1.id=1, foreignkey2.id=3, id=5
        """
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
        """(str, dict, **kwargs)->void
        keylist is dictionary of key fields and their values used
        to build the where.
        Pass the rest of the values in kwargs
        """
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
    """(str, str, str, str)->void
    opens an SQL Server engine with cnstr
    cnstr can be got by using the ConnectionString class

    Example:
    >>> cnn = ConnectionString('toshiba', 'imagedb', 'sa', 'GGM290471')
    >>> create_engine_mssql(cnn.mssql_connection_string(cnn.mssql_connection_string()))
    """
    global ENGINE
    ENGINE = _create_engine(cnstr, echo=echo, poolclass=poolclass)


def create_engine_sqlite(cnstr, echo=False, poolclass=_pool.NullPool):
    """create sqlite engine with cnstr"""
    global ENGINE_SQLITE
    ENGINE_SQLITE

def close():
    """close up db stuff"""
    try:
        ENGINE.dispose()
    except Exception as _:
        pass


def main():
    """entry for test code"""
    cnn = ConnectionString('toshiba', 'imagedb', 'sa', 'GGM290471')
    create_engine_mssql(cnn.mssql_connection_string(cnn.mssql_connection_string()))
    #set cnn to an sql server connection string
    #and pass to create_engine_mssql to instantiate alchemylib.ENGINE



# This only executes if this script was the entry point
if __name__ == '__main__':
    main()
