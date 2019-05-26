# pylint: disable=C0302
'''Connection handling and some basic CRUD.
CRUD is awaiting adaption of the SQLLite code which
is commented out. - Needs more testing and work
'''
import datetime as _datetime
import pymssql
import funclib.baselib as _baselib
import funclib.stringslib as _stringslib


class Conn():
    '''Connection to an SQL Server database.

    Args:
    dbname:database name
    server:server name, ip etc
    security: integrated for NT security, or any other string for SQL Server security
    user,pw: Authentication of NOT using NT (integrated) security

    Example:
    with mssql.Conn('mydb') as conn:
        sql = "DELETE FROM test"
        with conn.cursor() as cur:
            cur.execute(sql)
    '''

    def __init__(self, dbname, server='(local)', port=1433, security='integrated', user='', pw='', autocommit=True):
        self.conn = None
        self.dbname = dbname
        self.server = server
        self.port = port
        self.security = security
        self.user = user
        self.pw = pw
        self.autocommit = autocommit
        self._connect()
        # no need to open connection in init - __enter__ will do that.


    def __enter__(self):
        return self._connect()


    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()


    def open(self, dbname, server='(local)', port=1433, security='integrated', user='', pw='', autocommit=True):
        '''str->void
        file path location of the db
        open a connection, closing existing one
        '''
        self.conn = None
        self.dbname = dbname
        self.server = server
        self.port = port
        self.security = security
        self.user = user
        self.pw = pw
        self.autocommit = autocommit
        try:
            self.close()
        except Exception as _:
            pass
        self._connect()


    def close(self, commit=False):
        '''close the db'''
        try:
            if commit:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()
        except Exception as _:
            pass


    def commit(self):
        '''commit'''
        self.conn.commit()


    def _connect(self):
        if not self.conn is None:
            try:
                self.conn.close()
            except:
                pass
        if self.security == 'integrated':
            self.conn = pymssql.connect(server=self.server, port=self.port, database=self.dbname, autocommit=self.autocommit)
        else:
            self.conn = pymssql.connect(server=self.server, user=self.user, password=self.pw, port=self.port, database=self.dbname, autocommit=self.autocommit)
        return self.conn


    def execute(self, sql, commit=True):
        '''(str, bool) ->
        Executes a T-SQL statement against
        the current connection

        sql:
            the SQL
        commit:
            commits changes, by default autocommit is set for
            the connection

        Note, using the with statement for this object
        returns a pymssql connection instance and so
        this execute cannot be executed.
        '''
        with self.conn.cursor() as cur:
            cur.execute(sql)
        if commit:
            self.commit()




class CRUD(object):
    '''everything to do with the db
    Not implemented yet.
    See https://pymysql.readthedocs.io/en/latest/user/examples.html for
    examples of cursor use.
    '''

    def __init__(self, dbconn):
        '''(sqlite3.conection)
        pass in an open dbconn
        '''
        self.conn = dbconn
        assert isinstance(self.conn, pymssql.Connection)

    # region exists stuff
    def exists_by_primarykey(self, table, keyid):
        '''(str,id)->bool
        return bool indicating if id exists in table.
        i.e. relies on there being an id column as the primary key
        '''
        cur = self.conn.cursor()
        sql = 'SELECT EXISTS(SELECT 1 as one FROM ' + table + ' WHERE ' + \
            table + 'id="' + str(keyid) + '" LIMIT 1) as res;'
        cur.execute(sql)
        row = cur.fetchall()
        for _ in row:
            return bool(row['res'])


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
        '''
        sql = []
        where = ["%s='%s' AND " % (j, k) for j, k in dic.items()]
        where[-1] = where[-1].replace('AND', '')
        sql.append('select top 1 exists(select 1 from %s where ' % (table))
        sql.append("".join(where))
        sql.append(');')
        query = "".join(sql)
        cur = self.conn.cursor()
        cur.execute(query)
        row = cur.fetchall()
        return str(row[0][0])


    def execute_sql(self, sql, get_cursor=False):
        '''(str, bool) -> void|cursorpymssql.cursor
        Execute sql against the db

        get_cursor: if true,return the cursor object else None
        '''
        cur = self.conn.cursor()
        cur.execute(sql)
        if get_cursor:
            return cur
        return None


    def get_last_id(self, table_name):
        #see https://dba.stackexchange.com/questions/124847/best-way-to-get-last-identity-inserted-in-a-table
        '''str->int
        1) Returns last added id in table table_name
        2) Returns None if no id
        '''
        sql = "select ident_current('%s')"
        cur = self.conn.cursor()
        cur.execute(sql)
        row = cur.fetchall()
        return CRUD._read_col(row, 'seq')



    def lookup(self, table_name, col_to_search, col_with_value_we_want, value):
        '''(str, str, str, basetype)->basetype
        1) Returns lookup value, typically based on a primary key value
        2) Returns None if no matches found
        '''
        sql = "SELECT TOP 1 %s FROM %s WHERE %s='%s';" % \
            (col_with_value_we_want, table_name, col_to_search, value)
        cur = self.conn.cursor()
        cur.execute(sql)
        row = cur.fetchall()
        return self._read_col(row, col_with_value_we_want)


    def upsert(self, table, keylist, **kwargs):
        '''str, dict, kwargs->void
        Do an upsert against the curent connection

        table: table name
        keylist: field/value pairs for the key
        kwargs: rest of the field/value pairs for the update/insert

        Example:
        Insert/Update the contact with id=1 to 'Joe Bloggs'
        >>>upsert('mytable', {'id':1}, contact='Joe Bloggs')
        >>>
        '''
        self.execute_sql(CRUD.sql_upsert(table, keylist, kwargs))


    def delete(self, table, **kwargs):
        '''str, kwargs->void

        Delete record with key from kwargs.

        table: table name
        kwargs: field/value pairs

        Example:
        >>>delete('mytable', forename='Joe', lastname='bloggs')
        >>>
        '''
        self.execute_sql(CRUD.sql_delete(table, kwargs))



    def read_rows(self, **kwargs):
        '''read multiple rows'''
        raise NotImplementedError


    def sql_upsert(self, table, keylist, **kwargs):
        '''(str, dict, **kwargs)->str
        Return an SQL string UPSERT statement.

        table: table name
        keylist: field/value pairs for the key
        kwargs: rest of the field/value pairs for the update/insert

        Example (Key id=1 does not exist):
        >>>sql_upsert('mytable', {'id':1}, contact='Joe Bloggs')
        INSERT INTO mytable (id, contact) values (1, 'Joe Bloggs')
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



#CLASS STATICS
    @staticmethod
    def _get_blob(row, colname):
        '''(sqlite.Row, str)-> dic
        Returns unpickled object from db blob field
        which was pickled then stored
        '''
        #assert isinstance(row, sqlite3.Row)
        #return pickle.loads(str(colname))
        raise NotImplementedError


    @staticmethod
    def _read_col(cur, colname):
        '''pymmsql.cursor, str->basetype
        reads a cursor row column value
        returns None if there is no row
        First row only
        '''
        if not cur: return None

        for results in cur:
            if isinstance(results, tuple):
                return results[0]
            return results[colname]


    @staticmethod
    def _sql_read(table, **kwargs):
        '''(str, kwargs) -> str
        Generates the SQL for a SELECT statement matching the kwargs passed.

        table: table name
        kwargs:column/value pairs

        Example:
        >>>sql_read('mytable', id=1, contact='Joe Bloggs')
        SELECT * FROM mytable WHERE id='1' and contact='Joe Bloggs'
        '''
        sql = list()
        sql.append("SELECT * FROM %s " % table)
        if kwargs:
            sql.append("WHERE " + " AND ".join("%s = '%s'" % (k, v)
                                               for k, v in kwargs.items()))
        sql.append(";")
        return "".join(sql)



    @staticmethod
    def sql_delete(table, **kwargs):
        '''(kwargs)->str
        SQL for delete by kwargs.
        kwargs: field/value pair

        Example:
        >>>sql_delete('mytable', id=1)
        DELETE FROM mytable WHERE id=1
        '''
        sql = list()
        sql.append("DELETE FROM %s " % table)
        sql.append("WHERE " + " AND ".join("%s = '%s'" % (k, v)
                                           for k, v in kwargs.items()))
        sql.append(";")
        return "".join(sql)


def getNow():
    '''Get sql friendly current datetime
    '''
    return _datetime.datetime.strftime(_datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')


def get_as_list(table, col, dbname, server='(local)', quote=True, to_lower=False, clean=False):
    '''(str, str, Class:Conn, str, bool, bool) -> list

    Convert an sql table col to a list.

    quote: quote the data, use for string data
    to_lower: convert to lower case
    clean:clean the strings, e.g. remove single quotes

    example:
    >>>mssql.get_as_list('species_alias', 'species_aliasid', 'mmo', to_lower=True)
    ['trout','bass']
    '''
    if quote:
        sql = "" \
        "SELECT top 1 " \
	    "'[' + RIGHT(NameValues, len(NameValues) - 1) + ']' as csv" \
        " FROM (" \
	    " SELECT (" \
						    "SELECT " \
							    "',\"' + CAST([" + col + "] AS nvarchar(max)) + '\"'" \
						    "FROM" \
							    "[" + table + "]" \
						    " FOR XML PATH ('')" \
						    " )" \
						    " as NameValues" \
	    " FROM " \
		    " [" + table + "] as Results ) as a"
    else:
        sql = "" \
        "SELECT top 1  " \
	    "'[' + RIGHT(NameValues, len(NameValues) - 1) + ']' as csv " \
        " FROM (" \
	    " SELECT (" \
						    " SELECT " \
							    "',' + CAST([" + col + "] AS nvarchar(max)) " \
						    " FROM " \
							    "[" + table + "]" \
						    " FOR XML PATH ('')" \
						    " )" \
						    " as NameValues" \
	    " FROM " \
		    " [" + table + "] as Results ) as a"


    with Conn(dbname, server) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            row = cur.fetchall()
            s = CRUD._read_col(row, 'csv')
    l = _baselib.list_from_str(s)
    if to_lower:
        l = [s.lower() for s in l]
    if clean:
        l = [_stringslib.filter_alphanumeric1(s, strict=True, remove_single_quote=True, remove_double_quote=True) for s in l]
    return l



