# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use

'''unit tests for features'''
import unittest

from plotlib import stackedbargraph as sbg

class Test(unittest.TestCase):
    '''unittest for keypoints'''

    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        pass


    def test_demo(self):
        '''test demo'''
        SBG = sbg.StackedBarGrapher()
        SBG.demo()



if __name__ == '__main__':
    unittest.main()
    
