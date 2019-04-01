'''unit tests for mssql'''
import unittest
import dblib.alchemylib as alc

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

    #unittest.skip('test_conn tested')
    def test_conn_integrated(self):
        '''test integrated security, know user/pw works'''
        cnn = alc.ConnectionString(self.server, self.dbname, use_integrated=True)
        alc.create_engine_mssql(cnn.mssql_connection_string())
        try:
            alc.ENGINE.dispose()
        except:
            pass



if __name__ == '__main__':
    unittest.main()
