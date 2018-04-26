# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
'''unit tests for features'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path
import funclib.iolib as iolib
import opencvlib
import opencvlib.perspective as perspective


class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.this_file_path = _path.normpath(iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0])
        self.module_root = _path.normpath(opencvlib.__path__[0]) #root of opencvlib
        self.test_images_path = _path.normpath(_path.join(self.module_root, 'test/bin/images'))
        self.resources = _path.normpath(_path.join(self.module_root, 'test/bin/perspective'))


    #@unittest.skip("Temporaily disabled while debugging")
    def test_depth_estimates(self):
        '''test'''
        xp30 = {'focal_distance_mm':5., 'cmos_rows':3240, 'cmos_cols':4320, 'cmos_height_mm':4.55, 'cmos_width_mm':6.17}
        xp30_test_case1 = {'image':'xp30_1m_1.jpg', 'subj_dist':1000, 'measured_dist_px':683, 'measured_dist_mm':200}
        xp30_test_case2 = {'image':'xp30_1m_2.jpg', 'subj_dist':1000, 'measured_dist_px':648, 'measured_dist_mm':190}

        M1 = perspective.Measure(xp30_test_case1['subj_dist'], xp30_test_case1['measured_dist_mm'], xp30_test_case1['measured_dist_px'])
        C1 = perspective.Camera(xp30['focal_distance_mm'], xp30['cmos_cols'], xp30['cmos_rows'], xp30['cmos_width_mm'], xp30['cmos_height_mm'])

        M2 = perspective.Measure(xp30_test_case2['subj_dist'], xp30_test_case2['measured_dist_mm'], xp30_test_case2['measured_dist_px'])
        C2 = perspective.Camera(xp30['focal_distance_mm'], xp30['cmos_cols'], xp30['cmos_rows'], xp30['cmos_width_mm'], xp30['cmos_height_mm'])
        d = perspective.subjdist_camera(C1, M1)
        d = perspective.subjdist_knowndist(M1, M1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
