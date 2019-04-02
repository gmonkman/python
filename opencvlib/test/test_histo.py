'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path

import cv2
import numpy as np

import funclib.iolib as iolib
import opencvlib.histo as histo
import plotlib.qplot as qplot


class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        self.imgpath = _path.normpath(_path.join(self.modpath, 'bin/images/matt_pemb5.jpg'))
        self.I = cv2.imread(self.imgpath)
        self.grasspath = _path.normpath(_path.join(self.modpath, 'bin/images/grass.jpg'))
        self.Grass = cv2.imread(self.grasspath)
        self.img_random = np.random.randint(0, 256, (255, 255, 3))
        self.img_banded = np.dstack((np.random.randint(0, 100, (255, 255)), np.random.randint(100, 200, (255, 255)), np.random.randint(200, 255, (255, 255))))

    @unittest.skip("Temporaily disabled while debugging")
    def test_VisualColorHisto(self):
        '''test'''

        H = histo.VisualColorHisto(self.Grass)
        cv2.waitKey(0)
        H(cv2.cvtColor(self.Grass, cv2.COLOR_BGR2GRAY))

    #@unittest.skip("Temporaily disabled while debugging")
    def test_historgb(self):
        bins, hist = histo.histo_rgb(self.img_banded, channels=0, bins=3, normalise_img=True, normalise_histo=True)
        bins = qplot.pretty_bin(bins)
        qplot.bar_(bins, hist)

        bins, hist1, hist2, hist3 = histo.histo_rgb(self.img_banded, channels=(0, 1, 2), bins=5, normalise_img=True, normalise_histo=True)
        bins = qplot.pretty_bin(bins)
        qplot.bar_(bins, hist1)
        qplot.bar_(bins, hist2)
        qplot.bar_(bins, hist3)

        bins, hist1, hist2, hist3 = histo.histo_rgb(self.img_banded, rect_patch=(20, 40, 100, 120), channels=(0, 1, 2), bins=6, normalise_img=True, normalise_histo=True)
        bins = qplot.pretty_bin(bins)
        qplot.bar_(bins, hist1)
        qplot.bar_(bins, hist2)
        qplot.bar_(bins, hist3)
if __name__ == '__main__':
    unittest.main(verbosity=2)

