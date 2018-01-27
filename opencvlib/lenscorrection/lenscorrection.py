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

Examples:
    Undistort images in digikam database to c:/temp/pics
    lenscorrection.py -m undistort -c NEXTBASE512G -o C:/temp/pics -p DIGIKAM

    Undistort images in a path and output to c:/temp/pics
    lenscorrection.py -m undistort -c NEXTBASE512G -o C:/temp/pics -p c:/path/to/images/to/undistort

    Undistort images using a fisheye profile, in a path and output to c:/temp/pics
    lenscorrection.py -m undistort_fisheye -c NEXTBASE512G -o C:/temp/pics -p c:/path/to/images/to/undistort

    Calibrate lens using images in CALIBRATION_PATH
    lenscorrection.py -m calibrate -c NEXTBASE512G

    Calibrate lens using images in CALIBRATION_PATH. Saves vertex detection images to the debug folder
    lenscorrection.py -m calibrate -c NEXTBASE512G -d
'''
# region imports
# region base imports
from glob import glob as _glob
import argparse as _argparse
from inspect import getsourcefile as _getsourcefile
import pickle as _pickle
import os as _os
import os.path as _path
import warnings as _warn
# end region

# region 3rd party imports
import cv2 as _cv2
import fuckit as _fuckit
import numpy as _np
# endregion

# region my imports

from funclib.baselib import list_append_unique
import funclib.iolib as _iolib
import funclib.inifilelib as _inifilelib
import funclib.pyqtlib as _msgbox

from opencvlib import IMAGE_EXTENSIONS_AS_WILDCARDS as _IMAGE_EXTENSIONS_AS_WILDCARDS
import opencvlib.imgpipes.digikamlib as _digikamlib
import opencvlib.info as _info
import opencvlib.lenscorrection.lenscorrectiondb as _lenscorrectiondb
import opencvlib.transforms as _transforms

# endregion
# endregion


_PTH = _iolib.get_file_parts2(_path.abspath(_getsourcefile(lambda: 0)))[0]
_INIFILE = _PTH + '/lenscorrection.py.ini'

_DIGIKAM_CONNECTION_STRING = ''
_CALIBRATION_CONNECTION_STRING = ''
_PrintProgress = None

# region Class Declarations


class PrintProgress(object):
    '''DOS progressbar'''

    def __init__(self, maximum, bar_length=30):
        self.max = maximum
        self.bar_length = bar_length
        self.iteration = 0

    def increment(self):
        '''tick the progress bar'''
        _iolib.print_progress(
            self.iteration, self.max, prefix='%i of %i' %
            (self.iteration, self.max), bar_length=self.bar_length)
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

    def __init__(
            self,
            calibration_path,
            model='',
            image_file_mask='',
            grid=None,
            square_size=1):
        '''(str, str, str, calibration_grid[class], int)
        Also sets up the debug path (creating one if it doesnt exist)
        and image path (checking if it the image path exists)
        '''
        self._model = model
        self._calibration_path = _os.path.normpath(calibration_path)  # root
        self._grid = grid
        self._image_file_mask = image_file_mask
        self._square_size = square_size
        self._debugdir = ''
        self.digikam_camera_tag = ''  # currently set in def main
        self.digikam_measured_tag = ''

        self._calibration_path_debug = _os.path.normpath(
            _os.path.join(self.calibration_path, 'debug'))
        self._calibration_path_images = _os.path.normpath(self.calibration_path)
        _iolib.create_folder(self.calibration_path_debug)

    # region properties
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
    # endregion

    def get_full_calibration_image_path(self):
        '''-> str
        returns the full path concatenated with the mask so we can
        glob all the images in the cameras calibration path
        '''
        return _os.path.normpath(
            _os.path.join(
                self._calibration_path_images,
                self._image_file_mask))

    def get_debug_dir(self):
        '''-> str
        Returns the path for debug image output
        Creates it if it doesnt exist
        '''
        s = _os.path.normpath(_os.path.join(self._calibration_path, 'debug'))
        _iolib.create_folder(s)
        return s


class Calibration(object):
    '''container for a camera calibration at a specific resolution'''

    def __init__(
            self,
            camera_model,
            wildcarded_images_path,
            height,
            width,
            pattern_size=(
                9,
                6),
            square_size=1):
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
        pattern_points = _np.zeros((_np.prod(self.pattern_size), 3), _np.float32)
        pattern_points[:, :2] = _np.indices(self.pattern_size).T.reshape(-1, 2)
        pattern_points *= self.square_size
        return pattern_points

    def calibrate(self, fisheye_max_iter=30, skip_fisheye=False):
        '''main calibration entry point'''
        obj_points = []
        img_points = []
        img_points_fisheye = []
        fcnt = 0
        cnt = 0

        term = (_cv2.TERM_CRITERIA_EPS + _cv2.TERM_CRITERIA_COUNT, fisheye_max_iter, 0.1)

        for fn in _iolib.file_list_glob_generator(self.wildcarded_images_path):
            if _info.ImageInfo.is_image(fn):
                img = _cv2.imread(_os.path.normpath(fn), 0)
                w, h = _info.ImageInfo.resolution(img)
                if w == self.width and h == self.height:
                    cnt += 1
                    found, corners = _cv2.findChessboardCorners(
                        img, self.pattern_size, flags=_cv2.CALIB_CB_ADAPTIVE_THRESH + _cv2.CALIB_CB_NORMALIZE_IMAGE)
                    if found:
                        fcnt += 1
                        _cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), term)
                        img_points.append(corners.reshape(-1, 2))
                        img_points_fisheye.append(corners.reshape(1, -1, 2))
                        obj_points.append(self._pattern_points)
                    else:
                        self.messages.append(
                            'Chessboard vertices not found in %s' % (fn))

                    _PrintProgress.increment()

        if not img_points:
            raise ValueError('Failed to find any corners. OpenCV findChessboardCorners is bugged, pattern size must be 9 x 6 vertices in photo and ini file.')

        self.img_total_count = cnt
        self.img_used_count = fcnt
        n_ok = len(img_points_fisheye)

        # calculate camera distortion
        rms, camera_matrix, dist_coefs, rvecs, tvecs = _cv2.calibrateCamera(
            obj_points, img_points, (self.width, self.height), None, None)

        cm = _pickle.dumps(camera_matrix, _pickle.HIGHEST_PROTOCOL)
        dc = _pickle.dumps(dist_coefs, _pickle.HIGHEST_PROTOCOL)
        rv = _pickle.dumps(rvecs, _pickle.HIGHEST_PROTOCOL)
        tv = _pickle.dumps(tvecs, _pickle.HIGHEST_PROTOCOL)

        if not skip_fisheye:
            #K and D passed by ref in fisheye.calibrate. Initialise them first.
            K = _np.zeros((3, 3))
            D = _np.zeros((4, 1))
            #reset rvecs and tvecs for fisheye model
            rvecs = [_np.zeros((1, 1, 3), dtype=_np.float64) for i in range(n_ok)]
            tvecs = [_np.zeros((1, 1, 3), dtype=_np.float64) for i in range(n_ok)]
            #pattern_points is a tuple with the number of x and y vertices of the chess board
            #ie (9,6) would be a chessboard with 9 x 6 vertices
            chessboard_model = _np.zeros((1, self.pattern_size[0] * self.pattern_size[1], 3), dtype=_np.float32)
            chessboard_model[0, :, :2] = _np.mgrid[0:self.pattern_size[0], 0:self.pattern_size[1]].T.reshape(-1, 2)
            
            fisheye_calibration_flags = _cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + _cv2.fisheye.CALIB_CHECK_COND + _cv2.fisheye.CALIB_FIX_SKEW
            term = (_cv2.TERM_CRITERIA_EPS + _cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)

            rms, _, _, _, _ = _cv2.fisheye.calibrate(
                [chessboard_model]*n_ok, img_points_fisheye, (self.width, self.height),
                K, D, rvecs, tvecs, fisheye_calibration_flags, term)

            kk = _pickle.dumps(K, _pickle.HIGHEST_PROTOCOL)
            dd = _pickle.dumps(D, _pickle.HIGHEST_PROTOCOL)
        else:
            kk = None
            dd = None

        with _lenscorrectiondb.Conn(cnstr=_CALIBRATION_CONNECTION_STRING) as conn:
            db = _lenscorrectiondb.CalibrationCRUD(conn)
            modelid = int(db.crud_camera_upsert(self.camera_model))

            #calibrationid returned by crud_calibration_upsert, but we dont need it
            _ = int(db.crud_calibration_upsert(
                modelid, self.width, self.height, cm, dc, rms, rv, tv, kk, dd))
            conn.commit()

    @property
    def result_str(self):
        '''result_str getter'''
        return 'Camera %s Resolution %ix%i: %i of %i were useable' % (self.camera_model,
            self.width, self.height, self.img_used_count, self.img_total_count)
# endregion


def list_profiles():
    '''lists all valid camera profiles saved in the database'''
    with _lenscorrectiondb.Conn(cnstr=_CALIBRATION_CONNECTION_STRING) as conn:
        db = _lenscorrectiondb.CalibrationCRUD(conn)
        res = db.list_existing()
    print('\n'.join(map(str, res)))


def get_camera(model):
    '''(str)-> [class] camera
    Reads camera details from the lenscorrection.py.ini,
    returning the camera class.
    model is generally parsed from a command line argument when this routine is executed.
    '''
    if not _inifilelib.iniexists(_INIFILE):
        raise IOError('Ini file %s not found.' % _INIFILE)
    ini = _inifilelib.ConfigFile(_INIFILE)

    calpath = ini.tryread(model, 'CALIBRATION_PATH', force_create=False)
    if not _os.path.exists(calpath):
        raise IOError('Calibration path %s not found.' % (calpath))

    cam = CameraIni(model=model, calibration_path=calpath)

    cam.grid = CalibrationGrid(int(ini.tryread(model, 'x_vertices', force_create=False)), int(
        ini.tryread(model, 'y_vertices', force_create=False)))

    cam.image_file_mask = ini.tryread(
        model, 'IMAGE_PATTERN', force_create=False)
    if cam.image_file_mask == '':
        raise ValueError(
            'Image pattern (option IMAGE_PATTERN) could not be read from lenscorrection.py.ini')

    cam.square_size = int(
        ini.tryread(
            model,
            'square_size',
            force_create=False))
    cam.digikam_camera_tag = ini.tryread(
        model, 'DIGIKAM_CAMERA_TAG', force_create=False)
    cam.digikam_measured_tag = ini.tryread(
        model, 'DIGIKAM_MEASURED_TAG', force_create=False)
    return cam


def _ini_set_database_strings():
    '''load db config strings from the inifile'''
    if not _inifilelib.iniexists(_INIFILE):
        raise IOError('Ini file %s not found.' % _INIFILE)
    ini = _inifilelib.ConfigFile(_INIFILE)
    global _DIGIKAM_CONNECTION_STRING
    _DIGIKAM_CONNECTION_STRING = ini.tryread(
        'DATABASE', 'DIGIKAM_CONNECTION_STRING', force_create=False)
    global _CALIBRATION_CONNECTION_STRING
    _CALIBRATION_CONNECTION_STRING = ini.tryread(
        'DATABASE', 'CALIBRATION_CONNECTION_STRING', force_create=False)


def calibrate(cam, skip_fisheye=False):
    '''(camera[class])
    Pass in a camera class object, initialised from the ini file
    by calling get_camera
    '''
    assert isinstance(cam, CameraIni)

    if not _os.path.exists(cam.calibration_path):
        raise(ValueError('Ini defined calibration path  "%s" not found.' % cam.calibration_path()))

    dims = _info.ImageInfo.get_image_resolutions(cam.get_full_calibration_image_path())

    img_path = cam.get_full_calibration_image_path()

    # set up a list of classes for the different resolutions of calibration
    # images
    calibrations = [
        Calibration(
            cam.model,
            img_path,
            h,
            w,
            (cam.grid.x_vertices,
             cam.grid.y_vertices),
            cam.square_size) for w,
        h in dims]

    global _PrintProgress
    _PrintProgress = PrintProgress(len(_glob(img_path)))
    _PrintProgress.iteration = 1

    for Cal in calibrations:
        assert isinstance(Cal, Calibration)
        Cal.calibrate(skip_fisheye)

    for Cal in calibrations:
        print(Cal.result_str)


def _undistort(cam, img, mats, crop=True, use_fisheye=True):
    '''[c]Camera, ndarray (image), dic, bool -> ndarray (image) | None
    Undistorts an image based on the lens profile loaded into the Camera class cam.
    dic is a dictionary containing the undistortion matrices
    {'cmat':cmat, 'dcoef':dcoef, 'rvect':rvect, 'tvect':tvect}

    Returns None if an exception occurs
    '''
    assert isinstance(cam, CameraIni)
    assert isinstance(img, _np.ndarray)
    try:
        h, w = img.shape[:2]
        if use_fisheye:
            R = _np.eye(3)
            map1, map2 = _cv2.fisheye.initUndistortRectifyMap(mats['K'], mats['D'], R, mats['K'], (w, h), _cv2.CV_16SC2)
            dst = _cv2.remap(img, map1, map2, interpolation=_cv2.INTER_LINEAR, borderMode=_cv2.BORDER_CONSTANT)
        else:
            newcameramtx, roi = _cv2.getOptimalNewCameraMatrix(
                mats['cmat'], mats['dcoef'], (w, h), 1, (w, h))
            dst = _cv2.undistort(
                img,
                mats['cmat'],
                mats['dcoef'],
                None,
                newcameramtx)
            if roi == (0, 0, 0, 0):
                _warn.warn('_cv2.getOptimalNewCameraMatrix could not identify the ROI. Try recalibrating with more small calibration images at the camera edge or sets of larger calibration images.\n\nImages were undistorted but should be checked.')
            else:
                if crop:
                    x, y, w, h = roi
                    dst = dst[y:y + h, x:x + w]

    except Exception:
        print(Exception.message)
        dst = None
    finally:
        return dst


def undistort(
        cam,
        imgpaths_or_imagelist,
        outpath,
        label='_UND',
        label_fisheye='_FISHUND',
        crop=True,
        use_nearest_aspect=False, use_fisheye=False):
    '''(Camera, str|iterable, str, str, bool) -> void
    Bulk undistort, reading in the camera profile according to model name as matched in lenscorrection.py.ini
    Multiple paths can be provided

    imgpaths_or_imagelist can be an iterable of paths or a list. If appears to be paths,
    then _glob will be combined with known image extensions to list all files in paths
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
        # look to see if the list is mostly (50%) valid files rather than
        # directories
        validcnt = 0.0
        for myfiles in imgpaths_or_imagelist:
            validcnt += _os.path.isfile(_os.path.normpath(myfiles))
        if validcnt / len(imgpaths_or_imagelist) > 0.5:
            useglob = False

    if useglob:
        globlist = _iolib.file_list_generator(
            imgpaths_or_imagelist,
            _IMAGE_EXTENSIONS_AS_WILDCARDS)
        newlist = []
        for wildcards in globlist:
            for fil in _glob(wildcards):
                newlist.append(fil)
    else:
        newlist = imgpaths_or_imagelist

    cnt = 1
    success = 0
    outpath = _path.normpath(outpath)
    _iolib.create_folder(outpath)
    logfilename = _iolib.get_file_name(outpath)
    
    
    print('Undistort mode: %s' % ('fisheye lens model' if use_fisheye else 'standard lens model'))

    with _lenscorrectiondb.Conn(cnstr=_CALIBRATION_CONNECTION_STRING) as conn:
        db = _lenscorrectiondb.CalibrationCRUD(conn)
        last_width = 0
        last_height = 0
        for fil in newlist:
            try:
                resize_suffix = ''
                # used later to rebuild output file name
                path, name, ext = _iolib.get_file_parts(fil)
                path = path + ''
                ext = ext + ''  # silly thing to get rid of unused varible in pylint
                orig_img = _cv2.imread(fil)
                width, height = _info.ImageInfo.resolution(orig_img)
                if (last_width != width and last_height !=
                        height) and height > 0 and width > 0:
                    blobs = db.crud_read_calibration_blobs(
                        cam.model, height, width)
                    if use_nearest_aspect and blobs is None:  # use next best if no blobs found
                        blobs = db.blobs_get_nearest_aspect_match(
                            cam.model, height, width)
                        if blobs is not None:
                            w, h = blobs['matched_resolution_w_by_h']
                            list_append_unique(
                                subst_res,
                                'No exact calibration for resolution %ix%i, resized and used nearest match %ix%i' %
                                (width,
                                 height,
                                 w,
                                 h))
                            orig_img = _transforms.resize(orig_img, w, h)
                            resize_suffix = '_RZ%ix%i' % (w, h)

                if blobs is None:
                    _iolib.write_to_eof(
                        logfilename, 'No calibration data for image %s, resolution [%sx%s]' %
                        (fil, width, height))
                    list_append_unique(bad_res, '%ix%i' % (width, height))
                else:
                    #{'cmat':cmat, 'dcoef':dcoef, 'rvect':rvect, 'tvect':tvect, 'K':K, 'D':D}
                    img = _undistort(cam, orig_img, blobs, crop, use_fisheye=use_fisheye)
                    if img is None:
                        _iolib.write_to_eof(
                            logfilename,
                            'File %s failed in _undistort.\n' %
                            (fil))
                    else:

                        if use_fisheye:
                            outfile = _os.path.join(outpath, name + label_fisheye + resize_suffix + '.jpg')
                        else:
                            outfile = _os.path.join(outpath, name + label + resize_suffix + '.jpg')
                        
                        outfile = _path.normpath(outfile)
                        
                        _cv2.imwrite(outfile, img)
                        success += 1
                        with _fuckit:
                            _iolib.write_to_eof(
                                logfilename,
                                'Success:%s\n' %
                                (fil))
                last_width = width
                last_height = height

            except Exception:
                _iolib.write_to_eof(
                    logfilename, 'Failed:%s, Exception:%s\n' %
                    (fil, Exception.message))
            finally:
                with _fuckit:
                    _iolib.print_progress(
                        cnt, len(newlist), '%i of %i [Successes: %i]' %
                        (cnt, len(newlist), success), bar_length=30)
                    cnt += 1
        if bad_res:
            print(
                'Resolutions with no calibration matricies: %s' %
                (" ".join(bad_res)))

# region main


def main():
    '''(bool)->void
    Main is only called if the script is directly executed and can
    be used to do stuff in here like testing.

    Setting getcmdlineargs to true will set up cmdline arguments,
    which can be loaded into global variables as required (need to define)
    '''
    # read generic database setting from inifile and set as globals

    cmdline = _argparse.ArgumentParser(
        description='Examples:\n'
        'Undistort images in digikam database to c:/temp/pics\n'
        'lenscorrection.py -m undistort -c NEXTBASE512G -o C:/temp/pics -p DIGIKAM\n\n'
        'Undistort images in a path and output to c:/temp/pics\n'
        'lenscorrection.py -m undistort -c NEXTBASE512G -o C:/temp/pics -p c:/path/to/images/to/undistort \n\n'
        'Undistort images using fisheye, in a path and output to c:/temp/pics\n'
        'lenscorrection.py -m undistort_fisheye -c NEXTBASE512G -o C:/temp/pics -p c:/path/to/images/to/undistort \n\n'
        'Calibrate lens using images in CALIBRATION_PATH\n'
        'lenscorrection.py -m calibrate -c NEXTBASE512G\n\n'
        'Calibrate lens using images in CALIBRATION_PATH. Saves vertex detection images to the debug folder\n'
        'lenscorrection.py -m calibrate -c NEXTBASE512G -d\n'
        'List existing camera calibration profiles\n'
        'lenscorrection.py -m list\n')


    cmdline.add_argument(
        '-m',
        '--mode',
        action='store',
        help='The mode, values are:\nundistort - undistorts images in path\nundistort_fisheye - undistorts images in path using fisheye lens profile\ncalibrate - create lens calibration values',
        required=True)
    cmdline.add_argument(
        '-p',
        '--path',
        action='store',
        help='Path to images to undistort. Pass DIGIKAM to use digikam database with options provided in the ini file. This is required in UNDISTORT mode.',
        required=False)
    cmdline.add_argument(
        '-o',
        '--outpath',
        action='store',
        help='Path to store undistorted images. Must be provided in undistort mode',
        required=False)
    cmdline.add_argument(
        '-c',
        '--camera',
        action='store',
        help='Camera model key in the ini file which defines the camera calibration parameters for the camera model specified',
        required=False)
    cmdline.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='Run in DEBUG mode',
        default=False,
        required=False)
    cmdargs = cmdline.parse_args()

    cmdargs.mode = cmdargs.mode.lower()
    if cmdargs.mode == 'undistort' and (
            cmdargs.path == '' or cmdargs.path is None):
        print('\nMode was undistort but no path argument was specified.')
        _iolib.exit()

    if cmdargs.mode in ('undistort_fisheye', 'undistort'):
        if cmdargs.path.lower() != 'digikam' and not _os.path.exists(
                _os.path.normpath(cmdargs.path)):
            print(
                'Path ' +
                _os.path.normpath(
                    cmdargs.path) +
                ' does not exists')
        elif cmdargs.outpath == '':
            print('Output path not specified')
        else:
            cmdargs.outpath = _os.path.normpath(cmdargs.outpath)
            if _os.path.isdir(cmdargs.outpath):
                title = 'Delete Files?'
                msg = 'Folder %s already exists. Do you wish to delete existing files from it?' % cmdargs.outpath
                default = _msgbox.QMessageBox.No
                result = _msgbox.question(
                    title,
                    msg,
                    default,
                    _msgbox.QMessageBox.Yes,
                    _msgbox.QMessageBox.No)
                if result == _msgbox.QMessageBox.Yes:
                    _iolib.files_delete(cmdargs.outpath)
            else:
                _iolib.create_folder(cmdargs.outpath)

            cam = get_camera(cmdargs.camera)
            if cmdargs.path.lower() == 'digikam':
                digikam = _digikamlib.MeasuredImages(
                    _DIGIKAM_CONNECTION_STRING,
                    cam.digikam_measured_tag,
                    cam.digikam_camera_tag)
                lst = digikam.valid_images
            else:
                lst = _os.path.normpath(cmdargs.path)
            undistort(cam, lst, cmdargs.outpath, use_fisheye=(cmdargs.mode=='undistort_fisheye'))

            print('Undistort completed')
    elif cmdargs.mode == 'calibrate':
        cam = get_camera(cmdargs.camera)
        calibrate(cam)
        print('Calibration(s) saved to database.')
    elif cmdargs.mode == 'list':
        #list existing profiles
        list_profiles()
    else:
        print('\nInvalid or missing mode argument. Valid values are undistort or calibrate')
        _iolib.exit()


_ini_set_database_strings()

if __name__ == '__main__':
    main()
# endregion
