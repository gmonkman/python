'''unit tests for qplot'''
import unittest

import numpy as _np

import plotlib.qplot as qplot

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.mu_x, self.sigma_x = 100, 15
        self.x_rnd = self.mu_x + self.sigma_x*_np.random.randn(100)

        self.mu_y, self.sigma_y = 50, 7
        self.y_rnd = self.mu_y + self.sigma_y*_np.random.randn(100)

    @unittest.skip('histo tested')
    def test_histo(self):
        '''test the histo function'''
        qplot.histo(self.x_rnd, normed=True)     


    def test_scatter(self):
        '''test scatter plot'''
        qplot.scatter([self.x_rnd, self.x_rnd - 50], [self.y_rnd, self.y_rnd - 50], group_labels=('big', 'small'))

if __name__ == '__main__':
    unittest.main()
    
