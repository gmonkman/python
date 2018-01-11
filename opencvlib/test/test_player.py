'''unit tests for player.py'''
import unittest
from inspect import getsourcefile as _getsourcefile
import os.path as _path



import opencvlib.player as player
import funclib.iolib as _iolib
import opencvlib.transforms as transforms

class Test(unittest.TestCase):
    '''unittest for streams'''
    def setUp(self):
        '''setup variables etc for use in test cases
        '''
        self.pth = _iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
        self.modpath = _path.normpath(self.pth)
        #self.streampath = _path.normpath(_path.join(self.modpath, 'bin/movie/test-mpeg_512kb.mp4'))
        self.streampath = _path.normpath(_path.join(self.modpath, 'bin/movie/lobster-lowres.mp4'))
        self.output_folder = _path.normpath(_path.join(self.modpath, 'output'))


    def test(self):
        '''test'''
        print(player.__doc__)
        T = transforms.Transforms()
        T.add(transforms.Transform(transforms.equalize_adapthist))
        P = player.MultiProcessStream(self.streampath, T)

        P.play()



if __name__ == '__main__':
    unittest.main(verbosity=2)
