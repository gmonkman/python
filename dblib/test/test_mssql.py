'''unit tests for mssql'''
import unittest
import dblib.mssql as mssql
import csv
import funclib.iolib as iolib

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    _TMP_SQL = "CREATE TABLE #test(id INT IDENTITY(1,1), x CHAR(1));"
    _INSERT_SQL = "INSERT #test(x) VALUES ('a');"
    _UPDATE_SQL = "UPDATE #test(x) set x='z' WHERE x='a'"
    _DELETE_SQL_A = "DELETE FROM #test where x='a'"
    _SELECT_SQL_A = "SELECT * FROM #test where x='a'"
    _SELECT_SQL_ALL = "SELECT * FROM #test"

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.server = '(local)'
        self.security = 'integrated'
        self.dbname = 'imagedb'


    unittest.skip('test_conn tested')
    def test_conn(self):
        '''test the histo function'''
        cnn = mssql.Conn(dbname=self.dbname, server=self.server)
        cnn.close()

        with mssql.Conn('imagedb', '(local)') as cnn:
            pass



    #@unittest.skip('histo tested')
    def test_execute(self):
        fld = 'C:/GISDATA/_review/open-names_2904657/test'
        for fname in iolib.file_list_generator1(fld, '*.csv', recurse=True):
            with mssql.Conn('gazetteer', '(local)') as cnn:
                with open(fname, encoding='utf-8-sig') as f:
                    reader = csv.reader(f, delimiter=",")
                    for row in reader:
                        row = [s.replace("'","''") for s in row]
                        ins = "'" + "','".join(row) + "'"
                        sql = "INSERT INTO os_open_names SELECT %s" % ins
                        with cnn.cursor() as cur:
                            cur.execute(sql)


if __name__ == '__main__':
    unittest.main()
