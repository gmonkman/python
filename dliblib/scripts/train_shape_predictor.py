#pylint: skip-file
'''
Run shape predictor trainer.

Set the image folders and the path to the XML
file which defines the points in dliblib.ini
in the root of this module.

Create the training XML from running dliblib.vgg2xml first.
'''
import os
import sys
import glob
import dlib
from skimage import io

import dliblib.ini as ini
from funclib import iolib


images_folder = ini.Cfg.tryread('train_shape_predictor', 'images_folder')
assert iolib.folder_exists(images_folder), 'Images folder %s not found or not specified in ini file.' % images_folder

training_xml_file = ini.Cfg.tryread('train_shape_predictor', 'training_xml_file')
assert iolib.file_exists(training_xml_file), 'Training file %s not found. This should be a file and not a directory.' % training_xml_file

predictor_out = ini.Cfg.tryread('train_shape_predictor', 'predictor_out')
assert not iolib.file_exists(predictor_out), 'Predictor %s already exists, delete this manually.' % predictor_out

options = dlib.shape_predictor_training_options()
options.oversampling_amount = 300
options.nu = 0.05
options.tree_depth = 2
options.be_verbose = True

dlib.train_shape_predictor(training_xml_file, predictor_out, options)
print("\nTraining accuracy: {}".format(dlib.test_shape_predictor(training_xml_file, predictor_out)))



if False:
    #testing_xml_path = os.path.join(images_folder, "testing_with_face_landmarks.xml")
    #print("Testing accuracy: {}".format(
    #    dlib.test_shape_predictor(testing_xml_path, "predictor.dat")))

    # Now let's use it as you would in a normal application.  First we will load it
    # from disk. We also need to load a face detector to provide the initial
    # estimate of the facial location.
    predictor = dlib.shape_predictor("predictor.dat")
    detector = dlib.get_frontal_face_detector() #find the faces

if False:
    print("Showing detections and predictions on the images in the faces folder...")
    win = dlib.image_window()
    for f in glob.glob(os.path.join(images_folder, "*.jpg")):
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

