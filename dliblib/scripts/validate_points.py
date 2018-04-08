# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
'''Takes an vgg file of point landmarks
and plots the point angle and distance from
the origin to find outliers. Currently performs
a KNN on angle and distance to/from origin
but this produces too many 'outliers'

Currently hard coded for the 19 bass landmarks'''

import argparse


from os import path as _path

import numpy as np
from sklearn.neighbors import KNeighborsClassifier as KNN

from funclib.iolib import PrintProgress as _PP
import funclib.iolib as iolib
from opencvlib.imgpipes import vgg as _vgg

from geometry import Point
from plotlib import qplot

LABELS = [str(x+1) for x in range(19)]


def initialise_feature_matrix(n):
    '''create an empty feature matrix
    '''



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

    train_vectors = []
    train_images = []
    train_labels = []

    #initialise empty matrix


    for vggImg in _vgg.imagesGenerator(skip_imghdr_check=True, file_attr_match={'is_train':'1'}):
        PP.increment()
        assert isinstance(vggImg, _vgg.Image)
        for vggReg in vggImg.roi_generator(shape_type='point'):
            assert isinstance(vggReg, _vgg.Region)
            lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('pts', '') == '' else int(vggReg.region_attr['pts'])
            Pt = Point(vggReg.x, vggReg.y)
            train_vectors.append((Pt.angle_origin(), Pt.distance()))
            train_images.append(vggImg.filename)
            train_labels.append(lbl)
    train_angles, train_distances = zip(*train_vectors) #for plotting

    #for i in range(len(all_angles)):
    qplot.scatter(train_angles, train_distances, data_labels=train_labels, ptsizes=0)

    #endregion


    #region KNN training
    knn_ = KNN(n_neighbors=5)
    knn_.fit(train_vectors, train_labels)


    #region Load all data
    PP = _PP(sum([1 for x in _vgg.imagesGenerator(skip_imghdr_check=True)]), init_msg="\nGenerating full points list")

    all_vectors = []
    all_labels = []
    all_images = []

    for vggImg in _vgg.imagesGenerator(skip_imghdr_check=True):
        PP.increment()
        assert isinstance(vggImg, _vgg.Image)
        for vggReg in vggImg.roi_generator(shape_type='point'):
            assert isinstance(vggReg, _vgg.Region)
            lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('pts', '') == '' else int(vggReg.region_attr['pts'])
            Pt = Point(vggReg.x, vggReg.y)
            all_vectors.append((Pt.angle_origin(), Pt.distance()))
            all_images.append(vggImg.filename)
            all_labels.append(int(lbl))

    #all_angles, all_distances = zip(*all_vectors) #for plotting
    #endregion

    pred = knn_.predict(all_vectors)
    pred = np.asarray(pred)
    expected = np.asarray(all_labels)
    status = (pred != all_labels)
    bad = np.asarray(all_images)[status]

    #for i in range(len(all_angles)):
     #   qplot.scatter([all_angles[i]], [all_distances[i]], data_labels=all_labels)





if __name__ == "__main__":
    main()
