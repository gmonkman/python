# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Work with human faces'''

import cv2
import os.path as path

from funclib.iolib import get_file_parts

#TODO Test blur_face
def blur_face(imagepath, overwrite_original=False, save_face=False):
    '''(str, bool, bool)
    Blur a faces found in an image
    imagepath: path to image
    overwrite_original: overwrite or save as new file in image folder
    save_face: save the detected face as seperate file in image folder
    '''
    folder, file_part, ext_with_dot = get_file_parts(imagepath)
    image = cv2.imread(imagepath)
    result_image = image.copy()

    # Specify the trained cascade classifier
    face_cascade_name = "./haarcascade_frontalface_alt.xml"

    # Create a cascade classifier
    face_cascade = cv2.CascadeClassifier()

    # Load the specified classifier
    face_cascade.load(face_cascade_name)

    #Preprocess the image
    grayimg = cv2.cvtColor(image, cv2.cv.CV_BGR2GRAY)
    grayimg = cv2.equalizeHist(grayimg)

    #Run the classifiers
    faces = face_cascade.detectMultiScale(grayimg, 1.1, 2, 0|cv2.cv.CV_HAAR_SCALE_IMAGE, (30, 30))

        # If there are faces in the images
    for f in faces:         # For each face in the image
        # Get the origin co-ordinates and the length and width till where the face extends
        x, y, w, h = [v for v in f]

        # get the rectangle img around all the faces
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 0), 5)
        sub_face = image[y:y+h, x:x+w]
        # apply a gaussian blur on this new recangle image
        sub_face = cv2.GaussianBlur(sub_face, (23, 23), 30)
        # merge this blurry rectangle to our final image
        result_image[y:y+sub_face.shape[0], x:x+sub_face.shape[1]] = sub_face
        face_file_name = "./face_" + str(y) + ext_with_dot
        if save_face:
            face_file_name = path.normpath(path.join(folder, file_part + '_face' + ext_with_dot))
            cv2.imwrite(face_file_name, sub_face)

    # cv2.imshow("Detected face", result_image)
    if overwrite_original:
        file_name = imagepath
    else:
        file_name = path.join(folder, file_part + '_anon' + ext_with_dot)
    file_name = path.normpath(file_name)
    cv2.imwrite(file_name, result_image)
