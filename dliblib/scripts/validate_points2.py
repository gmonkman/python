# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''Takes an vgg file of point landmarks
and tries to find outliers.

Currently hard coded for the 19 bass landmarks'''

import argparse
from os import path as _path

import numpy as np
from sklearn.preprocessing import MaxAbsScaler
import xlwings

from funclib.iolib import PrintProgress as _PP
import funclib.iolib as iolib
from opencvlib.imgpipes import vgg as _vgg
from opencvlib.imgpipes.generators import VGGROI
from geometry import Point
from plotlib import qplot
from funclib.arraylib import distances, angles_between
from funclib.arraylib import min_indices
from funclib.baselib import list_flatten
from funclib.iolib import writecsv
from funclib.iolib import notepadpp_open_file
from dliblib import VALID_LABELS
from funclib.iolib import wait_key

LABELS = [str(x+1) for x in range(20)]

Scaler = MaxAbsScaler()

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
    x = sum([1 for x in _vgg.imagesGenerator(skip_imghdr_check=True, file_attr_match={'is_train':'1'})])
    PP = _PP(x, init_msg='Loading training data and creating model...')
    PP.max = x

    train_distances = np.zeros((x, 19, 19))
    train_angles = np.zeros((x, 19, 19))
    train_pts = np.empty((x, 19, 2)) #store points
    train_pts[:] = np.nan

    j = 0
    invalid_labels = []
    for vggImg in _vgg.imagesGenerator(skip_imghdr_check=True, file_attr_match={'is_train':'1'}):
        PP.increment()
        assert isinstance(vggImg, _vgg.Image)
        Pts = [[None, None]] * 19 #store all the points
        for vggReg in vggImg.roi_generator(shape_type='point'):
            assert isinstance(vggReg, _vgg.Region)
            lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('pts', '') == '' else int(vggReg.region_attr['pts'])

            if not lbl in range(1, 21):
                invalid_labels.append('Image %s has invalid pts label %s.' % (vggImg.filename, lbl))
                continue

            Pts[lbl-1] = [vggReg.x, vggReg.y]

        train_pts[j, ...] = np.array(Pts) #this contains all the points
        train_distances[j, :, :] = distances(Pts, Pts).squeeze()
        train_angles[j, ...] = angles_between(Pts, Pts).squeeze()
        j += 1

    if invalid_labels:
        print('\nInvalid Labels Found:')
        print('\n'.join(invalid_labels))
        _ = wait_key('Press any key to continue')
        return

    mean_distances = np.nanmean(train_distances, axis=0) #19x19 array of mean distances between points
    mean_distances_std = Scaler.fit_transform(mean_distances)
    mean_angles = np.nanmean(train_angles, axis=0)
    mean_points = np.nanmean(train_pts, axis=0)



    #region Load all data
    x = sum([1 for x in _vgg.imagesGenerator(skip_imghdr_check=True)])
    PP = _PP(x, init_msg="\nChecking all images ...")
    img_stats = []
    pt_cnt = 0
    for vggImg in _vgg.imagesGenerator(skip_imghdr_check=True):
        PP.increment()
        assert isinstance(vggImg, _vgg.Image)
        Pts = [[None, None] for x in range(19)] #store all the points
        got_points = False
        for vggReg in vggImg.roi_generator(shape_type='point'):
            got_points = True
            assert isinstance(vggReg, _vgg.Region)
            lbl = int(vggReg.region_json_key) + 1 if vggReg.region_attr.get('pts', '') == '' else int(vggReg.region_attr['pts'])
            Pts[lbl-1] = [vggReg.x, vggReg.y]
            pt_cnt += 1

        if got_points:
            distances_ = abs((distances(Pts, Pts).squeeze() - mean_distances))/np.nanmean(mean_distances) #each row has the distances for that point, so row 0 has the distances of every point from point 1.
            angles_ = abs(angles_between(Pts, Pts).squeeze() - mean_angles)/np.nanmean(mean_angles)
            err = (distances_ + angles_)/2
            err = np.apply_along_axis(np.nanmean, 0, err)
            err = ['' if np.isnan(x) else float(x) for x in err]
            lst = [vggImg.filename]
            lst.extend(err)
            img_stats.append(lst)
        else:
            lst = [vggImg.filename]
            lst.extend(['' for x in range(19)])
            img_stats.append(lst)

    print('\nTotal points was %s' % pt_cnt)

    if img_stats:
        writecsv('C:/temp/validate_probs_633bad.txt', img_stats, inner_as_rows=False)
        notepadpp_open_file('C:/temp/validate_probs_633bad.txt')


if __name__ == "__main__":
    main()
