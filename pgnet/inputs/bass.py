# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Generate bass images'''
#Further more advanced example
#https://github.com/tensorflow/models/blob/master/tutorials/image/cifar10/cifar10_input.py
import os.path as _path

from random import sample as _sample

import tensorflow as _tf
import numpy as _np
import cv2 as _cv2




from funclib.iolib import PrintProgress as _PP
from opencvlib.info import ImageInfo as _inf
from opencvlib.imgpipes.generators import FromPaths as _FromPaths

#from . import pascal_trainval as pascal_trainval

CLASSES = ['not_bass', 'bass']
NUM_CLASSES = len(CLASSES)
BACKGROUND_CLASS_ID = len(CLASSES)


W = 514; H = 120 #hardcoded for now

class ImagesFromPaths():
    '''Creates list of imagepaths with their labels
    Arguments:
        batch_size
            size of batch, trims negative images so total train set fits
            is exactly divisible by batch_size. If None, nothing is done.
    Properties:
        img_paths:
            list of full image paths, eg ['c:/a.jpg','c:/b.jpg']

        labels:
            labels for images referred to in img_paths, eg [1,0]
            where label[0] is label for image img_paths[0].

        img_info_list:
            list of all images, with corresponding labels and rows and columns.
            eg, [['c:/a.jpg', 'c:/b.jpg'], [1, 0], [600, 128], [800, 512]]
    '''
    def __init__(self, paths_with_images, labels, batch_size=None):
        self._paths_with_images = [_path.normpath(s) for s in paths_with_images]
        self._labels = labels
        self.img_info_list = [] #list of lists, [imagepaths, labels, resolutions]
        self.img_paths = []
        self.labels = []
        self.batch_size = batch_size
        self._read()


    @property
    def image_count(self):
        '''sample nr'''
        return len(self._paths_with_images)


    def _read(self):
        '''creates the full list of files
        with their labels and resolutions

        The assumption is that each path contains a single
        object class, and the label for the object class
        is set on per path
        '''
        self.img_info_list = []
        self.img_paths = []
        self.labels = []
        drop_candidates = []
        for i, pth in enumerate(self._paths_with_images):
            FP = _FromPaths(pth, wildcards='.jpg')
            for _, fname, _ in FP.generate(pathonly=True):
                fname = _path.normpath(fname)
                w, h = _inf.resolution(fname)
                if w == W and h == H:
                    self.img_paths.append(fname)
                    lbl = self._labels[i]
                    self.labels.append([lbl])
                    self.img_info_list.append([fname, lbl, h, w])
                else:
                    print('Expected image res of (%s, %s), got (%s, %s)' % (W, H, w, h))

        assert self.img_info_list, 'No jpg files found in %s' % str(self._paths_with_images)

        #fudge to drop neg trainng images to make the set fit
        #a whole nr of batch sizes
        if self.batch_size is None:
            return

        drop_candidates = [i for i, x in enumerate(self.img_info_list) if x[1] == 0] #0 is a neg image, we  have lots of them
        nr_to_drop = self.image_count % self.batch_size
        if nr_to_drop == 0:
            return

        drop_inds = _sample(drop_candidates, nr_to_drop)
        for d in drop_inds:
            del self.img_info_list[d]
            del self.labels[d]
            del self.img_paths[d]


    @property
    def Tlabels(self):
        '''return labels as a tensor'''
        assert self.labels, 'No labels initialised'
        assert len(self.labels) == len(self.img_paths), 'Number of labels and image paths did not match'
        return _tf.constant(self.labels)


    @property
    def TImages(self):
        '''return all images in a tensor'''
        assert self.labels, 'No labels initialised'
        assert len(self.labels) == len(self.img_paths), 'Number of labels and image paths did not match'
        print('\nStacking ndarray with images from the file system....')
        prog = _PP(len(self.img_paths))
        for i, f in enumerate(self.img_paths):
            if i == 0:
                nd_imgs = _np.expand_dims(_cv2.imread(f), 0)
            else:
                nd_imgs = _np.concatenate([nd_imgs, _np.expand_dims(_cv2.imread(f), 0)], 0)
            prog.increment()

        assert nd_imgs.shape[0] == len(self.img_paths), 'Depth stack size of images ndarray did not match expected number of images'
        return _tf.constant(nd_imgs)


BassTrain = ImagesFromPaths(['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/train/bass',
                            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/train/not_bass'],
                            [1, 0])

BassTest = ImagesFromPaths(['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/test/bass',
                            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/test/not_bass'],
                            [1, 0])

BassEval = ImagesFromPaths(['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/eval/not_bass',
                            'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/eval/bass'],
                            [1, 0])
