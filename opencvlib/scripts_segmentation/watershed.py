# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import

'''
Use watershed to segment the subject from images.

Usage
-----
watershed.py [folder]

Keys
----
  1     - Subject marker
  2     - Not subject marker
  SPACE - update segmentation
  h     - save subject histo to memory
  s     - dump histo to a file
  r     - reset
  b     - try backprojection
  a     - toggle autoupdate
  ESC   - exit
  n     - next image
'''


# Python 2/3 compatibility
import os.path as _path
from enum import Enum as _Enum


import argparse
import numpy as _np
import cv2 as _cv2

from opencvlib.common import Sketcher

import funclib.baselib as _baselib
import funclib.iolib as _iolib

from opencvlib.imgpipes.generators import FromPaths
from opencvlib import getimg as _getimg
from opencvlib import transforms as _transform
import opencvlib.histo as _histo

from inspect import getsourcefile
from os.path import abspath
from os.path import join
from os.path import normpath

from opencvlib.view import show


def script_folder():
    '''returns folder of this py'''
    return abspath(getsourcefile(lambda: 0))

_DUMP_DIR = normpath(join(script_folder(), '../../bin/watershedhisto'))
_EXT_NORMALISED = '.nrm'
_EXT = '.hst'


class eSource(_Enum):
    '''where did we get the histo'''
    FromFile = 0
    Memory = 1


class App:
    '''main app'''
    def __init__(self, fld, Trans):
        self._folder = fld
        self._Gen = FromPaths(fld)
        self._Transforms = Trans #we have to pass in Trans to be applied later, as the generator only does filepaths here
        self._files = [s[1] for s in self._Gen.generate(pathonly=True)]
        self._files_idx = 0
        self.setimg()
        self.subject_hist = [] #main histogram of subject
        self.cur_marker = None
        self._auto_update = False
        self._subj_mask = None
        self.cur_marker = 1 #subject
        print('Marker:Subject')
        self.load_saved_histos()

    
    def load_saved_histos(self):
        '''load saved normalised histos
        from the file system'''
        if not isinstance(LOAD_FROM, str):
            print('Failed to load histos from %s' % LOAD_FROM)
        fld = _path.normpath(_path.join(LOAD_FROM, '*' + _EXT_NORMALISED))

        hists = _histo.hist_load_from_folder(fld, FILE_PREFIX)
        for h in hists:
            self.subject_hist.append([h, eSource.FromFile])
        print('Loaded subject histogram(s) from %s' % LOAD_FROM)


    def reset(self):
        '''reset markers and saved
        histo data'''
        self.markers[:] = 0
        self.markers_vis[:] = self._img
        self.sketch.show()
        self.subject_hist = [] #list of lists [[hist,was_loaded]] main histogram of subject 
        self._subj_mask = None
        print('All histograms and markers reset')

        
    def setimg(self, nd_img=None, executeTransforms=True):
        '''(ndarray) -> void
        Set/get the next img.

        nd_img:
            override load and use this image
        '''
        
        self._curr_imgpath = self._files[self._files_idx]

        if not isinstance(nd_img, _np.ndarray):
            self._img = _getimg(self._files[self._files_idx])
            self._files_idx += 1
            if self._img is None:
                raise Exception('Failed to load image file: %s' % self._files[self._files_idx])
        else:
            self._img = nd_img

        if executeTransforms and not self._Transforms is None:
            self._img = self._Transforms.executeQueue(self._img)

        self.subj_mask = None
        self.non_subj_mask = None

        h, w = self._img.shape[:2]
        self.markers = _np.zeros((h, w), _np.int32)
        self.markers_vis = self._img.copy()
        self.cur_marker = 1
        self.colors = _np.int32(list(_np.ndindex(2, 2, 2))) * 255
        print('Loaded %s' % self._curr_imgpath)
        self.sketch = Sketcher(
            'img', [self.markers_vis, self.markers], self.get_colors)  


    def back_proj(self):
        '''Apply back proj using cached histogram(s)
        
        Each histogram is used in bkproj
        and the bkproj with the highest match
        is used
        '''

        if not self.subject_hist:
            print('No accumulated histogram, cannot BackProject')
            return
        ihsv = _cv2.cvtColor(self._img, _cv2.COLOR_BGR2HSV)
        
        bkprojs = [_cv2.calcBackProject([ihsv], (0, 1), b[0], (0, 180, 0, 256), 1)  for b in self.subject_hist]

        sumbp = [bk.sum() for bk in bkprojs]
        i = sumbp.index(max(sumbp))
        bkproj = bkprojs[i]

        disc = _cv2.getStructuringElement(_cv2.MORPH_ELLIPSE, (5, 5))
        _cv2.filter2D(bkproj, -1, disc, bkproj)
        bkproj = _transform.resize(bkproj, width=400)
        _cv2.imshow('Best BackProject Match', bkproj)


    def get_colors(self):
        ''' -> list, int
        Get colors'''
        return list(map(int, self.colors[self.cur_marker])), self.cur_marker



    def watershed(self):
        ''' -> void
        Show the watershed segmentation results'''
        m = self.markers.copy() #our lines, with rgb values
        _cv2.watershed(self._img, m) #m is our mask, =1 where subject, 2 where not subject, -1 where questionable
        overlay = self.colors[_np.maximum(m, 0)] #the regions, containing relevant number, eg 1 for subject
        self._subj_mask = (m == 1)
        vis = _cv2.addWeighted(self._img, 0.5, overlay,
                              0.5, 0.0, dtype=_cv2.CV_8UC3)
        vis = _transform.resize(vis, width=800)
        _cv2.imshow('watershed', vis)



    def grab_subj_hist(self):
        '''get histogram of image
        and set to self.subject_hist
        '''
        if _baselib.isempty(self._subj_mask):
            print('Watershed has not been successfully run')
            return

        #_histo.histo_hsv - normalizes by default
        self.subject_hist.append([_histo.histo_hsv(self._img, self.subject_hist, (0, 1), self._subj_mask, accumulate=False), eSource.Memory])  #False, ie not preloaded
        print('Historgram saved to Memory')


    def _save_to_file(self):
        '''(bool) -> void
        Save all added historgrams to a file.
        Histograms are prenormalized in grab_subj_hist
        '''
        if not self.subject_hist:
            print('No histogram to save')
            return

        for ind, h in enumerate(self.subject_hist):
            if h[1] == eSource.Memory:
                assert isinstance(h[0], _np.ndarray)
                fname = _iolib.get_file_parts(self._curr_imgpath)[1]
                fname = _path.normpath(_path.join(_DUMP_DIR, FILE_PREFIX + '_' + fname + _EXT_NORMALISED))
                h[0].dump(fname)
                print('Saved histogram to %s.' % fname)
                self.subject_hist[ind][1] = eSource.FromFile



#M = _cv2.calcHist([hsv],[0, 1], None, [180, 256], [0, 180, 0, 256] )
#I = _cv2.calcHist([hsvt],[0, 1], None, [180, 256], [0, 180, 0, 256] )
#_cv2.calcHist(images, channels, mask, histSize, ranges[, hist[, accumulate]])

    def run(self):
        ''' -> void
        main loop'''
        while _cv2.getWindowProperty('img', 0) != -1 or _cv2.getWindowProperty('watershed', 0) != -1:
            ch = _cv2.waitKey(50)
            if ch == 27:
                break
            
            if ch == ord('1'):
                self.cur_marker = ch - ord('0')
                print('marker: SUBJECT')

            if ch == ord('2'):
                self.cur_marker = ch - ord('0')
                print('marker: NOT SUBJECT')

            if ch == ord(' ') or (self.sketch.dirty and self._auto_update):
                self.watershed()
                self.sketch.dirty = False
           
            if ch in [ord('a'), ord('A')]:
                self._auto_update = not self._auto_update
                print('auto_update if', ['off', 'on'][self._auto_update])
            
            if ch in [ord('r'), ord('R')]:
                self.reset()
            
            if ch in [ord('n'), ord('R')]:
                self.setimg()

            if ch in [ord('h'), ord('H')]:
                self.grab_subj_hist()

            if ch in [ord('s'), ord('S')]:
                self._save_to_file()

            if ch in [ord('b'), ord('B')]: #try backprojection
                self.back_proj()

        _cv2.destroyAllWindows()



if __name__ == '__main__':

    cmdline = argparse.ArgumentParser(description='Run watershed segmentation and try back projection'
                                    'Example:\n'
                                    'watershed.py "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/lobster" -l "C:/development/python/opencvlib/bin/watershedhisto" -p LOBSTER'
                                    'watershed.py "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler" -l "C:/development/python/opencvlib/bin/watershedhistobass" -p BASS'
                                    )

    cmdline.add_argument('imgfolder', help='Folder with the images', default='')
    cmdline.add_argument('-l', '--loadfrom', help='Load files from this folder.', default='')
    cmdline.add_argument('-p', '--prefix', help='File prefix for saving or loading.', default='')
    args = cmdline.parse_args()


    fn = args.imgfolder
    FILE_PREFIX = args.prefix
    LOAD_FROM = normpath(args.loadfrom)

    _DUMP_DIR = normpath(LOAD_FROM)


    print(__doc__)

    Ts = None

    #Ts = _transform.Transforms()
    #Ts.add(_transform.Transform(_cv2.fastNlMeansDenoisingColored,None,10,10,7,21))
    #Ts.add(_transform.Transform(_transform.equalize_adapthist)) #1 arg, the img, autoconverts to HSV
    App(fn, Ts).run()
