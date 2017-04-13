# pylint: disable=C0302, line-too-long, too-few-public-methods,
# too-many-branches, too-many-statements, no-member, ungrouped-imports,
# too-many-arguments, wrong-import-order, relative-import,
# too-many-instance-attributes, too-many-locals, unused-variable,
# not-context-manager
'''SQLAlchemy *independent* sqllite CRUD functions'''
import os

import sqlite3
import fuckit
import pickle


import funclib.baselib as baselib

# endregion


class Conn(object):
    '''connection to database. Loaded into the self.conn
    initiate with the with statement.
    A path can be passed in and it will call sqlite_connection_string
    to correctly format the connection string.

    Pass the cnstr in when the class is initialised or call open
    '''

    def __init__(self, cnstr=':memory:', force_absolute_path=True):
        self.cnstr = self._make_abs_path(
            cnstr) if force_absolute_path else cnstr
        self.conn = None
        # no need to open connection in init - __enter__ will do that.

    def __enter__(self):
        self.conn = sqlite3.connect(self.cnstr)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def open(self, cnstr, force_absolute_path=True):
        '''str->void
        file path location of the db
        open a connection, closing existing one
        '''
        self.cnstr = self._make_abs_path(
            cnstr) if force_absolute_path else cnstr
        self.close()
        self.conn = sqlite3.connect(self.cnstr)
        self.conn.row_factory = sqlite3.Row

    def close(self, commit=False):
        '''close the db'''
        with fuckit:
            if commit:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()

    def commit(self):
        '''commit'''
        self.conn.commit()

    @staticmethod
    def _make_abs_path(fileptr):
        '''(str)->str
        Creates absolute paths to sqlite db file for consumption by the sqlite3 library.e
        '''
        if fileptr != ':memory:':
            s = os.path.normpath(fileptr)
            s = os.path.abspath(s)
        else:
            s = ':memory:'
        return s


class CRUD(object):
    '''everything to do with the db
    '''

    def __init__(self, dbconn):
        '''(sqlite3.conection)
        pass in an open dbconn
        '''
        self.conn = dbconn
        assert isinstance(self.conn, sqlite3.Connection)

    # region exists stuff
    def exists_by_primarykey(self, table, keyid):
        '''(str,id)->bool
        return bool indicating if  id exists in table
        '''
        cur = self.conn.cursor()
        sql = 'SELECT EXISTS(SELECT 1 as one FROM ' + table + ' WHERE ' + \
            table + 'id="' + str(keyid) + '" LIMIT 1) as res;'
        cur.execute(sql)
        row = cur.fetchall()
        for res in row:
            return bool(row['res'])

    def exists_by_compositekey(self, table, dic):
        '''(str, dic)->bool
        Return true or false if a record exists in table based on multiple values
        so dic would be for e.g.
        foreignkey1.id=1, foreignkey2.id=3, id=5
        '''
        sql = []
        where = ["%s='%s' AND " % (j, k) for j, k in dic.iteritems()]
        where[-1] = where[-1].replace('AND', '')
        sql.append('select  exists(select 1 from %s where ' % (table))
        sql.append("".join(where))
        sql.append('LIMIT 1);')
        query = "".join(sql)
        cur = self.conn.cursor()
        cur.execute(query)
        row = cur.fetchall()
        return bool(row[0][0])
    # endregion

    @staticmethod
    def get_blob(row, colname):
        '''(sqlite.Row, str)-> dic
        Returns unpickled object from db blob field
        which was pickled then stored
        '''
        assert isinstance(row, sqlite3.Row)
        return pickle.loads(str(colname))

    def execute_sql(self, sql):
        '''execute sql against the db'''
        cur = self.conn.cursor()
        cur.execute(sql)

    def get_last_id(self, table_name):
        '''str->int
        1) Returns last added id in table table_name
        2) Returns None if no id
        '''
        sql = 'select seq from sqlite_sequence where name="%s"' % table_name
        cur = self.conn.cursor()
        cur.execute(sql)
        row = cur.fetchall()
        return CRUD._read_col(row, 'seq')

    @staticmethod
    def _read_col(cur, colname):
        '''cursor, str->basetype
        reads a cursor row column value
        returns None if there is no row
        First row only
        '''
        if len(cur) == 0:
            return None
        else:
            for results in cur:
                return results[colname]

    def lookup(self, table_name, col_to_search, col_with_value_we_want, value):
        '''(str, str, str, basetype)->basetype
        1) Returns lookup value, typically based on a primary key value
        2) Returns None if no matches found
        '''
        sql = 'SELECT %s FROM %s WHERE %s="%s" LIMIT 1;' % \
            (col_with_value_we_want, table_name, col_to_search, value)
        cur = self.conn.cursor()
        cur.execute(sql)
        row = cur.fetchall()
        return self._read_col(row, col_with_value_we_want)

    @staticmethod
    def sql_read(table, **kwargs):
        ''' Generates SQL for a SELECT statement matching the kwargs passed. '''
        sql = list()
        sql.append("SELECT * FROM %s " % table)
        if kwargs:
            sql.append("WHERE " + " AND ".join("%s = '%s'" % (k, v)
                                               for k, v in kwargs.iteritems()))
        sql.append(";")
        return "".join(sql)

    def sql_upsert(self, table, keylist, **kwargs):
        '''(str, dict, **kwargs)->void
        keylist is dictionary of key fields and their values used
        to build the where.
        Pass the rest of the values in kwargs
        '''
        allargs = baselib.dic_merge_two(keylist, kwargs)
        sql_insert = []
        sql_update = []
        if self.exists_by_compositekey(table, keylist):
            where = [" %s='%s' " % (j, k) for j, k in keylist.iteritems()]

            update = ["%s='%s'" % (j, k) for j, k in allargs.iteritems()]

            sql_update.append("UPDATE %s SET " % (table))
            sql_update.append(", ".join(update))
            sql_update.append(" WHERE %s" % (" AND ".join(where)))
            return "".join(sql_update)
        else:
            keys = ["%s" % k for k in allargs]
            values = ["'%s'" % v for v in allargs.values()]
            sql_insert = list()
            sql_insert.append("INSERT INTO %s (" % table)
            sql_insert.append(", ".join(keys))
            sql_insert.append(") VALUES (")
            sql_insert.append(", ".join(values))
            sql_insert.append(");")
            return "".join(sql_insert)

    @staticmethod
    def sql_delete(table, **kwargs):
        ''' deletes rows from table where **kwargs match '''
        sql = list()
        sql.append("DELETE FROM %s " % table)
        sql.append("WHERE " + " AND ".join("%s = '%s'" % (k, v)
                                           for k, v in kwargs.iteritems()))
        sql.append(";")
        return "".join(sql)


def main():
    '''run when executed directly'''
    pass


# This only executes if this script was the entry point
if __name__ == '__main__':
    main()
    # execute my code
