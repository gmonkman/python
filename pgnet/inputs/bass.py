# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Generate bass images
Call init_() to initalse data classes

This reads the image paths from ini file in package root
'''
#Further more advanced example
#https://github.com/tensorflow/models/blob/master/tutorials/image/cifar10/cifar10_input.py
import os.path as _path
from random import sample as _sample
from random import shuffle as _shuffle

import tensorflow as _tf
import numpy as _np
import cv2 as _cv2


from funclib.iolib import PrintProgress as _PP
from funclib.iolib import file_count as _filecnt
from opencvlib.info import ImageInfo as _inf
from opencvlib.imgpipes.generators import FromPaths as _FromPaths
import opencvlib.transforms as _transforms
import pgnet.ini as _ini


CLASSES = ['not_bass', 'bass']
NUM_CLASSES = len(CLASSES)
BACKGROUND_CLASS_ID = len(CLASSES)

W_ORIG = _ini.Cfg.tryread('images', 'WIDTH', error_on_read_fail=True)
H_ORIG = _ini.Cfg.tryread('images', 'HEIGHT', error_on_read_fail=True)
CH_ORIG = _ini.Cfg.tryread('images', 'CHANNELS', error_on_read_fail=True)
W = 200; H = 200 #hardcoded for now

#these will be an instance of class ImageFromPaths
BassTrain = None
BassEval = None #Validation - Model  Tuning
BassTest = None
DebugImages = None


class ImagesFromPaths():
    '''Creates list of imagepaths with their labels.

    img_paths and labels correspond by index.
    ie. the img_paths[12] imagepath has label labels[12]
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
            eg, [['c:/a.jpg', 1, 600, 128],
                 ['c:/b.jpg'], 0, 600, 128]
                 ['c:/12.jpg'], 0, 800, 600]]
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
        return len(self.img_info_list)


    def _read(self, skip_res_test=True):
        '''(bool) -> void
        creates the full list of files
        with their labels and resolutions and
        sets as class propertes.

        The assumption is that each path contains a single
        object class, and the label for the object class
        is set on per path

        skip_res_test:
            dont check resolutions meet an
            expected value
        '''
        self.img_info_list = []
        self.img_paths = []
        self.labels = []
        drop_candidates = []
        print('\nChecking resolutions of images in folder(s) %s' %  str(self._paths_with_images))
        pp = _PP(_filecnt(self._paths_with_images, wildcards='*.jpg', recurse=False))

        for i, pth in enumerate(self._paths_with_images):
            FP = _FromPaths(pth, wildcards='.jpg')
            for _, fname, _ in FP.generate(pathonly=True):
                pp.increment()
                fname = _path.normpath(fname)
                w, h = _inf.resolution(fname)
                if skip_res_test:
                    lbl = self._labels[i]
                    self.img_info_list.append([fname, lbl, h, w])
                else:
                    if w == W and h == H:
                        lbl = self._labels[i]
                        self.img_info_list.append([fname, lbl, h, w])
                    else:
                        print('Expected image res of (%s, %s), got (%s, %s)' % (W, H, w, h))
        assert self.img_info_list, 'No jpg files found in %s' % str(self._paths_with_images)

        _shuffle(self.img_info_list)
        lsts = list(map(list, zip(*self.img_info_list))) #map as zip returns list of tuples, not lists
        self.img_paths = lsts[0]
        self.labels = lsts[1]

        #fudge to drop neg trainng images to make the set fit
        #a whole nr of batch sizes
        if self.batch_size is None:
            return

        drop_candidates = [i for i, x in enumerate(self.img_info_list) if x[1] == 0] #0 is a neg image, we  have lots of them
        nr_to_drop = self.image_count % self.batch_size
        if nr_to_drop == 0:
            return

        drop_inds = _sample(drop_candidates, nr_to_drop)
        drop_inds.sort(reverse=True) #del from end of img_info_list first
        for d in drop_inds:
            del self.img_info_list[d]
            del self.labels[d]
            del self.img_paths[d]


    @property
    def Tlabels(self):
        '''return labels as a tensor'''
        assert self.labels, 'No labels initialised'
        assert len(self.labels) == len(self.img_paths), 'Number of labels and image paths did not match'
        return _tf.constant(self.ndlabels)


    @property
    def ndlabels(self):
        '''(void) -> n,1-ndarray
        labels as an ndarray

        returns:
            np.array([[1],[0],[1], ...])
        '''
        assert self.labels, 'No labels initialised'
        assert len(self.labels) == len(self.img_paths), 'Number of labels and image paths did not match'
        return _np.array(self.labels)


    @property
    def Timages(self):
        '''return all images in a tensor constant'''
        nd_images = self._make_img_array()
        return _tf.constant(nd_images)


    @property
    def ndimages(self):
        '''return all images as an 4-d n,y,x,channel
        numpy array'''
        nd_images = self._make_img_array()
        return nd_images

    @property
    def lst_imgs_and_lbls(self):
        '''return list of images and labels

        Example:
        >>>print(bass.lst_imgs_and_lbls)
        [['c:\1.jpg', 1]
            ['c:\2.jpg', 0]
        ]]
        '''
        return list(zip(self.img_paths, self.labels))


    def _make_img_array(self):
        '''(void) -> ndarray
        make numpy array of images,
        returns as float64 type, range 0 - 1
        not uint8
        '''
        assert self.labels, 'No labels initialised'
        assert len(self.labels) == len(self.img_paths), 'Number of labels and image paths did not match'
        print('\nStacking ndarrays with images (and their labels) from the file system....')
        prog = _PP(len(self.img_paths))
        for i, f in enumerate(self.img_paths):
            img = _cv2.imread(f)
            img = _transforms.resize(img, width=W, height=H)
            img = _transforms.toFloat(img, _transforms.eCvt.uint8_to_1minus1)
            if i == 0:
                nd_imgs = _np.expand_dims(img, 0)
            else:
                nd_imgs = _np.concatenate([nd_imgs, _np.expand_dims(img, 0)], 0)
            prog.increment()

        assert nd_imgs.shape[0] == len(self.img_paths), 'Depth stack size of images ndarray did not match expected number of images'
        return nd_imgs





def init_(batch_size=10, init=('DebugImages', 'BassTest', 'BassEval', 'BassTrain')):
    '''(int, str|list|tuple') ->void
    initialise classes which are used to retrieve images.
    Paths to the images are defined in pgnet.ini in
    the module root.

    batch_size:
        the batch size which will be used
    init:
        select which image feeders to initialise.
        ['DebugImages', 'BassTest', 'BassEval', 'BassTrain']
    '''
    opts = ['DebugImages', 'BassTest', 'BassEval', 'BassTrain']

    if isinstance(init, str):
        init = [init]

    for s in init:
        if not s in opts:
            raise ValueError('Invalid bass init_ option %s' % s)

    if 'BassTrain' in init:
        pos = _path.normpath(_path.join(_ini.Cfg.tryread('bass.py', 'train_images_path'), 'bass'))
        neg = _path.normpath(_path.join(_ini.Cfg.tryread('bass.py', 'train_images_path'), 'not_bass'))
        global BassTrain
        BassTrain = ImagesFromPaths([pos, neg], [1, 0], batch_size=batch_size)

    if 'BassEval' in init:
        pos = _path.normpath(_path.join(_ini.Cfg.tryread('bass.py', 'eval_images_path'), 'bass'))
        neg = _path.normpath(_path.join(_ini.Cfg.tryread('bass.py', 'eval_images_path'), 'not_bass'))
        global BassEval
        BassEval = ImagesFromPaths([pos, neg], [1, 0], batch_size=batch_size)

    if 'BassTest' in init:
        pos = _path.normpath(_path.join(_ini.Cfg.tryread('bass.py', 'test_images_path'), 'bass'))
        neg = _path.normpath(_path.join(_ini.Cfg.tryread('bass.py', 'test_images_path'), 'not_bass'))
        global BassTest
        BassTest = ImagesFromPaths([pos, neg], [1, 0], batch_size=batch_size)

    if 'DebugImages' in init:
        pos = _path.normpath(_ini.Cfg.tryread('bass.py', 'debug_images_path'))
        global DebugImages
        DebugImages = ImagesFromPaths([pos], [1])
