# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''Takes an vgg file of point landmarks
and tries to find outliers.

Currently hard coded for the 19 bass landmarks'''

import argparse
from os import path as _path

import numpy as np
from sklearn import svm

from funclib.iolib import PrintProgress as _PP
import funclib.iolib as iolib
from opencvlib.imgpipes import vgg as _vgg
from opencvlib.imgpipes.generators import VGGROI
from geometry import Point
from plotlib import qplot
from funclib.arraylib import distances, angles_between

LABELS = [str(x+1) for x in range(19)]




def main():
    '''main
    '''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    cmdline.add_argument('vgg_in', help='Path to the vgg json file')
    #cmdline.add_argument('xml_out', help='Name of the outputted XML file, must not exist.')

    args = cmdline.parse_args()
    vgg_in = _path.normpath(args.vgg_in)
    _vgg.load_json(vgg_in)

    #region Load train data
    x = sum(1 for n in _vgg.imagesGenerator(skip_imghdr_check=True))
    PP = _PP(x, init_msg='Loading training data and creating model...')
    PP.max = sum([1 for x in _vgg.imagesGenerator(skip_imghdr_check=True, file_attr_match={'is_train':'1'})])

    train_data = np.array([])
    train_labels = []
    for vggImg in _vgg.imagesGenerator(skip_imghdr_check=True, file_attr_match={'is_train':'1'}):
        PP.increment()
        assert isinstance(vggImg, _vgg.Image)
        Pts = [None] * 19 #store all the points
        for vggReg in vggImg.roi_generator(shape_type='point'):
            assert isinstance(vggReg, _vgg.Region)
            lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('pts', '') == '' else int(vggReg.region_attr['pts'])
            Pts[lbl-1] = (vggReg.x, vggReg.y)


        for i, Pt in  enumerate(Pts):
            if isinstance(Pt, Point):
                train_labels.append(i+1) #pt labels are 1 based, enumerate is 0 based
                dists = distances(Pt, Pts)
                angles = vector_angles(Pt, Pts)
                features = np.hstack((dists, angles)).flatten()
                train_data = np.hstack(features)



    #region KNN training
    clf = svm.SVC(gamma=0.001, C=100.)
    clf.fit(train_data, train_labels)

    #region Load all data
    PP = _PP(sum([1 for x in _vgg.imagesGenerator(skip_imghdr_check=True)]), init_msg="\nGenerating full points list")

    all_data = []
    expected = []
    all_images = []

    for vggImg in _vgg.imagesGenerator(skip_imghdr_check=True):
        PP.increment()
        assert isinstance(vggImg, _vgg.Image)
        Pts = [None] * 19 #store all the points
        for vggReg in vggImg.roi_generator(shape_type='point'):
            assert isinstance(vggReg, _vgg.Region)
            lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('pts', '') == '' else int(vggReg.region_attr['pts'])
            Pts[lbl-1] = (vggReg.x, vggReg.y)


        for i, Pt in  enumerate(Pts):
            if isinstance(Pt, Point):
                expected.append(i+1) #pt labels are 1 based, enumerate is 0 based, this contains the expected labels
                dists = distances(Pt, Pts)
                angles = angles_between(Pt, Pts)
                features = np.hstack((dists, angles)).flatten()
                all_data = np.hstack(features)
                all_images.append(vggImg.filename)

        predictions = clf.predict(all_data)

        diffs = (predictions != expected)
        all_images = np.asarray(all_images)
        bad = set(all_images[diffs].tolist())  #get unique values



if __name__ == "__main__":
    main()
