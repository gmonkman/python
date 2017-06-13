#!/usr/bin/env python

'''
Watershed segmentation
=========

This program demonstrates the watershed segmentation algorithm
in OpenCV: watershed().

Usage
-----
watershed.py [image filename]

Keys
----
  1     - Subject marker
  2     - Not subject marker
  SPACE - update segmentation
  h     - save subject histo
  r     - reset
  a     - toggle autoupdate
  ESC   - exit
  n     - next image
'''


# Python 2/3 compatibility
import sys
import numpy as np
import cv2
from common import Sketcher

import funclib.baselib as _baselib
from opencvlib.imgpipes.generators import FromPaths
from opencvlib import getimg as _getimg
from opencvlib import transforms as _transform
import opencvlib.histo as _histo


class App:
    '''main app'''
    def __init__(self, fld, Trans):
        self._folder = fld
        self._Gen = FromPaths(fld)
        self._files = [s[1] for s in self._Gen.generate(pathonly=True)]
        self.files_idx = 0
        self.setimg()
        self._Transforms = Trans
        self.subject_hist = None
        self.cur_marker = None
        self.auto_update = False


    def setimg(self, nd_img=None, executeTransforms=True):
        '''(ndarray) -> void
        Set/get the next img.

        nd_img:
            override load and use this image
        '''

        if not isinstance(nd_img, np.ndarray):
            self._img = _getimg(self._files[self.files_idx])
            self.files_idx += 1
            if self._img is None:
                raise Exception('Failed to load image file: %s' % self._files[self.files_idx])
        else:
            self._img = nd_img

        if executeTransforms:
            self._img = self._Transforms.executeQueue(self._img)

        self.subj_mask = None
        self.non_subj_mask = None

        h, w = self._img.shape[:2]
        self.markers = np.zeros((h, w), np.int32)
        self.markers_vis = self._img.copy()
        self.cur_marker = 1
        self.colors = np.int32(list(np.ndindex(2, 2, 2))) * 255

        self.sketch = Sketcher(
            'img', [self.markers_vis, self.markers], self.get_colors)  



    def get_colors(self):
        ''' -> list, int
        Get colors'''
        return list(map(int, self.colors[self.cur_marker])), self.cur_marker



    def watershed(self):
        ''' -> void
        watershed'''
        m = self.markers.copy() #our lines, with rgb values
        cv2.imshow('self.markers', m.astype('uint8'))
        cv2.watershed(self._img, m) #m is our mask, =1 where subject, 2 where not subject, -1 where questionable
        overlay = self.colors[np.maximum(m, 0)] 
        cv2.imshow('self.overlay', overlay.astype('uint8'))
        self.subject_histograms.append(m == 2)
        self.nonsubject_histograms.append(m == 1)
        vis = cv2.addWeighted(self._img, 0.5, overlay,
                              0.5, 0.0, dtype=cv2.CV_8UC3)
        cv2.imshow('watershed', vis)



    def grab_subj_hist(self, accumulate=True):
        '''get histogram of image
        and set to self.subject_hist
        '''
        if _baselib.isempty(self.subj_mask):
            print('Watershed has not been successfully run')
            return
        _histo.histo_hsv(self._img, self.subject_hist, (0, 1), self.subj_mask, accumulate=True)



#M = cv2.calcHist([hsv],[0, 1], None, [180, 256], [0, 180, 0, 256] )
#I = cv2.calcHist([hsvt],[0, 1], None, [180, 256], [0, 180, 0, 256] )
#cv2.calcHist(images, channels, mask, histSize, ranges[, hist[, accumulate]])

    def run(self):
        ''' -> void
        main loop'''
        while cv2.getWindowProperty('img', 0) != -1 or cv2.getWindowProperty('watershed', 0) != -1:
            ch = cv2.waitKey(50)
            if ch == 27:
                break
            
            if ch == ord('1'):
                self.cur_marker = ch - ord('0')
                print('marker: SUBJECT')

            if ch == ord('2'):
                self.cur_marker = ch - ord('0')
                print('marker: NOT SUBJECT')

            if ch == ord(' ') or (self.sketch.dirty and self.auto_update):
                self.watershed()
                self.sketch.dirty = False
           
            if ch in [ord('a'), ord('A')]:
                self.auto_update = not self.auto_update
                print('auto_update if', ['off', 'on'][self.auto_update])
            
            if ch in [ord('r'), ord('R')]:
                self.markers[:] = 0
                self.markers_vis[:] = self._img
                self.sketch.show()
            
            if ch in [ord('n'), ord('R')]:
                self.setimg()

            if ch in [ord('h'), ord('H')]:
                self.grabhist()
                print('Histogram accumulated')


        cv2.destroyAllWindows()


if __name__ == '__main__':
    fn = sys.argv[1]
    print(__doc__)

    Ts = _transform.Transforms()
    Ts.add(_transform.Transform(_transform.histeq_color)) #1 arg, the img, autoconverts to HSV
    App(fn).run()
