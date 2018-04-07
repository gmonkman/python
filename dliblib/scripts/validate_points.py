# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Takes an vgg file of point landmarks
and plots the point angle and distance from
the origin to find outliers.

Currently hard coded for the 19 bass landmarks'''

import argparse

import dliblib.vgg2xml as vgg2xml
from os import path as _path

import numpy as np
from sklearn import svm
import xlwings


from funclib.iolib import PrintProgress as _PP
import funclib.iolib as iolib
from opencvlib.imgpipes import vgg as _vgg
from opencvlib.imgpipes.generators import VGGROI
from geometry import Point
from plotlib import qplot


def main():
    '''main
    '''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    cmdline.add_argument('vgg_in', help='Path to the vgg json file')
    #cmdline.add_argument('xml_out', help='Name of the outputted XML file, must not exist.')

    args = cmdline.parse_args()
    vgg_in = _path.normpath(args.vgg_in)

    x = sum(1 for n in _vgg.imagesGenerator(skip_imghdr_check=True))
    PP = _PP(x)
    _vgg.load_json(vgg_in)

    labels = [str(x+1) for x in range(19)]

    pts_train = []
    pts_images_train = []
    _ = [pts_train.append([]) for n in range(19)]
    _ = [pts_images_train.append([]) for n in range(19)] #image label of every point

    #region get train
    print('\nGenerating training points')
    PP.max = sum([1 for x in _vgg.imagesGenerator(skip_imghdr_check=True, file_attr_match={'is_train':'1'})])
    for vggImg in _vgg.imagesGenerator(skip_imghdr_check=True, file_attr_match={'is_train':'1'}):
        PP.increment()
        assert isinstance(vggImg, _vgg.Image)

        for vggReg in vggImg.roi_generator(shape_type='point'):
            assert isinstance(vggReg, _vgg.Region)
            lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('pts', '') == '' else int(vggReg.region_attr['pts'])
            pts_train[lbl - 1].append(Point(vggReg.x, vggReg.y)) #i.e PTS[0] has all the "01" points, PTS[1] as the "02" points
            pts_images_train[lbl-1].append(vggImg.filename) #all the point labels, indexes will match those of PTS, so we can retrieve problem images

    pts_images_train = np.asarray(pts_images_train)
    train = [[(pt.distance(), pt.angle_origin()) for pt in label] for label in pts_train]

    train_angles = [[pt.angle_origin() for pt in label] for label in pts_train]
    train_distances = [[pt.distance() for pt in label] for label in pts_train]
    #endregion



    #region Load all data
    pts_images_all = []
    pts_all = []
    _ = [pts_images_all.append([]) for n in range(19)] #image label of every point
    _ = [pts_all.append([]) for n in range(19)]


    #print('\nGenerating full points list')
    PP = _PP(sum([1 for x in _vgg.imagesGenerator(skip_imghdr_check=True)]), init_msg="\nGenerating full points list")
    for vggImg in _vgg.imagesGenerator(skip_imghdr_check=True):
        PP.increment()
        assert isinstance(vggImg, _vgg.Image)

        for vggReg in vggImg.roi_generator(shape_type='point'):
            assert isinstance(vggReg, _vgg.Region)
            lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('pts', '') == '' else int(vggReg.region_attr['pts'])
            pts_all[lbl - 1].append(Point(vggReg.x, vggReg.y)) #i.e PTS[0] has all the "01" points, PTS[1] as the "02" points
            pts_images_all[lbl-1].append(vggImg.filename) #all the point labels, indexes will match those of PTS, so we can retrieve problem images

    pts_images_all = np.asarray(pts_images_all)

    all_ = [[(pt.distance(), pt.angle_origin()) for pt in label] for label in pts_all]
    #endregion

    PP = _PP(len(all_), init_msg='\nDetecting outliers...')
    #region Apply the model to predict outliers
    clf = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
    problems = []
    for i, landmark_group in enumerate(all_):
        PP.increment()
        clf.fit(train[i])
        res = clf.predict(landmark_group) #array of 1s and -1s
        res[res > 0] = 0 #set ok to false, as we just want outliers
        res = res.astype('bool')
        problem = np.extract(res, pts_images_all[i])
        problems.append(problem.tolist())
    #endregion


    #qplot.scatter(train_angles, train_distances, labels)
    #iolib.writecsv('c:/temp/validate_results.csv', problems, labels)
    xlwings.view(problems)




if __name__ == "__main__":
    main()
