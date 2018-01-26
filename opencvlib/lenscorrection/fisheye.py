# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, logging-format-interpolation

'''fisheye correction'''
import cv2 as _cv2
import joblib as _joblib
import logging as _logging

import numpy as _np
import os as _os
import pickle as _pickle

_EPS = _np.finfo(_np.float).eps

def load_model(filename, calib_img_shape=None):
    """Load a previosly saved fisheye model."""

    return FishEye.load(filename, calib_img_shape)


def extract_corners(img, img_index, nx, ny, subpix_criteria, verbose):
    """Extract chessboard corners."""

    if isinstance(img, str):
        fname = img
        if verbose:
            _logging.info("Processing img: {}...".format(_os.path.split(fname)[1]))

        #
        # Load the image.
        #
        img = _cv2.imread(fname)
    else:
        if verbose:
            _logging.info("Processing img: {}...".format(img_index))

    if img.ndim == 3:
        gray = _cv2.cvtColor(img, _cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    #
    # Find the chess board corners
    #
    ret, cb_2D_pts = _cv2.findChessboardCorners(
        gray,
        (nx, ny),
        _cv2.CALIB_CB_ADAPTIVE_THRESH+_cv2.CALIB_CB_FAST_CHECK+_cv2.CALIB_CB_NORMALIZE_IMAGE
    )

    if ret:
        #
        # Refine the corners.
        #
        cb_2D_pts = _cv2.cornerSubPix(gray, cb_2D_pts, (3, 3), (-1, -1), subpix_criteria)

    return ret, cb_2D_pts


class FishEye(object):
    """Fisheye Camera Class

    Wrapper around the opencv fisheye calibration code.

    Args:
        nx, ny (int): Number of inner corners of the chessboard pattern, in x and y axes.
        verbose (bool): verbose flag.
    """

    def __init__(self, nx, ny, img_shape=None, verbose=False
        ):

        self._nx = nx
        self._ny = ny
        self._verbose = verbose
        self._K = _np.zeros((3, 3))
        self._D = _np.zeros((4, 1))
        self._img_shape = img_shape
        self.chessboard_model = _np.zeros((1, self._nx*self._ny, 3), _np.float32)
        self.chessboard_model[0, :, :2] = _np.mgrid[0:self._nx, 0:self._ny].T.reshape(-1, 2)

    def calibrate(
        self, img_paths=None, imgs=None, update_model=True, max_iter=30, eps=1e-6, show_imgs=False, return_mask=False,
        calibration_flags=_cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC+_cv2.fisheye.CALIB_CHECK_COND+_cv2.fisheye.CALIB_FIX_SKEW,
        n_jobs=-1, backend='threading'):
        """Calibration

        Calibrate a fisheye model using images of chessboard pattern.

        Args:
            img_paths (list of paths): Paths to images of chessboard pattern.
            update_model (optional[bool]): Whether to update the stored clibration. Set to
                False when you are interested in calculating the position of
                chess boards.
            max_iter (optional[int]): Maximal iteration number. Defaults to 30.
            eps (optional[int]): error threshold. Defualts to 1e-6.
            show_imgs (optional[bool]): Show calibtration images.
            calibration_flags (optional[int]): opencv flags to use in the opencv.fisheye.calibrate command.
        """

        assert not ((img_paths is None) and (imgs is None)), 'Either specify imgs or img_paths'

        #
        # Arrays to store the chessboard image points from all the images.
        #
        chess_2Dpts_list = []

        subpix_criteria = (_cv2.TERM_CRITERIA_EPS+_cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)

        if show_imgs:
            _cv2.namedWindow('checkboard img', _cv2.WINDOW_AUTSIZE)
            _cv2.namedWindow('fail img', _cv2.WINDOW_AUTOSIZE)

        if img_paths is not None:
            imgs = img_paths

        with _joblib.Parallel(n_jobs=n_jobs, backend=backend) as _joblib.Parallel:
            rets = _joblib.Parallel(
                _joblib.delayed(extract_corners)(
                    img, img_index, self._nx, self._ny, subpix_criteria, self._verbose
                    ) for img_index, img in enumerate(imgs)
            )

        mask = []
        for img_index, (img, (ret, cb_2d_pts)) in enumerate(zip(imgs, rets)):

            if isinstance(img, str):
                fname = img
                if self._verbose:
                    _logging.info("Processing img: {}...".format(_os.path.split(fname)[1]))
                img = _cv2.imread(fname)
            else:
                if self._verbose:
                    _logging.info("Processing img: {}...".format(img_index))

            if self._img_shape is None:
                self._img_shape = img.shape[:2]
            else:
                assert self._img_shape == img.shape[:2], "All images must share the same size."
            if ret:
                mask.append(True)
                # Was able to find the chessboard in the image, append the 3D points
                # and image points (after refining them).
                if self._verbose:
                    _logging.info('OK')

                # The 2D points are reshaped to (1, N, 2). This is a hack to handle the bug
                # in the opecv python wrapper.
                chess_2Dpts_list.append(cb_2d_pts.reshape(1, -1, 2))

                if show_imgs:
                    # Draw and display the corners
                    img = _cv2.drawChessboardCorners(
                        img.copy(), (self._nx, self._ny),
                        cb_2d_pts,
                        ret
                    )
                    _cv2.imshow('checkboard img', img)
                    _cv2.waitKey(500)
            else:
                mask.append(False)

                if self._verbose:
                    _logging.info('FAIL!')

                if show_imgs:
                    # Show failed img
                    _cv2.imshow('fail img', img)
                    _cv2.waitKey(500)

        if show_imgs:
            _cv2.destroyAllWindows()

        N_OK = len(chess_2Dpts_list)
        rvecs = [_np.zeros((1, 1, 3), dtype=_np.float64) for i in range(N_OK)]
        tvecs = [_np.zeros((1, 1, 3), dtype=_np.float64) for i in range(N_OK)]

        # Update the intrinsic model
        if update_model:
            K = self._K
            D = self._D
        else:
            K = self._K.copy()
            D = self._D.copy()

        rms, _, _, _, _ = _cv2.fisheye.calibrate(
                [self.chessboard_model]*N_OK,
                chess_2Dpts_list,
                (img.shape[1], img.shape[0]),
                K, D, rvecs, tvecs, calibration_flags,
                (_cv2.TERM_CRITERIA_EPS+_cv2.TERM_CRITERIA_MAX_ITER, max_iter, eps)
            )

        if return_mask:
            return rms, K, D, rvecs, tvecs, mask

        return rms, K, D, rvecs, tvecs


    def undistort(self, distorted_img, undistorted_size=None, R=_np.eye(3), K=None):
        """Undistort an image using the fisheye model"""

        if K is None:
            K = self._K

        if undistorted_size is None:
            undistorted_size = distorted_img.shape[:2]

        map1, map2 = _cv2.fisheye.initUndistortRectifyMap(self._K, self._D, R, K, undistorted_size, _cv2.CV_16SC2
        )

        undistorted_img = _cv2.remap(distorted_img, map1, map2, interpolation=_cv2.INTER_LINEAR, borderMode=_cv2.BORDER_CONSTANT)

        return undistorted_img


    def projectPoints(self, object_points=None, skew=0, rvec=None, tvec=None):
        """Projects points using fisheye model.
        """

        if object_points is None:
            #
            # The default is to project the checkerboard.
            #
            object_points = self.chessboard_model

        if object_points.ndim == 2:
            object_points = _np.expand_dims(object_points, 0)

        if rvec is None:
            rvec = _np.zeros(3).reshape(1, 1, 3)
        else:
            rvec = _np.array(rvec).reshape(1, 1, 3)

        if tvec is None:
            tvec = _np.zeros(3).reshape(1, 1, 3)
        else:
            tvec = _np.array(tvec).reshape(1, 1, 3)

        image_points, _ = _cv2.fisheye.projectPoints(object_points, rvec, tvec, self._K, self._D, alpha=skew)

        return _np.squeeze(image_points)


    def undistortPoints(self, distorted, R=_np.eye(3), K=None):
        """Undistorts 2D points using fisheye model.
        """

        if distorted.ndim == 2:
            distorted = _np.expand_dims(distorted, 0)
        if K is None:
            K = self._K

        undistorted = _cv2.fisheye.undistortPoints(
            distorted.astype(_np.float32), self._K, self._D, R=R, P=K)

        return _np.squeeze(undistorted)


    def undistortDirections(self, distorted):
        """Undistorts 2D points using fisheye model.

        Args:
            distorted (array): nx2 array of distorted image coords (x, y).

        Retruns:
            Phi, Theta (array): Phi and Theta undistorted directions.
        """

        assert distorted.ndim == 2 and distorted.shape[1] == 2, "distorted should be nx2 points array."

        # Calculate
        f = _np.array((self._K[0, 0], self._K[1, 1])).reshape(1, 2)
        c = _np.array((self._K[0, 2], self._K[1, 2])).reshape(1, 2)
        k = self._D.ravel().astype(_np.float64)

        # Image points
        pi = distorted.astype(_np.float)

        # World points (distorted)
        pw = (pi-c)/f

        # Compensate iteratively for the distortion.
        theta_d = _np.linalg.norm(pw, ord=2, axis=1)
        theta = theta_d
        for _ in range(10):
            theta2 = theta**2
            theta4 = theta2**2
            theta6 = theta4*theta2
            theta8 = theta6*theta2
            theta = theta_d / (1 + k[0]*theta2 + k[1]*theta4 + k[2]*theta6 + k[3]*theta8)

        theta_d_ = theta * (1 + k[0]*theta**2 + k[1]*theta**4 + k[2]*theta**6 + k[3]*theta**8)

        # Mask stable theta values.
        ratio = _np.abs(theta_d_- theta_d) / (theta_d + _EPS)
        mask = (ratio < 1e-2)

        # Scale is equal to \prod{\r}{\theta_d} (http://docs.opencv.org/trunk/db/d58/group__calib3d__fisheye.html)
        scale = _np.tan(theta) / (theta_d + _EPS)

        # Undistort points
        pu = pw * scale.reshape(-1, 1)
        phi = _np.arctan2(pu[:, 0], pu[:, 1])

        return phi, theta, mask

    def save(self, filename):
        """Save the fisheye model."""

        with open(filename, 'wb') as f:
            _pickle.dump(self, f)

    @property
    def img_shape(self):
        """Shape of image used for calibration."""

        return self._img_shape

    @classmethod
    def load(cls, filename, calib_img_shape=None):
        """Load a previously saved fisheye model.
        Note: this is a classmethod.

        Args:
            filename (str): Path to previously saved FishEye object.
            calib_img_shape (Optional[tuple]): Shape of images used for
                calibration.
        Returns:
            FishEye object.
        """

        with open(filename, 'rb') as f:
            tmp_obj = _pickle.load(f)

        assert hasattr(tmp_obj, '_img_shape') or calib_img_shape is not None, \
               "FishEye obj does not include 'img_shape'. You need to explicitly specify one."

        img_shape = getattr(tmp_obj, 'img_shape', calib_img_shape)
        img_shape = img_shape[:2]

        obj = FishEye(nx=tmp_obj._nx, ny=tmp_obj._ny, img_shape=img_shape)
        obj.__dict__.update(tmp_obj.__dict__)

        return obj
