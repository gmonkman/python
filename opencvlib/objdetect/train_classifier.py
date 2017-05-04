# pylint: disable=C0103, too-few-public-methods, locally-disabled,
# no-self-use, unused-argument

'''classifier training'''
import argparse as ap
import glob
import os

#from skimage.feature import local_binary_pattern
from sklearn.svm import LinearSVC
#from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib

from opencvlib.objdetect import config

#import opencvlib.objdetect.config as config
def parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument(
        '-p', "--posfeat", help="Path to the positive features directory", required=True)
    parser.add_argument(
        '-n', "--negfeat", help="Path to the negative features directory", required=True)
    parser.add_argument('-c', "--classifier",
                        help="Classifier to be used", default="LIN_SVM")
    args = vars(parser.parse_args())

    pos_feat_path = args["posfeat"]
    neg_feat_path = args["negfeat"]

    # Classifiers supported
    clf_type = args['classifier']


    fds = []
    labels = []
    # Load the positive features
    for feat_path in glob.glob(os.path.join(pos_feat_path, "*.feat")):
        fd = joblib.load(feat_path)
        fds.append(fd)
        labels.append(1)

    # Load the negative features
    for feat_path in glob.glob(os.path.join(neg_feat_path, "*.feat")):
        fd = joblib.load(feat_path)
        fds.append(fd)
        labels.append(0)

    if clf_type is "LIN_SVM":
        clf = LinearSVC()
        print("Training a Linear SVM Classifier")
        clf.fit(fds, labels)
        # If feature directories don't exist, create them
        if not os.path.isdir(os.path.split(config.model_path)[0]):
            os.makedirs(os.path.split(config.model_path)[0])
        joblib.dump(clf, config.model_path)
        print("Classifier saved to {}".format(config.model_path))
