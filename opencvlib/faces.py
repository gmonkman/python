# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument
'''Work with human faces'''
import os.path as _path
import shutil as _shutil

import cv2 as _cv2

import funclib.iolib as _iolib
from funclib.stringslib import datetime_stamp as _datetime_stamp


def blur_face(imagepath, save_face=False, overwrite_original=False):
    '''(str, bool, bool)
    Blur faces found in an image
    imagepath: path to image

    If overwrite_original, then originals will be moved
    to a subfolder with datetime stamp.

    Otherwise the blurred images will be created in this subdir
    '''

    folder, file_part, ext_with_dot = _iolib.get_file_parts2(imagepath)
    image = _cv2.imread(imagepath)
    result_image = image.copy()

    # Specify the trained cascade classifier
    face_cascade_name = "./bin/haar/haarcascade_frontalface_alt.xml"

    # Create a cascade classifier
    face_cascade = _cv2.CascadeClassifier()

    # Load the specified classifier
    face_cascade.load(face_cascade_name)

    # Preprocess the image
    grayimg = _cv2.cvtColor(image, _cv2.cv.CV_BGR2GRAY)
    grayimg = _cv2.equalizeHist(grayimg)

    # Run the classifiers
    faces = face_cascade.detectMultiScale(
        grayimg, 1.1, 2, 0 | _cv2.cv.CV_HAAR_SCALE_IMAGE, (30, 30))

    # If there are faces in the images
    for f in faces:         # For each face in the image
        # Get the origin co-ordinates and the length and width till where the
        # face extends
        x, y, w, h = [v for v in f]

        # get the rectangle img around all the faces
        _cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 5)
        sub_face = image[y:y + h, x:x + w]
        # apply a gaussian blur on this new recangle image
        sub_face = _cv2.GaussianBlur(sub_face, (23, 23), 30)
        # merge this blurry rectangle to our final image
        result_image[y:y + sub_face.shape[0],
                     x:x + sub_face.shape[1]] = sub_face
        face_file_name = "./face_" + str(y) + ext_with_dot
        if save_face:
            face_file_name = _path.normpath(
                _path.join(
                    folder,
                    file_part +
                    '_face' +
                    ext_with_dot))
            _cv2.imwrite(face_file_name, sub_face)

    # _cv2.imshow("Detected face", result_image)

    stamp = _datetime_stamp()
    newfld = _path.join(folder, stamp)

    # DEBUG
    if overwrite_original:
        _iolib.create_folder(newfld)
        _shutil.copy(imagepath, _path.normpath(_path.join(newfld, file_part)))
        _cv2.imwrite(imagepath, result_image)
    else:
        _cv2.imwrite(_path.join(newfld, file_part), result_image)
