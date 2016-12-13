# pylint: disable=C0302, line-too-long, too-few-public-methods, too-many-branches, too-many-statements, no-member, ungrouped-imports, too-many-arguments, wrong-import-order, relative-import, too-many-instance-attributes, too-many-locals, unused-variable, not-context-manager
'''deals with database operations related to lenscorrecton.py'''

#region imports
import sqlite3
import fuckit
import pickle

import funclib.baselib as baselib
#endregion

class Conn(object):
    '''connection to database'''
    def __init__(self, cnstr=':memory:'):
        self.cnstr = cnstr
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.cnstr)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def open(self, cnstr):
        '''str->void
        file path location of the db
        open a connection, closing existing one
        '''
        self.close()
        self.conn = sqlite3.connect(cnstr)
        self._conn.row_factory = sqlite3.Row

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
        self._conn.commit()


class CalibrationCRUD(object):
    '''everything to do with the db
    '''
    def __init__(self, dbconn):
        '''(cnstr)
        pass in an open dbconn
        '''
        self.conn = dbconn
        assert isinstance(self.conn, sqlite3.Connection)

    #region exists stuff
    def exists_by_primarykey(self, table, keyid):
        '''(str,id)->bool
        return bool indicating if  id exists in table
        '''
        cur = self.conn.cursor()
        sql = 'SELECT EXISTS(SELECT 1 as one FROM ' + table + ' WHERE ' + table + 'id="' + str(keyid) + '" LIMIT 1) as res;'
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
    #endregion

    #region correction.db specific
    def crud_camera_upsert(self, camera_model):
        '''(str)-> int
        add a camera
        '''
        keys = {'camera_model':camera_model}
        sql = self._sql_upsert('camera_model', keys)
        self.executeSQL(sql)
        return self._get_last_id('camera_model')

    def crud_calibration_upsert(self, camera_modelid, width, height, camera_matrix, dcoef, rms, rvect, tvect):
        '''update/insert calibration record'''
        assert isinstance(camera_modelid, int)
        keys = {'camera_modelid':camera_modelid, 'width':width, 'height':height}
        sql = self._sql_upsert('calibration', keys, width=width, height=height, rms=rms)
        self.executeSQL(sql)
        calibrationid = self._get_last_id('calibration')
        self._blobs(calibrationid, camera_matrix, dcoef, rvect, tvect)

    def crud_calibration_delete_by_composite(self, camera_modelid, height, width):
        '''delete calibration by unique key
        kargs should be:
        width: height: camera_model:
        '''
        assert isinstance(camera_modelid, int)
        cur = self.conn.cursor()
        sql = CalibrationCRUD._sql_delete('calibration', camera_modelid=camera_modelid, height=height, width=width)
        self.executeSQL(sql)

    def crud_read_calibration_blobs(self, camera_model, height, width):
        '''(str, int, int)-> dic
        1) Using the key for table calibrtion
        2) Returns the calibration blobs from the db as a dictionary
        3) {'cmat':cmat, 'dcoef':dcoef, 'rvect':rvect, 'tvect':tvect}
        4) Returns None if no match.
        '''
        cameramodelid = self._lookup('camera_model', 'camera_model', 'camera_modelid', camera_model)
        if cameramodelid is None:
            raise ValueError('cameramodelid could not be read for %s' % camera_model)

        sql = CalibrationCRUD._sql_read('calibration', camera_modelid=cameramodelid, height=height, width=width)
        cur = self.conn.cursor()
        res = cur.execute(sql)
        assert isinstance(res, sqlite3.Cursor)
        for row in res:
            if len(row) == 0:
                return None
            else:
                cmat = pickle.loads(str(row['camera_matrix']))
                dcoef = pickle.loads(str(row['distortion_coefficients']))
                rvect = pickle.loads(str(row['rotational_vectors']))
                tvect = pickle.loads(str(row['translational_vectors']))
                return {'cmat':cmat, 'dcoef':dcoef, 'rvect':rvect, 'tvect':tvect}

    def executeSQL(self, sql):
        '''execute sql against the db'''
        cur = self.conn.cursor()
        cur.execute(sql)

    def _blobs(self, calibrationid, camera_matrix, dcoef, rvect, tvect):
        '''add the blobs seperately, easier because we let upsert generator deal with the insert/update
        but then just pass the composite key to edit the record
        '''
        assert isinstance(calibrationid, int)
        cur = self.conn.cursor()
        cm_b = sqlite3.Binary(camera_matrix)
        dcoef_b = sqlite3.Binary(dcoef)
        rvect_b = sqlite3.Binary(rvect)
        tvect_b = sqlite3.Binary(tvect)
        sql = 'UPDATE calibration SET camera_matrix=?, distortion_coefficients=?, rotational_vectors=?, translational_vectors=?' \
                ' WHERE calibrationid=?'
        cur.execute(sql, (cm_b, dcoef_b, rvect_b, tvect_b, calibrationid))

    def blobs_get_nearest_aspect_match(self, camera_model, height, width):
        '''(str, int, int)->dict
        Returns the calibration matrices for the nearest matching
         aspect for which we have correction matrices
        {'cmat':cmat, 'dcoef':dcoef, 'rvect':rvect, 'tvect':tvect, 'matched_resolution_w_by_h':(w,h), 'new_aspect':w/h)}
        '''

        aspect = width / float(height)
        sql = 'SELECT calibration.height, calibration.width, calibration.camera_matrix, calibration.distortion_coefficients,' \
            ' calibration.rotational_vectors, calibration.translational_vectors, width/cast(height as float) as aspect' \
            ' FROM calibration' \
            ' INNER JOIN camera_model ON calibration.camera_modelid=camera_model.camera_modelid' \
            ' WHERE camera_model.camera_model=?' \
            ' ORDER BY ABS(? - (width/cast(height as float))) LIMIT 1'
        cur = self.conn.cursor()
        res = cur.execute(sql, [camera_model, aspect])
        assert isinstance(res, sqlite3.Cursor)
        for row in res:
            if len(row) == 0:
                return None
            else:
                cmat = pickle.loads(str(row['camera_matrix']))
                dcoef = pickle.loads(str(row['distortion_coefficients']))
                rvect = pickle.loads(str(row['rotational_vectors']))
                tvect = pickle.loads(str(row['translational_vectors']))
                w = row['width']; h = row['height']; aspect = w/float(h)
                return {'cmat':cmat, 'dcoef':dcoef, 'rvect':rvect, 'tvect':tvect, 'matched_resolution_w_by_h':(w, h), 'new_aspect':aspect}
    #endregion


    #helpers
    def _get_last_id(self, table_name):
        '''str->int
        1) Returns last added id in table table_name
        2) Returns None if no id
        '''
        sql = 'select seq from sqlite_sequence where name="%s"' % table_name
        cur = self.conn.cursor()
        cur.execute(sql)
        row = cur.fetchall()
        return CalibrationCRUD._read_col(row, 'seq')

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

    def _lookup(self, table_name, col_to_search, col_with_value_we_want, value):
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
    def _sql_read(table, **kwargs):
        ''' Generates SQL for a SELECT statement matching the kwargs passed. '''
        sql = list()
        sql.append("SELECT * FROM %s " % table)
        if kwargs:
            sql.append("WHERE " + " AND ".join("%s = '%s'" % (k, v) for k, v in kwargs.iteritems()))
        sql.append(";")
        return "".join(sql)

    def _sql_upsert(self, table, keylist, **kwargs):
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
    def _sql_delete(table, **kwargs):
        ''' deletes rows from table where **kwargs match '''
        sql = list()
        sql.append("DELETE FROM %s " % table)
        sql.append("WHERE " + " AND ".join("%s = '%s'" % (k, v) for k, v in kwargs.iteritems()))
        sql.append(";")
        return "".join(sql)


def main():
    '''run when executed directly'''

    pass


#This only executes if this script was the entry point
if __name__ == '__main__':
    main()
    #execute my code
