# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
'''Takes an vgg file of point landmarks
and plots the point angle and distance from
the origin to find outliers. Currently performs
a KNN on angle and distance to/from origin
but this produces too many 'outliers'

Currently hard coded for the 19 bass landmarks'''

import argparse


from os import path as _path

from funclib.iolib import PrintProgress as _PP
import funclib.iolib as iolib
from opencvlib.imgpipes import vgg as _vgg
from funclib.baselib import list_flatten
from geometry import Point
from plotlib import qplot

LABELS = [str(x+1) for x in range(19)]




def main():
    '''main
    '''
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    cmdline.add_argument('vgg_in', help='Path to the vgg json file')

    args = cmdline.parse_args()
    vgg_in = _path.normpath(args.vgg_in)
    _vgg.load_json(vgg_in)

    if False:
        #region Load train data
        x = sum(1 for n in _vgg.imagesGenerator(skip_imghdr_check=True))
        PP = _PP(x, init_msg='Loading training data and creating model...')
        PP.max = sum([1 for x in _vgg.imagesGenerator(skip_imghdr_check=True, file_attr_match={'is_train':'1'})])

        train_vectors = [[] for _ in range(19)]
        train_images = [[] for _ in range(19)]
        train_labels = [[] for _ in range(19)]

        #initialise empty matrix

        for vggImg in _vgg.imagesGenerator(skip_imghdr_check=True, file_attr_match={'is_train':'1'}):
            PP.increment()
            assert isinstance(vggImg, _vgg.Image)
            for vggReg in vggImg.roi_generator(shape_type='point'):
                assert isinstance(vggReg, _vgg.Region)
                lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('pts', '') == '' else int(vggReg.region_attr['pts'])
                Pt = Point(vggReg.x, vggReg.y)
                train_vectors[lbl-1].append((Pt.angle_origin(), Pt.distance()))
                train_images[lbl-1].append(vggImg.filename)
                train_labels[lbl-1].append(lbl)

        if False:
            for i in range(len(train_vectors)):
                train_angles, train_distances = zip(*train_vectors[i]) #for plotting
                qplot.scatter(train_angles, train_distances, data_labels=train_images[i], ptsizes=4)
    #endregion



    #region Load all data
    PP = _PP(sum([1 for x in _vgg.imagesGenerator(skip_imghdr_check=True)]), init_msg="\nGenerating full points list")

    all_vectors = [[] for _ in range(19)]
    all_labels = [[] for _ in range(19)]
    all_images = [[] for _ in range(19)]
    all_angles = []
    all_distances = []
    for vggImg in _vgg.imagesGenerator(skip_imghdr_check=True):
        PP.increment()
        assert isinstance(vggImg, _vgg.Image)
        for vggReg in vggImg.roi_generator(shape_type='point'):
            assert isinstance(vggReg, _vgg.Region)
            lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('pts', '') == '' else int(vggReg.region_attr['pts'])
            Pt = Point(vggReg.x, vggReg.y)
            angle_origin = Pt.angle_origin()
            distance = Pt.distance()
            all_vectors[lbl-1].append((angle_origin, distance))
            all_angles.append(angle_origin)
            all_distances.append(distance)
            all_images[lbl-1].append(vggImg.filename)
            all_labels[lbl-1].append(int(lbl))
    #endregion
    total_points = len(list_flatten(all_vectors))
    print('\nTotal points: %s' % total_points)

    for i in range(len(all_vectors)):
        all_angles_i, all_distances_i = zip(*all_vectors[i]) #for plotting
        qplot.scatter(all_angles_i, all_distances_i, data_labels=all_images[i], xlim=(0, max(all_angles)), ylim=(0, max(all_distances)))





if __name__ == "__main__":
    main()
