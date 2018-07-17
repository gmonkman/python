# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''Calculate RMS for distorted and undistorted
chess board images taken with the NextBase 512G
in movie mode

Uses a vgg file with the region annotations of
fids and mm. i.e. the cols in vgg region attrs
are called fids and mm.

The vgg files must be called distorted.json and undistorted.json

Results saved to a csv file rms.csv.

Example:
oneoff_rms.py "C:/temp/fshpics"
'''
#This was used to generate RMS comparison data between distorted
#and undistorted chessboard images in folder
#C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/calibration/rms
#for us in the fiducial_error_minimisation paper

import argparse
import os.path as path
from shutil import copyfile

import numpy as np
import statsmodels.api as sm

import opencvlib.imgpipes.vgg as vgg
from funclib.iolib import get_file_parts2
from funclib.iolib import get_file_parts
import funclib.iolib as iolib
from funclib.iolib import PrintProgress
from funclib import arraylib
from opencvlib.view import draw_points
from opencvlib.view import show


VGGFILE_DISTORTED = 'distorted.json'
VGGFILE_UNDISTORTED = 'undistorted.json'

CSVOUT = 'rms.csv'

ROWS_UND = 13; COLS_UND = 34
ROWS_DIS = 16; COLS_DIS = 36

def main():
    '''main'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('folder', help='Folder containing the images and vgg files distorted.json and undistorted.json')
    args = cmdline.parse_args()

    vgg.SILENT = True
    folder = path.normpath(args.folder)
    assert iolib.folder_exists(folder), 'Folder %s not found' % folder
    vgg_file_distorted = path.normpath(path.join(folder, VGGFILE_DISTORTED))
    print('Opened vgg file %s' % vgg_file_distorted)

    vgg_file_undistorted = path.normpath(path.join(folder, VGGFILE_DISTORTED))
    print('Opened vgg file %s' % vgg_file_undistorted)

    out_file = path.normpath(path.join(folder, CSVOUT))

    #should be only one image
    D = np.zeros(COLS_DIS*ROWS_DIS*2).reshape(ROWS_DIS, COLS_DIS, 2)
    vgg.load_json(vgg_file_distorted)
    PP = PrintProgress(sum([1 for x in vgg.imagesGenerator()]), init_msg='\nProcessing distorted points...')
    for Img in vgg.imagesGenerator():
        PP.increment()
        assert isinstance(Img, vgg.Image)
        for vggReg in Img.roi_generator(shape_type='point'):
            assert isinstance(vggReg, vgg.Region)
            ind = int(vggReg.region_json_key)
            col = ind % COLS_DIS
            row = int(ind / COLS_DIS)
            D[row, col, 0] = vggReg.x #x coordinates
            D[row, col, 1] = vggReg.y #y coordinates

    #get each row of points and run a regression to find the y residuals
    #this is right, a row varies in the y axis
    x_resids = []
    for row in D[:,:,0].T:
        row = row - np.average(row) #standardise
        x = np.array([0]*len(row))
        model = sm.OLS(row, x).fit()
        x_resids.append(model.resid) #build list of the x residuals, these are deviations from x=0
    x_resids  = np.array(y_resids)

    #get each column of points and run a regression to find the x residuals
    y_resids = []
    for row in D[:, :, 1].T:
        row = row - np.average(row) #standardise
        x = np.array([0]*len(row))
        model = sm.OLS(y, x).fit()
        x_resids.append(model.resid) #build list of the x residuals, these are deviations from x=0
    y_resids = np.array(y_resids)

    #this calculates euclidean distance of the 2d residual (x,y) and (0,0)
    #then calculates the RMS
    distorted_rms = np.sqrt(np.mean(np.square(np.sqrt(np.square(y_resids) + np.square(x_resids)))))




    #Now the undistorted points
    undistorted_pts = []
    vgg.load_json(vgg_file_distorted)
    PP = PrintProgress(sum([1 for x in vgg.imagesGenerator()]), init_msg='\nProcessing distorted points...')
    n_und = 0
    for Img in vgg.imagesGenerator():
        PP.increment()
        assert isinstance(Img, vgg.Image)
        for vggReg in Img.roi_generator(shape_type='point'):
            assert isinstance(vggReg, vgg.Region)
            undistorted_pts.append([vggReg.x, vggReg.y])
    U = np.array(undistorted_pts)

    #get each row of points and run a regression to find the y residuals
    y_resids = []
    for y in U:
        x = np.array([0]*len(y))
        model = sm.OLS(y, x).fit()
        y_resids.append(model.resid) #build list of the x residuals, these are deviations from x=0
    y_resids  = np.array(y_resids)

    #get each column of points and run a regression to find the x residuals
    x_resids = []
    for y in U.T:
        x = np.array([0]*len(y))
        model = sm.OLS(y, x).fit()
        x_resids.append(model.resid) #build list of the x residuals, these are deviations from x=0
    x_resids = np.array(x_resids)

    #this calculates euclidean distance of the 2d residual (x,y) and (0,0)
    #then calculates the RMS
    undistorted_rms = np.sqrt(np.mean(np.square(np.sqrt(np.square(y_resids) + np.square(x_resids)))))

    print('undistorted rms: %0.3f; distorted rms: %0.3f' % (undistorted_rms, distorted_rms))



if __name__ == "__main__":
    main()
    #sys.exit(int(main() or 0))
