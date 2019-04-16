'''unit tests for mssql'''
import unittest

import pandas as pd

from funclib.stringslib import to_ascii
import funclib.iolib as iolib
import pytesseract as pyt
import funclib.pandaslib as pdl
import xlwings

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.tesseract_path = 'C:/Program Files/Tesseract-OCR'

    #@unittest.skip('test_conn tested')
    def test_img(self):
        s = pyt.image_to_data('C:/temp/sa/441/SA_441_006.jpg', config='--psm 1')
        df = pdl.df_fromstring(to_ascii(s), sep='\t')
        xlwings.view(df)
        iolib.write_to_file(s, full_file_path='c:/temp/pyt.txt')




if __name__ == '__main__':
    unittest.main()
