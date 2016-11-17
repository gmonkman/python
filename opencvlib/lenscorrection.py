# pylint: disable=C0302, no-member, not-context-manager
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
import cPickle
import os
#end region

#region 3rd party imports
import cv2
import fuckit
import numpy as np
#endregion

#region my imports
import opencvlib.digikamlib as digikamlib
import funclib.iolib as iolib
import funclib.inifilelib as inifilelib
import funclib.pyqtlib as msgbox
import opencvlib.common as common
import opencvlib.lenscorrectiondb as lenscorrectiondb
from opencvlib.common import resolution
from funclib.baselib import list_append_unique

#from opencvlib.common import is_image
#endregion
#endregion


_INIFILE = './lenscorrection.py.ini'
_DIGIKAM_CONNECTION_STRING = ''
_CALIBRATION_CONNECTION_STRING = ''
_PrintProgress = None

#region Class Declarations
class PrintProgress(object):
    '''DOS progressbar'''
    def __init__(self, maximum, bar_length=30):
        self.max = maximum
        self.bar_length = bar_length
        self.iteration = 0

    def increment(self):
        '''tick the progress bar'''
        iolib.print_progress(self.iteration, self.max, prefix='%i of %i' % (self.iteration, self.max), bar_length=self.bar_length)
        self.iteration += 1


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


class CameraIni(object):
    '''Class container for the ini file configuration for a particular camera model'''
    def __init__(self, calibration_path, model='', image_file_mask='', grid=None, square_size=1):
        '''(str, str, str, calibration_grid[class], int)
        Also sets up the debug path (creating one if it doesnt exist)
        and image path (checking if it the image path exists)
        '''
        self._model = model
        self._calibration_path = os.path.normpath(calibration_path) #root
        self._grid = grid
        self._image_file_mask = image_file_mask
        self._square_size = square_size
        self._debugdir = ''
        self.digikam_camera_tag = '' #currently set in def main
        self.digikam_measured_tag = ''

        self._calibration_path_debug = os.path.normpath(os.path.join(self.calibration_path, 'debug'))
        self._calibration_path_images = os.path.normpath(os.path.join(self.calibration_path, 'images'))
        iolib.create_folder(self.calibration_path_debug)

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
    #endregion



    def get_full_calibration_image_path(self):
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


class Calibration(object):
    '''container for a camera calibration at a specific resolution'''

    def __init__(self, camera_model, wildcarded_images_path, height, width, pattern_size=(9, 6), square_size=1):
        '''(str, int, int, tuple)
        (camera model name, image height, image width, tuple:(x vertices, y vertices), square_size)
        of the calibration images.
        '''
        self.height = height
        self.width = width
        self.camera_model = camera_model
        self.wildcarded_images_path = wildcarded_images_path
        self.pattern_size = pattern_size
        self.square_size = square_size
        self.img_used_count = 0
        self.img_total_count = 0
        self.messages = []

    @property
    def _pattern_points(self):
        '''pattern_points getter'''
        pattern_points = np.zeros((np.prod(self.pattern_size), 3), np.float32)
        pattern_points[:, :2] = np.indices(self.pattern_size).T.reshape(-1, 2)
        pattern_points *= self.square_size
        return pattern_points

    def calibrate(self):
        '''main calibration entry point'''
        obj_points = []
        img_points = []
        fcnt = 0; cnt = 0
      #  for fn in iolib.file_list_glob_generator(self.path_to_calibration_images):
        for fn in iolib.file_list_glob_generator(self.wildcarded_images_path):
            if common.is_image(fn):
                img = cv2.imread(os.path.normpath(fn), 0)
                w, h = common.resolution(img)
                if w == self.width and h == self.height:
                    cnt += 1
                    found, corners = cv2.findChessboardCorners(img, self.pattern_size)
                    if found:
                        fcnt += 1
                        term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
                        cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), term)
                        img_points.append(corners.reshape(-1, 2))
                        obj_points.append(self._pattern_points)
                    else:
                        self.messages.append('Chessboard vertices not found in %s' % (fn))

                    _PrintProgress.increment()

        self.img_total_count = cnt; self.img_used_count = fcnt
    # calculate camera distortion
        rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, (self.width, self.height), None, None)

        cm = cPickle.dumps(camera_matrix, cPickle.HIGHEST_PROTOCOL)
        dc = cPickle.dumps(dist_coefs, cPickle.HIGHEST_PROTOCOL)
        rv = cPickle.dumps(rvecs, cPickle.HIGHEST_PROTOCOL)
        tv = cPickle.dumps(tvecs, cPickle.HIGHEST_PROTOCOL)

        with lenscorrectiondb.Conn(cnstr=_CALIBRATION_CONNECTION_STRING) as conn:
            db = lenscorrectiondb.CalibrationCRUD(conn)
            modelid = db.crud_camera_upsert(self.camera_model)
            db.crud_calibration_upsert(modelid, self.width, self.height, cm, dc, rms, rv, tv)
            conn.commit()

    @property
    def result_str(self):
        '''result_str getter'''
        return 'Resolution %ix%i: %i of %i were useable' % (self.width, self.height, self.img_used_count, self.img_total_count)
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

    cam = CameraIni(model=model, calibration_path=calpath)

    cam.grid = CalibrationGrid(int(ini.tryread(model, 'x_vertices', force_create=False)), int(ini.tryread(model, 'y_vertices', force_create=False)))

    cam.image_file_mask = ini.tryread(model, 'IMAGE_PATTERN', force_create=False)
    if cam.image_file_mask == '':
        raise ValueError('Image pattern (option IMAGE_PATTERN) could not be read from lenscorrection.py.ini')

    cam.square_size = int(ini.tryread(model, 'square_size', force_create=False))
    cam.digikam_camera_tag = ini.tryread(model, 'DIGIKAM_CAMERA_TAG', force_create=False)
    cam.digikam_measured_tag = ini.tryread(model, 'DIGIKAM_MEASURED_TAG', force_create=False)
    return cam

def _ini_set_database_strings():
    '''load db config strings from the inifile'''
    if not inifilelib.iniexists(_INIFILE):
        raise IOError('Ini file %s not found.' % _INIFILE)
    ini = inifilelib.configfile(_INIFILE)
    global _DIGIKAM_CONNECTION_STRING
    _DIGIKAM_CONNECTION_STRING = ini.tryread('DATABASE', 'DIGIKAM_CONNECTION_STRING', force_create=False)
    global _CALIBRATION_CONNECTION_STRING
    _CALIBRATION_CONNECTION_STRING = ini.tryread('DATABASE', 'CALIBRATION_CONNECTION_STRING', force_create=False)

def calibrate(cam):
    '''(camera[class])
    Pass in a camera class object, initialised from the ini file
    by calling get_camera
    '''
    assert isinstance(cam, CameraIni)

    calpath = iolib.get_file_name(path=cam.calibration_path)
    dims = common.get_image_resolutions(cam.get_full_calibration_image_path())

    img_path = cam.get_full_calibration_image_path()

    #set up a list of classes for the different resolutions of calibration images
    calibrations = [Calibration(cam.model, img_path, h, w, (cam.grid.x_vertices, cam.grid.y_vertices), cam.square_size) for w, h in dims]

    global _PrintProgress
    _PrintProgress = PrintProgress(len(glob(img_path)))
    _PrintProgress.iteration = 1

    for Cal in calibrations:
        Cal.calibrate()

    for Cal in calibrations:
        print(Cal.result_str)

def _undistort(cam, img, mats, crop=True):
    '''[c]Camera, ndarray (image), dic, bool -> ndarray (image) | None
    Undistorts an image based on the lens profile loaded into the Camera class cam.
    dic is a dictionary containing the undistortion matrices
    {'cmat':cmat, 'dcoef':dcoef, 'rvect':rvect, 'tvect':tvect}

    Returns None if an exception occurs
    '''
    assert isinstance(cam, CameraIni)
    assert isinstance(img, np.ndarray)
    try:
        h, w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mats['cmat'], mats['dcoef'], (w, h), 1, (w, h))
        dst = cv2.undistort(img, mats['cmat'], mats['dcoef'], None, newcameramtx)
        if crop:
            x, y, w, h = roi
            dst = dst[y:y+h, x:x+w]
    except Exception:
        print(Exception.message)
        dst = None
    finally:
        return dst

def undistort(cam, imgpaths_or_imagelist, outpath, label='_UND', crop=True, use_nearest_aspect=True):
    '''(Camera, str|iterable, str, str, bool) -> void
    Bulk undistort, reading in the camera profile according to model name as matched in lenscorrection.py.ini
    Multiple paths can be provided

    imgpaths_or_imagelist can be an iterable of paths or a list. If appears to be paths,
    then glob will be cobined with known image extensions to list all files in paths
    which appear to be images. If a single directory string is passed in, this
    will also be valid and globbed.

    Converted images are saved to outpath, with label appended to the original file name.
    '''

    blobs = {}
    useglob = True
    bad_res = []
    subst_res = []

    if isinstance(imgpaths_or_imagelist, str):
        imgpaths_or_imagelist = [imgpaths_or_imagelist]
    else:
        #look to see if the list is mostly (50%) valid files rather than directories
        validcnt = 0.0
        for myfiles in imgpaths_or_imagelist:
            validcnt += os.path.isfile(os.path.normpath(myfiles))
        if validcnt/len(imgpaths_or_imagelist) > 0.5: useglob = False

    if useglob:
        globlist = iolib.file_list_generator(imgpaths_or_imagelist, common.IMAGE_EXTENSIONS_AS_WILDCARDS)
        newlist = []
        for wildcards in globlist:
            for fil in glob(wildcards):
                newlist.append(fil)
    else:
        newlist = imgpaths_or_imagelist

    cnt = 1; success = 0
    logfilename = iolib.get_file_name(outpath)

    with lenscorrectiondb.Conn(cnstr=_CALIBRATION_CONNECTION_STRING) as conn:
        db = lenscorrectiondb.CalibrationCRUD(conn)
        last_width = 0; last_height = 0
        for fil in newlist:
            try:
                resize_suffix = ''
                path, name, ext = common.splitfn(fil) # used later to rebuild output file name
                orig_img = cv2.imread(fil)
                width, height = resolution(orig_img)
                if (last_width != width and last_height != height) and height > 0 and width > 0:
                    blobs = db.crud_read_calibration_blobs(cam.model, height, width)
                    if use_nearest_aspect and blobs is None: #use next best if no blobs found
                        blobs = db.blobs_get_nearest_aspect_match(cam.model, height, width)
                        if not blobs is None:
                            w, h = blobs('matched_resolution_w_by_h')
                            list_append_unique(subst_res, 'No exact calibration for resolution %ix%i, resized and used nearest match %ix%i' % (width, height, w, h))
                            orig_img = common.resize(orig_img, w, h)
                            resize_suffix = '_RZ%ix%i' % (w, h)
                if blobs is None:
                    iolib.write_to_eof(logfilename, 'No calibration data for image %s, resolution [%sx%s]' % (fil, width, height))
                    list_append_unique(bad_res, '%ix%i' % (width, height))
                else:
                    #{'cmat':cmat, 'dcoef':dcoef, 'rvect':rvect, 'tvect':tvect}
                    img = _undistort(cam, orig_img, blobs, crop)
                    if img is None:
                        iolib.write_to_eof(logfilename, 'File %s failed in _undistort.\n' % (fil))
                    else:
                        outfile = os.path.join(outpath, name + label + resize_suffix + '.png')
                        cv2.imwrite(outfile, img)
                        success += 1
                        with fuckit:
                            iolib.write_to_eof(logfilename, 'Success:%s\n' % (fil))
                last_width = width; last_height = height

            except Exception:
                iolib.write_to_eof(logfilename, 'Failed:%s, Exception:%s\n' % (fil, Exception.message))
            finally:
                with fuckit:
                    iolib.print_progress(cnt, len(newlist), '%i of %i [Successes: %i]' % (cnt, len(newlist), success), bar_length=30)
                    cnt += 1
        if len(bad_res) > 0: print('Resolutions with no calibration matricies: %s' % (" ".join(bad_res)))

#region main
def main():
    '''(bool)->void
    Main is only called if the script is directly executed and can
    be used to do stuff in here like testing.

    Setting getcmdlineargs to true will set up cmdline arguments,
    which can be loaded into global variables as required (need to define)
    '''
    #read generic database setting from inifile and set as globals
    _ini_set_database_strings()

    cmdline = argparse.ArgumentParser(description='Examples:\n'
                                      'Undistort images in digikam database to c:/temp/pics\n'
                                      'lenscorrection.py -m undistort -c NEXTBASE512G -o C:/temp/pics -p DIGIKAM\n\n'

                                      'Undistort images in a path and output to c:/temp/pics\n'
                                      'lenscorrection.py -m undistort -c NEXTBASE512G -o C:/temp/pics -p c:/path/to/images/to/undistort \n\n'

                                      'Calibrate lens using images in CALIBRATION_PATH\n'
                                      'lenscorrection.py -m calibrate -c NEXTBASE512G\n\n'

                                      'Calibrate lens using images in CALIBRATION_PATH. Saves vertex detection images to the debug folder\n'
                                      'lenscorrection.py -m calibrate -c NEXTBASE512G -d\n')

    cmdline.add_argument('-m', '--mode', action='store', help='The mode, values are:\nUNDISTORT - undistorts images in path\nCALIBRATE - create lens calibration values', required=True)
    cmdline.add_argument('-p', '--path', action='store', help='Path to images to undistort. Pass DIGIKAM to use digikam database with options provided in the ini file. This is required in UNDISTORT mode.', required=False)
    cmdline.add_argument('-o', '--outpath', action='store', help='Path to store undistorted images. Must be provided in undistort mode', required=False)
    cmdline.add_argument('-c', '--camera', action='store', help='Camera model key in the ini file which defines the camera calibration parameters for the camera model specified', required=True)
    cmdline.add_argument('-d', '--debug', action='store_true', help='Run in DEBUG mode', default=False, required=False)
    cmdargs = cmdline.parse_args()

    cmdargs.mode = cmdargs.mode.lower()
    if cmdargs.mode == 'undistort' and (cmdargs.path == '' or cmdargs.path is None):
        print('\nMode was undistort but no path argument was specified.')
        iolib.exit()

    cam = get_camera(cmdargs.camera)
    if cmdargs.mode == 'undistort':
        if cmdargs.path.lower() != 'digikam' and not os.path.exists(os.path.normpath(cmdargs.path)):
            print('Path ' + os.path.normpath(cmdargs.path) + ' does not exists')
        elif cmdargs.outpath == '':
            print('Output path not specified')
        else:
            cmdargs.outpath = os.path.normpath(cmdargs.outpath)
            if os.path.isdir(cmdargs.outpath):
                title = 'Delete Files?'
                msg = 'Folder %s already exists. Do you wish to delete existing files from it?' % cmdargs.outpath
                default = msgbox.QMessageBox.No
                result = msgbox.question(title, msg, default, msgbox.QMessageBox.Yes, msgbox.QMessageBox.No)
                if result == msgbox.QMessageBox.Yes:
                    iolib.files_delete(cmdargs.outpath)
            else:
                iolib.create_folder(cmdargs.outpath)

            if cmdargs.path.lower() == 'digikam':
                digikam = digikamlib.MeasuredImages(_DIGIKAM_CONNECTION_STRING, cam.digikam_measured_tag, cam.digikam_camera_tag)
                lst = digikam.valid_images
                undistort(cam, lst, cmdargs.outpath)
            else:
                undistort(cam, os.path.normpath(cmdargs.path), cmdargs.outpath)
            print('Undistort completed')
    elif cmdargs.mode == 'calibrate':
        calibrate(cam)
        print('Calibration(s) saved to database.')
    else:
        print('\nInvalid or missing mode argument. Valid values are undistort or calibrate')
        iolib.exit()




if __name__ == '__main__':
    main()
#endregion
