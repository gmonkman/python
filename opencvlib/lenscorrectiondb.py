# pylint: disable=C0302, line-too-long, too-few-public-methods, too-many-branches, too-many-statements, unused-import, no-member, ungrouped-imports, too-many-arguments, wrong-import-order, relative-import, too-many-instance-attributes, too-many-locals, unused-variable, not-context-manager
'''deals with database operations related to lenscorrecton.py'''

#region imports
import sqlite3
import fuckit
import cPickle

import funclib.baselib as baselib
#endregion


class DB(object):
    '''everything to do with the db
    '''
    cConn = sqlite3.connect(':memory:') #set in memory, simply so intellisense works
    cConn.row_factory = sqlite3.Row
    assert isinstance(cConn, sqlite3.Connection)

    def __init__(self, cnstr):
        '''(cnstr)
        open the connection using cnstr
        '''
        DB.open(cnstr)

    def __del__(self):
        with fuckit:
            DB.close()

    @staticmethod
    def open(cnstr):
        '''str->void
        file path location of the db
        '''
        DB.cConn = sqlite3.connect(cnstr)
        DB.cConn.row_factory = sqlite3.Row

    @staticmethod
    def close(commit=False):
        '''close the engine'''
        with fuckit:
            if commit:
                DB.cConn.commit()
            else:
                DB.cConn.rollback()
            DB.cConn.close()

    @staticmethod
    def commit():
        '''try a commit'''
        with fuckit:
            DB.cConn.commit()

    def rollback():
        '''try a rollback'''
        with fuckit:
            DB.cConn.rollback()

    #region exists stuff
    @staticmethod
    def exists_by_primarykey(table, keyid):
        '''(str,id)->bool
        return bool indicating if  id exists in table
        '''
        cur = DB.cConn.cursor()
        sql = 'SELECT EXISTS(SELECT 1 as one FROM ' + table + ' WHERE ' + table + 'id="' + str(keyid) + '" LIMIT 1) as res;'
        cur.execute(sql)
        row = cur.fetchall()
        for res in row:
            return bool(row['res'])

    @staticmethod
    def exists_by_compositekey(table, dic):
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
        cur = DB.cConn.cursor()
        cur.execute(query)
        row = cur.fetchall()
        return bool(row[0][0])
    #endregion

    #region correction.db specific
    @staticmethod
    def crud_camera_upsert(camera_model):
        '''(str)-> int
        add a camera
        '''
        keys = {'camera_model':camera_model}
        sql = DB._sql_upsert('camera_model', keys)
        DB.executeSQL(sql)
        return DB._get_last_id('camera_model')

    @staticmethod
    def crud_calibration_upsert(camera_modelid, width, height, camera_matrix, dcoef, rms, rvect, tvect):
        '''update/insert calibration record'''
        assert isinstance(camera_modelid, int)
        keys = {'camera_modelid':camera_modelid, 'width':width, 'height':height}
        sql = DB._sql_upsert('calibration', keys, width=width, height=height, rms=rms)
        DB.executeSQL(sql)
        calibrationid = DB._get_last_id('calibration')
        DB._blobs(calibrationid, camera_matrix, dcoef, rvect, tvect)

    @staticmethod
    def crud_calibration_delete_by_composite(camera_modelid, height, width):
        '''delete calibration by unique key
        kargs should be:
        width: height: camera_model:
        '''
        assert isinstance(camera_modelid, int)
        cur = DB.cConn.cursor()
        sql = DB._sql_delete('calibration', camera_modelid=camera_modelid, height=height, width=width)
        DB.executeSQL(sql)

    @staticmethod
    def crud_read_calibration_blobs(camera_model, height, width):
        '''(str, int, int)-> dic
        1) Using the key for table calibrtion
        2) Returns the calibration blobs from the db as a dictionary
        3) {'cmat':cmat, 'dcoef':dcoef, 'rvect':rvect, 'tvect':tvect}
        4) Returns None if no match.
        '''
        sql = DB._sql_read('calibration', camera_model=camera_model, height=height, width=width)
        cur = DB.cConn.cursor()
        res = cur.execute(sql)
        res.fetchall()
        assert isinstance(res, sqlite3.Cursor)
        if len(res) == 0:
            return None
        else:
            for row in res:
                cmat = cPickle.loads(str(row['camera_martrix']))
                dcoef = cPickle.loads(str(row['distortion_coefficients']))
                rvect = cPickle.loads(str(row['rotational_vectors']))
                tvect = cPickle.loads(str(row['translational_vectors']))
            return {'cmat':cmat, 'dcoef':dcoef, 'rvect':rvect, 'tvect':tvect}

    @staticmethod
    def executeSQL(sql):
        '''execute sql against the db'''
        cur = DB.cConn.cursor()
        cur.execute(sql)

    @staticmethod
    def _blobs(calibrationid, camera_matrix, dcoef, rvect, tvect):
        '''add the blobs seperately, easier because we let upsert generator deal with the insert/update
        but then just pass the composite key to edit the record
        '''
        assert isinstance(calibrationid, int)
        cur = DB.cConn.cursor()
        cm_b = sqlite3.Binary(camera_matrix)
        dcoef_b = sqlite3.Binary(dcoef)
        rvect_b = sqlite3.Binary(rvect)
        tvect_b = sqlite3.Binary(tvect)
        sql = 'UPDATE calibration SET camera_matrix=?, distortion_coefficients=?, rotational_vectors=?, translational_vectors=?' \
                ' WHERE calibrationid=?'
        cur.execute(sql, (cm_b, dcoef_b, rvect_b, tvect_b, calibrationid))
    #endregion


    #private helpers
    @staticmethod
    def _get_last_id(table_name):
        '''str->int
        1) Returns last added id in table table_name
        2) Returns None if no id
        '''
        sql = 'select seq from sqlite_sequence where name="%s"' % table_name
        cur = DB.cConn.cursor()
        cur.execute(sql)
        row = cur.fetchall()
        if len(row)==0:
            return None
        else:
            for results in row:
                return results['seq']


    def _sql_read(table, **kwargs):
        ''' Generates SQL for a SELECT statement matching the kwargs passed. '''
        sql = list()
        sql.append("SELECT * FROM %s " % table)
        if kwargs:
            sql.append("WHERE " + " AND ".join("%s = '%s'" % (k, v) for k, v in kwargs.iteritems()))
        sql.append(";")
        return "".join(sql)

    @staticmethod
    def _sql_upsert(table, keylist, **kwargs):
        '''(str, dict, **kwargs)->void
        keylist is dictionary of key fields and their values used
        to build the where.
        Pass the rest of the values in kwargs
        '''
        allargs = baselib.dic_merge_two(keylist, kwargs)
        sql_insert = []
        sql_update = []
        if DB.exists_by_compositekey(table, keylist):
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
#    db = DB()
 #   cam = db.camera_model(camera_model='NEXTBASE512G')
  #  DB.session.add(cam)
  #  DB.session.commit()
   # engine_close()


#This only executes if this script was the entry point
if __name__ == '__main__':
    main()
    #execute my code
