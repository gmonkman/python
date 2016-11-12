# pylint: disable=C0302, line-too-long, too-few-public-methods, too-many-branches, too-many-statements, unused-import, no-member, ungrouped-imports, too-many-arguments, wrong-import-order, relative-import, too-many-instance-attributes, too-many-locals, unused-variable, not-context-manager
'''deals with database operations related to lenscorrecton.py'''

#region imports
import sqlite3
import fuckit
#endregion


class DB(object):
    '''everything to do with the db
    '''
    cConn = sqlite3.connect(':memory:') #set in memory, simply so intellisense works
    assert isinstance(cConn, sqlite3.Connection)

    def __init__(self, cnstr):
        '''(cnstr)
        open the connection using cnstr
        '''
        open(cnstr)

    def __del__(self):
        with fuckit:
            close()

    @staticmethod
    def open(cnstr):
        '''str->void
        file path location of the db
        '''
        DB.cConn = sqlite3.connect(cnstr)

    @staticmethod
    def close():
        '''close the engine'''
        with fuckit:
            cConn.commit()
            DB.cConn.close()

    @staticmethod
    def exists_by_primarykey(table, id):
        '''(str,id)->bool
        return bool indicating if  id exists in table
        '''
        cur = DB.cConn.cursor()
        sql = 'SELECT EXISTS(SELECT 1 FROM ' + table + ' WHERE ' + table + 'id="' + str(id) + '" LIMIT 1);'
        cur.execute(sql)
        row = cur.fetchall()
        return bool(row[0][0])

    @staticmethod
    def crud_camera_upsert(camera_model):
        '''add a camera'''
        cur = DB.cConn.cursor()
        sql = DB._sql_upsert(camera_model, camera_model=camera_model)
        cur.execute(sql,camera_model)

    @staticmethod
    def crud_calibration_upsert(camera_model, width, height, camera_matrix, dcoef, rms, rvect, tvect):
        '''update/insert calibration record'''
        sql = _sql_upsert(calibration, camera_model=camera_model, width=width, height=height, camera_matrix=camera_matrix, dcoef=dcoef, rms=rms, rvect=rvect, tvect=tvect)
        cur = DB.cConn.cursor()
        cur.execute(sql)
        DB._blobs(camera_model, width, height, camera_matrix, dcoef, rvect, tvect)

    def _blobs(camera_model, width, height, camera_matrix, dcoef, rvect, tvect):
        '''add the blobs seperately, easier because we let upsert generator deal with the insert/update
        but then just pass the composite key to edit the record
        '''
        cur = DB.cConn.cursor()
        cm_b = sqlite3.Binary(camera_matrix)
        dcoef_b = sqlite3.Binary()
        rvect_b = sqlite3.Binary(rvect)
        tvect_b = sqlite3.Binary(tvect)
        sql = 'UPDATE calibration SET camera_matrix=?, distortion_coefficients=?, rotational_vectors=?, translational_vectors=?' \
                ' WHERE camera_model=? and width=? and height=?'
        cur.execute(sql, (cm_b, dcoef_b, rvect_b, tvect_b, camera_model, width, height))

    @staticmethod
    def crud_calibration_delete_by_composite(camera_modelid, height, width):
        '''delete calibration by unique key
        kargs should be:
        width: height: camera_model:
        '''
        cur = DB.cConn.cursor()
        sql = DB._sql_delete('calibration', camera_modelid=camera_modelid, height=height, width=width)
        cur.execute(sql)

    @staticmethod
    def _sql_read(table, **kwargs):
        ''' Generates SQL for a SELECT statement matching the kwargs passed. '''
        sql = list()
        sql.append("SELECT * FROM %s " % table)
        if kwargs:
            sql.append("WHERE " + " AND ".join("%s = '%s'" % (k, v) for k, v in kwargs.iteritems()))
        sql.append(";")
        return "".join(sql)

    @staticmethod
    def _sql_upsert(table, **kwargs):
        ''' update/insert rows into objects table (update if the row already exists)
            given the key-value pairs in kwargs '''
        keys = ["%s" % k for k in kwargs]
        values = ["'%s'" % v for v in kwargs.values()]
        sql = list()
        sql.append("INSERT INTO %s (" % table)
        sql.append(", ".join(keys))
        sql.append(") VALUES (")
        sql.append(", ".join(values))
        sql.append(") ON DUPLICATE KEY UPDATE ")
        sql.append(", ".join("%s = '%s'" % (k, v) for k, v in kwargs.iteritems()))
        sql.append(";")
        return "".join(sql)

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
