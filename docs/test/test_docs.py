#pylint: skip-file
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path
import funclib.iolib as iolib
import funclib.arraylib as arraylib
import numpy as np
import funclib
import img2pdf
import docs
import docs.topdf as topdf

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.this_file_path = _path.normpath(iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
        self.module_root = _path.normpath(tuple(docs.__path__)[0]) #root
        self.test_images_path = _path.normpath(_path.join(self.module_root, 'test/bin/images'))
        self.x1_image_path = _path.normpath(self.test_images_path + '/X1_1990.jpg')
        self.x5_image_path = _path.normpath(self.test_images_path + '/X5_2007_2.jpg')

        img2pdf_layout = img2pdf.get_layout_fun((img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297)))


        pth = _path.normpath('%s/%s' % (self.test_images_path, 'x1_image.pdf'))
        with open(pth, "wb") as f:
            f.write(img2pdf.convert(self.x1_image_path, layout_fun=img2pdf_layout))
        
        pth = _path.normpath('%s/%s' % (self.test_images_path, 'x5_image.pdf'))
        with open(pth ,"wb") as f:
            f.write(img2pdf.convert(self.x5_image_path, layout_fun=img2pdf_layout))

        pth = _path.normpath('%s/%s' % (self.test_images_path, 'x1_x5_image.pdf'))
        with open(pth, "wb") as f:
            f.write(img2pdf.convert([self.x1_image_path, self.x5_image_path], layout_fun=img2pdf_layout))



    #@unittest.skip("Temporaily disabled while debugging")
    def test_basic(self):
        '''test cropping stacks'''
        x = 1
        pass





if __name__ == '__main__':
    unittest.main(verbosity=2)
