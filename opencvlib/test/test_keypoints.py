'''unit tests for keypoints'''
import unittest
import opencvlib.keypoints as keypoints
import numpy as np
import cv2

class Test(unittest.TestCase):
    '''unittest for keypoints'''
    def setUp(self):
        self.pts = [cv2.KeyPoint(0, 0, 1), cv2.KeyPoint(0, 1, 1), cv2.KeyPoint(1, 0, 1), cv2.KeyPoint(1, 1, 1)]
        self.kp1 = cv2.KeyPoint(1, 1, 1., 1., 1, 1)
        self.kp2 = cv2.KeyPoint(1, 1, 1., 1., 1, 1)
        self.kp3 = cv2.KeyPoint(1, 2, 1., 3., 1, 1)
        self.kp4 = cv2.KeyPoint(1, 1, 1., 1., 1, 1)

    def test_applymask(self):
        '''unit tests for applymask'''
        
        mask = np.array([[True, False], [False, True]])

        keypoints.applymask(self.pts, mask)
        self.assertTrue(keypoints.equal(cv2.KeyPoint(0, 0, 1), self.pts[0]) and keypoints.equal(cv2.KeyPoint(1, 1, 1), self.pts[1]))


    def test_equal(self):
        '''test equal'''
        self.assertTrue(keypoints.equal(self.kp1, self.kp2))
        self.assertFalse(keypoints.equal(self.kp3, self.kp4))



if __name__ == '__main__':
    unittest.main()
