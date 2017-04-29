# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument,wildcard-import,unused-wildcard-import
'''extract features'''

import argparse as ap
import glob
import os

from skimage.feature import hog
from skimage.io import imread
from sklearn.externals import joblib

import opencvlib.objdetect.config as config

if __name__ == "__main__":
    # Argument Parser
    parser = ap.ArgumentParser()
    parser.add_argument('-p', "--pospath", help="Path to positive images",
                        required=True)
    parser.add_argument('-n', "--negpath", help="Path to negative images",
                        required=True)
    parser.add_argument('-d', "--descriptor", help="Descriptor to be used -- HOG",
                        default="HOG")
    args = vars(parser.parse_args())

    pos_im_path = args["pospath"]
    neg_im_path = args["negpath"]

    des_type = args["descriptor"]

    # If feature directories don't exist, create them
    if not os.path.isdir(config.pos_feat_ph):
        os.makedirs(config.pos_feat_ph)

    # If feature directories don't exist, create them
    if not os.path.isdir(config.neg_feat_ph):
        os.makedirs(config.neg_feat_ph)

    print("Calculating the descriptors for the positive samples and saving them")
    for im_path in glob.glob(os.path.join(pos_im_path, "*")):
        im = imread(im_path, as_grey=True)
        if des_type == "HOG":
            fd = hog(im, config.orientations, config.pixels_per_cell,
                     config.cells_per_block, config.visualize, config.normalize)
        fd_name = os.path.split(im_path)[1].split(".")[0] + ".feat"
        fd_path = os.path.join(config.pos_feat_ph, fd_name)
        joblib.dump(fd, fd_path)
    print("Positive features saved in {}".format(config.pos_feat_ph))

    print("Calculating the descriptors for the negative samples and saving them")
    for im_path in glob.glob(os.path.join(neg_im_path, "*")):
        im = imread(im_path, as_grey=True)
        if des_type == "HOG":
            fd = hog(im, config.orientations, config.pixels_per_cell,
                     config.cells_per_block, config.visualize, config.normalize)
        fd_name = os.path.split(im_path)[1].split(".")[0] + ".feat"
        fd_path = os.path.join(config.neg_feat_ph, fd_name)
        joblib.dump(fd, fd_path)
    print("Negative features saved in {}".format(config.neg_feat_ph))

    print("Completed calculating features from training images")
