'''unit tests for roi'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

#import opencvlib.roi as roi
import funclib.iolib as iolib


class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)

        self.db_path = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/digikam4.db'
        pass


    @unittest.skip("Temporaily disabled while debugging")
    def test_roi(self):
        '''test roi'''
        pass



if __name__ == '__main__':
    unittest.main()
    
