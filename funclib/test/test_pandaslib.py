
# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import funclib.iolib as iolib

import numpy as np
import pandas as pd
import funclib.pandaslib as pdl
import funclib



class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.this_file_path = _path.normpath(iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
        self.module_root = _path.normpath(funclib.__path__[0]) #root of opencvlib
        self.bin_path = _path.normpath(_path.join(self.module_root, 'test/bin'))
        f = _path.normpath(_path.join(self.bin_path, 'fish.xlsx'))
        self.df = pd.read_excel(f, 'fish', header=0)



    @unittest.skip("Temporaily disabled while debugging")
    def test_GroupBy(self):
        '''test'''
        pdl.GroupBy.PRECISION = 5
        GB = pdl.GroupBy(self.df, ['fish', 'sex'], ['length', 'weight'], np.mean, np.median, pdl.GroupBy.fCI_str(95), pdl.GroupBy.fCI(95), pdl.GroupBy.fPercentile(25))
        out = _path.join(self.bin_path, 'fish_tmp.xlsx')
        GB.to_excel(out, fail_if_exists=False)
        print(GB.result)

    #@unittest.skip("Temporaily disabled while debugging")
    def test_df_fromstring(self):
        '''test'''
        s = """col1,col2,col3\n1,4.4,99\n2,4.5,200\n3,4.7,65\n4,3.2,140"""
        df = pdl.df_fromstring(s)


if __name__ == '__main__':
    unittest.main(verbosity=2)
