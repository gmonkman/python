#pylint: skip-file

'''
Give the path to the examples/faces directory as the argument to this
program. For example, if you are in the python_examples folder then
execute this program by running:
./train_shape_predictor.py ../examples/faces
'''

import os
import sys
import glob
import dlib
from skimage import io

import dliblib.ini as ini
from funclib import iolib


faces_folder = ini.Cfg.tryread('EXAMPLES', 'faces_folder')
assert iolib.folder_exists(faces_folder), 'Face folder %s not found or not specified in ini file.' % faces_folder

options = dlib.shape_predictor_training_options()
options.oversampling_amount = 300

options.nu = 0.05
options.tree_depth = 2
options.be_verbose = True


training_xml_path = os.path.join(faces_folder, "training_with_face_landmarks.xml")
dlib.train_shape_predictor(training_xml_path, "predictor.dat", options)

print("\nTraining accuracy: {}".format(
    dlib.test_shape_predictor(training_xml_path, "predictor.dat")))

testing_xml_path = os.path.join(faces_folder, "testing_with_face_landmarks.xml")
print("Testing accuracy: {}".format(
    dlib.test_shape_predictor(testing_xml_path, "predictor.dat")))

# Now let's use it as you would in a normal application.  First we will load it
# from disk. We also need to load a face detector to provide the initial
# estimate of the facial location.
predictor = dlib.shape_predictor("predictor.dat")
detector = dlib.get_frontal_face_detector()


print("Showing detections and predictions on the images in the faces folder...")
win = dlib.image_window()
for f in glob.glob(os.path.join(faces_folder, "*.jpg")):
    print("Processing file: {}".format(f))
    img = io.imread(f)

    win.clear_overlay()
    win.set_image(img)

    dets = detector(img, 1)
    print("Number of faces detected: {}".format(len(dets)))
    for k, d in enumerate(dets):
        print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
            k, d.left(), d.top(), d.right(), d.bottom()))

        # Get the landmarks/parts for the face in box d.
        shape = predictor(img, d)
        print("Part 0: {}, Part 1: {} ...".format(shape.part(0),
                                                  shape.part(1)))
        # Draw the face landmarks on the screen.
        win.add_overlay(shape)

    win.add_overlay(dets)
    dlib.hit_enter_to_continue()

