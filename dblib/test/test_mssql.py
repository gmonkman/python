'''unit tests for qplot'''
import unittest
import dblib.mssql as mssql


class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.server = '(local)'
        self.security = 'integrated'
        self.dbname = 'imagedb'

    #@unittest.skip('histo tested')
    def test_conn(self):
        '''test the histo function'''
        cnn = mssql.Conn(dbname=self.dbname, server=self.server)
        cnn.close()

        with mssql.Conn('imagedb', '(local)') as cnn:
            pass


if __name__ == '__main__':
    unittest.main()
