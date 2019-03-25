# pylint: disable=C0302, line-too-long, too-few-public-methods,
# too-many-branches, too-many-statements, no-member, ungrouped-imports,
# too-many-arguments, wrong-import-order, relative-import,
# too-many-instance-attributes, too-many-locals, unused-variable,
# not-context-manager
'''SQLAlchemy *independent* sqllite CRUD functions'''
import sqlite3 as _sqlite3
import pickle as _pickle

import funclib.baselib as _baselib

# endregion


class Conn(object):
    '''connection to database'''

    def __init__(self, cnstr=':memory:'):
        self.cnstr = cnstr
        self.conn = None

    def __enter__(self):
        self.conn = _sqlite3.connect(self.cnstr)
        self.conn.row_factory = _sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def open(self, cnstr):
        '''str->void
        file path location of the db
        open a connection, closing existing one
        '''
        self.close()
        self.conn = _sqlite3.connect(cnstr)
        self.conn.row_factory = _sqlite3.Row

    def close(self, commit=False):
        '''close the db'''
        try:
            if commit:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()
        except:
            pass

    def commit(self):
        '''commit'''
        self.conn.commit()


class CRUD(object):
    '''everything to do with the db
    '''

    def __init__(self, dbconn):
        '''(sqlite3.conection)
        pass in an open dbconn
        '''
        self.conn = dbconn
        assert isinstance(self.conn, _sqlite3.Connection)


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
            return bool(res)


    def exists_by_compositekey(self, table, dic):
        '''(str, dic)->bool
        Return true or false if a record exists in table based on multiple values
        so dic would be for e.g.
        foreignkey1.id=1, foreignkey2.id=3, id=5
        '''
        sql = []
        where = ["%s='%s' AND " % (j, k) for j, k in dic.items()]
        where[-1] = where[-1].replace('AND', '')
        sql.append('select  exists(select 1 from %s where ' % (table))
        sql.append("".join(where))
        sql.append('LIMIT 1);')
        query = "".join(sql)
        cur = self.conn.cursor()
        cur.execute(query)
        row = cur.fetchall()
        return bool(row[0][0])


    def get_value(self, table, col_to_read, key_cols):
        '''(str, str, dic:str) -> str|None
        Read the value in col_to_read which matches
        the values assigned to the col-value pairs in key_cols.
        Returns None if no match

        table:
            the name of the table
        col_to_read:
            the name of the column which contains the value to return
        key_cols:
            a dictionary of key value pairs, e.g. {'id':1, 'country':'UK'}

        returns:
            The first matched value, or None

        Exmaple:
            tot = get_value('orders', 'total', {'company':'Amazon', 'region':'UK'})
        '''
        sql = []
        where = ["%s='%s' AND " % (j, k) for j, k in key_cols.items()]
        where[-1] = where[-1].replace('AND', '')
        sql.append('select %s from %s where ' % (col_to_read, table))
        sql.append("".join(where))
        sql.append('LIMIT 1;')
        query = "".join(sql)
        cur = self.conn.cursor()
        cur.execute(query)
        row = cur.fetchall()

        try:
            s = str(row[0][0])
        except Exception:
            s = None

        return s


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


    def upsert(self, table, keylist, **kwargs):
        '''(str, dict, **kwargs)->str
        Upsert a record and return the sql as well

        Generate an SQL statement to either insert or update an sql table.
        If the record exists, as determined by the keylist then an update is
        generated, otherwise an insert

        Keylist is dictionary of key fields and their values used to build the where.

        Field values are passed as kwargs.

        The upsert will considers a value string of 'CURRENT_TIMESTAMP'
        a special case, and will strip the quotes so the corresponding
        field gets set to CURRENT_TIMESTAMP. e.g. timestamp='CURRENT_TIMESTAMP'
        will be timestamp=CURRENT_TIMESTAMP in the final sql.

        table:
            Database table name
        keylist:
            Builds the where e.g. {'orderid':1, 'supplier':'Widget Company'}
        kwargs:
            Fields to insert/update

        returns:
            The insert or update SQL as a string
        '''
        allargs = _baselib.dic_merge_two(keylist, kwargs)
        sql_insert = []
        sql_update = []
        if self.exists_by_compositekey(table, keylist):
            where = [" %s='%s' " % (j, k) for j, k in keylist.items()]

            update = ["%s='%s'" % (j, k) for j, k in allargs.items()]

            sql_update.append("UPDATE %s SET " % (table))
            sql_update.append(", ".join(update))
            sql_update.append(" WHERE %s" % (" AND ".join(where)))

            ret = "".join(sql_update)
            ret = ret.replace("'CURRENT_TIMESTAMP'", "CURRENT_TIMESTAMP")
            return ret


        keys = ["%s" % k for k in allargs]
        values = ["'%s'" % v for v in allargs.values()]
        sql_insert = list()
        sql_insert.append("INSERT INTO %s (" % table)
        sql_insert.append(", ".join(keys))
        sql_insert.append(") VALUES (")
        sql_insert.append(", ".join(values))
        sql_insert.append(");")
        ret = "".join(sql_insert)
        ret = ret.replace("'CURRENT_TIMESTAMP'", "CURRENT_TIMESTAMP")
        cur = self.conn.cursor()
        cur.execute(ret)
        self.conn.commit()
        return ret



    def executeSQL(self, sql):
        '''execute sql against the db'''
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()


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








    #region Static methods and helpers
    @staticmethod
    def get_blob(row, colname):
        '''(sqlite.Row, str)-> dic
        Returns unpickled object from db blob field
        which was pickled then stored
        '''
        assert isinstance(row, _sqlite3.Row)
        return _pickle.loads(str(colname))


    @staticmethod
    def _read_col(cur, colname):
        '''cursor, str->basetype
        reads a cursor row column value
        returns None if there is no row
        First row only
        '''
        if not cur:
            return None

        for results in cur:
            return results[colname]


    @staticmethod
    def _sql_read(table, **kwargs):
        ''' Generates SQL for a SELECT statement matching the kwargs passed. '''
        sql = list()
        sql.append("SELECT * FROM %s " % table)
        if kwargs:
            sql.append("WHERE " + " AND ".join("%s = '%s'" % (k, v)
                                               for k, v in kwargs.items()))
        sql.append(";")
        return "".join(sql)


    @staticmethod
    def _sql_delete(table, **kwargs):
        '''(str, dict) -> str
        Generates a delete sql from keyword/value pairs
        where keyword is the column name and value is the value to match.

        table:
            table name
        kwargs:
            Key/value pairs, e.g. {'camera':'GoPro', 'x':1024, 'y':768}

        returns:
            The delete SQL
        '''
        sql = list()
        sql.append("DELETE FROM %s " % table)
        sql.append("WHERE " + " AND ".join("%s = '%s'" % (k, v)
                                           for k, v in kwargs.items()))
        sql.append(";")
        return "".join(sql)
    #endregion
