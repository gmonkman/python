# pylint: disable=C0302, line-too-long, too-few-public-methods, too-many-branches, too-many-statements, unused-import, no-member, ungrouped-imports, too-many-arguments, wrong-import-order, relative-import, too-many-instance-attributes, too-many-locals, unused-variable
'''
camera calibration for distorted images with chess board samples
reads distorted images, calculates the calibration and write undistorted images
usage:
    calibrate.py [--debug <output path>] [--square_size] [<image mask>]
default values:
    --debug:    ./output/
    --square_size: 1.0
    <image mask> defaults to ../data/left*.jpg
'''


#region imports
#region base imports
from __future__ import print_function
from glob import glob
import argparse
import itertools
import os
import sys
#end region

#region 3rd party imports
import cv2
import fuckit
import numpy as np
import scipy
import xlwings
#endregion

#region my imports
import opencvlib.digikamlib as digikamlib
import funclib.arraylib as arraylib
import funclib.iolib as iolib
import funclib.inifilelib as inifilelib
import funclib.stringslib as stringslib
from funclib.stringslib import add_right
#import funclib.statslib as statslib #includes rpy which takes ages to load
from common import splitfn
from enum import Enum
from funclib.baselib import switch
#endregion
#endregion

_INIFILE = './lenscorrection.py.ini'
_IMAGE_EXTENSIONS = ('*.jpg', '*.gif', '*.bmp', '*.png', '*.tif', '*.tiff', '*.tga')

#region Class Declarations
class CalibrationGrid(object):
    '''representation of checker board x and y vertices'''
    def __init__(self, x_vertices=9, y_vertices=6):
        '''init'''
        self._x = x_vertices
        self._y = y_vertices

    @property
    def x_vertices(self):
        '''get'''
        return self._x
    @x_vertices.setter
    def x_vertices(self, x):
        '''(int) set numer of x vertices'''
        self._x = x

    @property
    def y_vertices(self):
        '''getter'''
        return self._y
    @y_vertices.setter
    def y_vertices(self, y):
        '''(int) set number of y vertices'''
        self._y = y

class CalibrationParam(object):
    '''single calibation parameter'''
    def __init__(self, filename, value):
        self.filename = filename
        self.value = value

class CalibrationParams(object):
    '''Handles loading and saving of the camera calibration parameters'''
    def __init__(self, path, rms=None, camera_matrix=None, distortion_coefficients=None,
                 rotational_vectors=None, translation_vectors=None):
        '''the arguments are the vector values, not a calibration_param object.
        Path is the directory to which parameters are pickled/unpickled.
        '''
        self._path = os.path.normpath(path)
        self._rms = CalibrationParam('rms.pkl', rms)
        self._camera_matrix = CalibrationParam('camera_matrix.pkl', camera_matrix)
        self._distortion_coefficients = CalibrationParam('distortion_coefficients.pkl', distortion_coefficients)
        self._rotational_vectors = CalibrationParam('rotational_vectors.pkl', rotational_vectors)
        self._translation_vectors = CalibrationParam('translation_vectors.pkl', translation_vectors)
        self.last_save = None
        self.last_load = None
        assert isinstance(self._rms, CalibrationParam)
        assert isinstance(self._camera_matrix, CalibrationParam)
        assert isinstance(self._distortion_coefficients, CalibrationParam)
        assert isinstance(self._rotational_vectors, CalibrationParam)
        assert isinstance(self._translation_vectors, CalibrationParam)

    #region properties
    @property
    def rms(self):
        '''rms getter'''
        return self._rms.value
    @rms.setter
    def rms(self, rms):
        '''rms setter'''
        self._rms.value = rms

    @property
    def path(self):
        '''path getter'''
        return self._path
    @path.setter
    def path(self, path):
        '''path setter'''
        self._path = path

    @property
    def camera_matrix(self):
        '''camera_matrix getter'''
        return self._camera_matrix.value
    @camera_matrix.setter
    def camera_matrix(self, camera_matrix):
        '''camera_matrix setter'''
        self._camera_matrix.value = camera_matrix

    @property
    def distortion_coefficients(self):
        '''distortion_coefficients getter'''
        return self._distortion_coefficients.value
    @distortion_coefficients.setter
    def distortion_coefficients(self, distortion_coefficients):
        '''distortion_coefficients setter'''
        self._distortion_coefficients.value = distortion_coefficients

    @property
    def rotational_vectors(self):
        '''rotational_vectors getter'''
        return self._rotational_vectors.value
    @rotational_vectors.setter
    def rotational_vectors(self, rotational_vectors):
        '''rotational_vectors setter'''
        self._rotational_vectors.value = rotational_vectors

    @property
    def translation_vectors(self):
        '''translational_vectors getter'''
        return self._translation_vectors.value
    @translation_vectors.setter
    def translation_vectors(self, translational_vectors):
        '''translational_vectors setter'''
        self._translational_vectors.value = translational_vectors
    #endregion

    #region Static methods
    @staticmethod
    def _load_param(folder, param):
        '''(str, [class]calibration_param)
        Tries to load the pickled calibration parameter from
        the file system
        '''
        assert isinstance(param, CalibrationParam)
        folder = add_right(folder) + param.filename
        param.value = iolib.unpickle(folder)

    @staticmethod
    def _save_param(folder, param):
        '''(str, [cls]calibration_param) -> void
        pickle the parameter value to the file system
        '''
        iolib.pickleit(os.path.join(folder, param.filename), param.value)
    #endregion

    def load(self):
        '''-> bool
        Trys to load the pickled parameters from
        the file system.
        Parameter values will be None if they arn't loaded

        Returns True if all params were loaded, otherwise False
        '''
        success = True
        try:
            CalibrationParams._load_param(self.path, self._camera_matrix)
            CalibrationParams._load_param(self.path, self._distortion_coefficients)
            CalibrationParams._load_param(self.path, self._rms)
            CalibrationParams._load_param(self.path, self._rotational_vectors)
            CalibrationParams._load_param(self.path, self._translation_vectors)
            if self._camera_matrix.value is None: success = False
            if self._distortion_coefficients.value is None: success = False
            if self._rms.value is None: success = False
            if self._rotational_vectors.value is None: success = False
            if self._translation_vectors.value is None: success = False
        except Exception:
            success = False
        self.last_load = success
        return success

    def save(self):
        '''-> bool
        Saves (pickles) parameter values to class path

        Returns True if no errors occured
        '''
        success = True
        try:
            CalibrationParams._save_param(self.path, self._camera_matrix)
            CalibrationParams._save_param(self.path, self._distortion_coefficients)
            CalibrationParams._save_param(self.path, self._rms)
            CalibrationParams._save_param(self.path, self._rotational_vectors)
            CalibrationParams._save_param(self.path, self._translation_vectors)
        except Exception:
            success = False
        self.last_save = success
        self.last_load = success #save is an implicit load, so flag we have good values
        return success

class Camera(object):
    '''Class container for all things related to a particular camera'''
    def __init__(self, calibration_path, model='', image_file_mask='', grid=None, square_size=1):
        '''(str, str, str, calibration_grid[class], int)
        Also sets up the debug path (creating one if it doesnt exist)
        and image path (checking if it the image path exists)
        '''
        self._model = model
        self._calibration_path = os.path.normpath(calibration_path) #root
        self._calibration_output_path = os.path.normpath(calibration_path)
        self._grid = grid
        self._image_file_mask = image_file_mask
        self._square_size = square_size
        self._debugdir = ''
        self.digikam_camera_tag = ''
        self.digikam_measured_tag = ''
        self.digikam_connection_string = ''
        self._calibration_params = CalibrationParams(self._calibration_path)

        if not os.path.exists(self.calibration_path):
            raise IOError('Calibration path %s does not exist.' % self.calibration_path)

        self._calibration_path_debug = os.path.normpath(os.path.join(self.calibration_path, 'debug'))
        iolib.create_folder(self.calibration_path_debug)

        self._calibration_path_images = os.path.normpath(os.path.join(self.calibration_path, 'images'))
        if not os.path.exists(self.calibration_path_images):
            raise IOError('Calibration image path %s does not exist.' % self._calibration_path_images)

    #region properties
    @property
    def calibration_path_debug(self):
        '''hard coded to ./debug'''
        return self._calibration_path_debug

    @property
    def calibration_path_images(self):
        '''hard coded to ./images'''
        return self._calibration_path_images

    @property
    def calibration_output_path(self):
        '''where we pickle our calibration outputs'''
        return self._calibration_output_path

    @property
    def model(self):
        '''the model name, used as inifile section header'''
        return self._model

    @property
    def calibration_path(self):
        '''getter. (str) root of the camera calibration path'''
        return self._calibration_path
    @calibration_path.setter
    def calibration_path(self, calibration_path):
        '''(str) root of the camera calibration path'''
        self._calibration_path = calibration_path

    @property
    def image_file_mask(self):
        '''image_pattern getter'''
        return self._image_file_mask
    @image_file_mask.setter
    def image_file_mask(self, mask):
        '''image_pattern setter'''
        self._image_file_mask = mask

    @property
    def grid(self):
        '''calibration_grid class - getter'''
        return self._grid
    @grid.setter
    def grid(self, grid):
        '''grid setter'''
        assert isinstance(grid, CalibrationGrid)
        self._grid = grid

    @property
    def square_size(self):
        '''square_size getter'''
        return self._square_size
    @square_size.setter
    def square_size(self, square_size):
        '''square_size setter'''
        self._square_size = square_size

    @property
    def calibration_params(self):
        '''calibration_params getter'''
        return self._calibration_params
    #endregion

    def get_full_path(self):
        '''-> str
        returns the full path concatenated with the mask so we can
        glob all the images in the cameras calibration path
        '''
        return os.path.normpath(os.path.join(self._calibration_path_images, self._image_file_mask))

    def get_debug_dir(self):
        '''-> str
        Returns the path for debug image output
        Creates it if it doesnt exist
        '''
        s = os.path.normpath(os.path.join(self._calibration_path, 'debug'))
        iolib.create_folder(s)
        return s

    def load_params(self):
        '''trys to load calibration params previously saved to the file system'''
        self._calibration_params = CalibrationParams(self.calibration_output_path)
        self._calibration_params.load()

    def save_params(self):
        '''save all the calibration objects'''
        self._calibration_params.save()
#endregion

def get_camera(model):
    '''(str)-> [class] camera
    Reads camera details from the lenscorrection.py.ini,
    returning the camera class.
    model is generally parsed from a command line argument when this routine is executed.
    '''
    if not inifilelib.iniexists(_INIFILE):
        raise IOError('Ini file %s not found.' % _INIFILE)
    ini = inifilelib.configfile(_INIFILE)

    calpath = ini.tryread(model, 'CALIBRATION_PATH', force_create=False)
    if not os.path.exists(calpath):
        raise IOError('Calibration path %s not found.' % (calpath))

    cam = Camera(model=model, calibration_path=calpath)

    cam.grid = CalibrationGrid(int(ini.tryread(model, 'x_vertices', force_create=False)), int(ini.tryread(model, 'y_vertices', force_create=False)))

    cam.image_file_mask = ini.tryread(model, 'IMAGE_PATTERN', force_create=False)
    if cam.image_file_mask == '':
        raise ValueError('Image pattern (option IMAGE_PATTERN) could not be read from lenscorrection.py.ini')

    cam.square_size = int(ini.tryread(model, 'square_size', force_create=False))
    cam.digikam_camera_tag = ini.tryread(model, 'DIGIKAM_CAMERA_TAG', force_create=False)
    cam.digikam_measured_tag = ini.tryread(model, 'DIGIKAM_MEASURED_TAG', force_create=False)
    cam.digikam_connection_string = ini.tryread(model, 'DIGIKAM_CONNECTION_STRING', force_create=False)

    return cam

def calibrate(cam, debug=False):
    '''(camera[class])
    Pass in a camera class object, initialised from the ini file
    by calling get_camera
    '''
    assert isinstance(cam, Camera)

    pattern_size = (cam.grid.x_vertices, cam.grid.y_vertices)
    pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
    pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    pattern_points *= cam.square_size

    obj_points = []
    img_points = []
    h, w = 0, 0
    img_names_undistort = []
    i = 1

    calpath = iolib.get_file_name(path=cam.calibration_path)
    print('Logging to %s' % calpath)
    iolib.create_file(calpath)

    foundcnt = 0
    img_names = glob(cam.get_full_path())
    for fn in img_names:
        img = cv2.imread(os.path.normpath(fn), 0)
        if img is None:
            iolib.write_to_eof(calpath, 'Failed to load image %s\n' % (fn))
        else:
            h, w = img.shape[:2]
            found, corners = cv2.findChessboardCorners(img, pattern_size)

            if found:
                term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
                cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), term)
                img_points.append(corners.reshape(-1, 2))
                obj_points.append(pattern_points)
                foundcnt += 1
            else:
                iolib.write_to_eof(calpath, 'Chessboard not found in %s\n' % (fn))

            if debug:
                vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                cv2.drawChessboardCorners(vis, pattern_size, corners, found)
                path, name, ext = splitfn(fn)
                outfile = os.path.normpath(os.path.join(cam.calibration_path_debug, name + '_chess.png'))
                cv2.imwrite(outfile, vis)

        iolib.print_progress(i, len(img_names), prefix='%i of %i [found:%i]' % (i, len(img_names), foundcnt), bar_length=30)
        i += 1

    # calculate camera distortion
    rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, (w, h), None, None)
    cam.calibration_params.rms = rms
    cam.calibration_params.camera_matrix = camera_matrix
    cam.calibration_params.distortion_coefficients = dist_coefs
    cam.calibration_params.rotational_vectors = rvecs
    cam.calibration_params.translational_vectors = tvecs
    cam.save_params()

    iolib.write_to_eof(calpath, '\nCamera correction parameters pickled to %s' % (cam.calibration_output_path))
    iolib.write_to_eof(calpath, '\nWas the pickling a success?: %s' % (str(cam.calibration_params.last_save)))
    iolib.write_to_eof(calpath, '\nRMS: %d' % rms)

    cv2.destroyAllWindows()

def _undistort(cam, img, crop=True):
    '''[c]Camera, ndarray (image), bool -> ndarray (image) | None
    Undistorts an image based on the lens profile loaded into the Camera class cam.

    Returns None if an exception occurs
    '''
    assert isinstance(cam, Camera)
    assert isinstance(img, np.ndarray)
    try:
        h, w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(cam.calibration_params.camera_matrix, cam.calibration_params.distortion_coefficients, (w, h), 1, (w, h))
        dst = cv2.undistort(img, cam.calibration_params.camera_matrix, cam.calibration_params.distortion_coefficients, None, newcameramtx)
        if crop:
            x, y, w, h = roi
            dst = dst[y:y+h, x:x+w]
    except Exception:
        dst = None
    finally:
        return dst

def undistort_using_paths(cam, imgpaths_or_imagelist, outpath, label='_UND', crop=True):
    '''(Camera, str|iterable, str, str, bool) -> void
    Bulk undistort, reading in the camera profile according to model name as matched in lenscorrection.py.ini
    Multiple paths can be provided

    imgpaths_or_imagelist can be an iterable of paths or a list. If appears to be paths,
    then glob will be cobined with known image extensions to list all files in paths
    which appear to be images. If a single directory string is passed in, this
    will also be valid and globbed.

    Converted images are saved to outpath, with label appended to the original file name.
    '''

    useglob = True
    if isinstance(imgpaths_or_imagelist, str):
        imgpaths_or_imagelist = [imgpaths_or_imagelist]

    #look to see if the list is mostly (50%) valid files rather than directories
    validcnt = 0.0
    for myfiles in imgpaths_or_imagelist:
        validcnt += os.path.isfile(os.path.normpath(myfiles))

    if validcnt/len(myfiles) > 0.5: useglob = False

    if useglob:
        globlist = iolib.file_list_generator(imgpaths_or_imagelist, _IMAGE_EXTENSIONS)
    else:
        newlist = imgpaths_or_imagelist

    if useglob:
        newlist = []
        for wildcards in globlist:
            for fil in glob(wildcards):
                newlist.append(fil)

    cnt = 0
    success = 0
    logfilename = iolib.get_file_name(outpath)
    for fil in newlist:
        try:
            path, name, ext = splitfn(fil)
            outfile = os.path.join(outpath, name + label + '.png')
            img = _undistort(cam, cv2.imread(fil), crop)
            if img is None:
                iolib.write_to_eof(logfilename, 'File %s failed in _undistort.' % (fil, Exception.message))
            else:
                cv2.imwrite(outfile, img)
                success += 1
                with fuckit:
                    iolib.write_to_eof(logfilename, 'Success:%s' % (fil))
        except Exception:
            iolib.write_to_eof(logfilename, 'Failed:%s, Exception:%s' % (fil, Exception.message))
        finally:
            with fuckit:
                iolib.print_progress(cnt, len(fil), '%i of %i [Successes: %i]' % (cnt, len(fil), success), bar_length=30)
                cnt += 1


#region main
def main():
    '''(bool)->void
    Main is only called if the script is directly executed and can
    be used to do stuff in here like testing.

    Setting getcmdlineargs to true will set up cmdline arguments,
    which can be loaded into global variables as required (need to define)
    '''

    cmdline = argparse.ArgumentParser(description='Description if script is executed with -h option')
    cmdline.add_argument('-m', '--mode', action='store', help='The mode, values are:\nUNDISTORT - undistorts images in path\nCALIBRATE - create lens calibration values', required=True)
    cmdline.add_argument('-p', '--path', action='store', help='Path to images to undistort. Pass DIGIKAM to use digikam database with options provided in the ini file. This is required in UNDISTORT mode.', required=False)
    cmdline.add_argument('-o', '--outpath', action='store', help='Path to store undistorted images. Must be provided in undistort mode', required=False)
    cmdline.add_argument('-c', '--camera', action='store', help='Camera model key in the ini file which defines the camera calibration parameters for the camera model specified', required=True)
    cmdline.add_argument('-d', '--debug', action='store_true', help='Run in DEBUG mode', default=False, required=False)
    cmdargs = cmdline.parse_args()
    if cmdargs.mode == 'undistort' and (cmdargs.path == '' or cmdargs.path is None):
        print('\nMode was undistort but no path argument was specified.')
        iolib.exit()

    cam = get_camera(cmdargs.camera)
    if cmdargs.mode == 'undistort':
        if cmdargs.path != 'digikam' and not os.path.exists(os.path.normpath(cmdargs.path)):
            print('Path ' + os.path.normpath(cmdargs.path) + ' does not exists')
        elif cmdargs.outpath == '':
            print('Output path not specified')
        else:
            iolib.create_folder(os.path.normpath(cmdargs.outpath))
            if cmdargs.path == 'digikam':


                undistort_using_paths(cmdargs.camera, os.path.normpath(cmdargs.path), os.path.normpath(cmdargs.outpath))
            else:
                undistort_using_paths(cam, os.path.normpath(cmdargs.path), os.path.normpath(cmdargs.outpath))
            print('Undistort completed. Undistorted images saved to %s' % (os.path.normpath(cmdargs.outpath)))
    elif cmdargs.mode == 'calibrate':
        calibrate(cam)
        if cam.calibration_params.last_load:
            print('Camera calibration was successful.')
        else:
            print('Camera calibration was attempted but appears to have failed.')
    else:
        print('\nInvalid or missing mode argument. Valid values are undistort or calibrate')
        iolib.exit()



if __name__ == '__main__':
    main()
#endregion
