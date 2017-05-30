from __future__ import print_function
import os

import argparse
import pickle


import cv2
import numpy as np
from sklearn.cluster import KMeans

import opencvlib.keypoints as _keypoints
from opencvlib import show
from opencvlib import showarray


_NEW_SIZE = 150

def build_arg_parser():
    parser = argparse.ArgumentParser(
        description='Creates features for given images')
    parser.add_argument("-sample", "--samples", dest="cls", nargs="+", action="append",
                        required=True, help="Folders containing the training images. \
            The first element needs to be the class label.")
    parser.add_argument("-codebook-file", "--codebook-file", dest='codebook_file', required=True,
                        help="Base file name to store the codebook")
    parser.add_argument("-feature-map-file", "--feature-map-file", dest='feature_map_file', required=True,
                        help="Base file name to store the feature map")
    parser.add_argument("-scale-image", "--scale-image", dest="scale", type=int, default=150,
                        help="Scales the longer dimension of the image down to this size.")

    return parser


def load_input_map(label, input_folder):
    combined_data = []

    if not os.path.isdir(input_folder):
        print("The folder " + input_folder + " doesn't exist")
        raise IOError

    for root, dirs, files in os.walk(input_folder):
        for filename in (x for x in files if x.endswith('.jpg')):
            combined_data.append(
                {'label': label, 'image': os.path.join(root, filename)})

    return combined_data



class FeatureExtractor(object):
    def extract_image_features(self, img):
        D = _keypoints.DenseKeypoints(initFeatureScale=20)
        kps = D(img)
        S = cv2.xfeatures2d.SIFT_create()
        kps, fvs = S.compute(img, kps)
        return fvs

    def get_centroids(self, input_map, num_samples_to_fit=10):
        kps_all = []

        count = 0
        cur_label = ''
        for item in input_map: #loop through labels and images in the folder eg. item['label'] == bass, item['image'] == c:/temp/bass.jpg
            if count >= num_samples_to_fit:
                if cur_label != item['label']:
                    count = 0
                else:
                    continue

            count += 1

            if count == num_samples_to_fit:
                print("Built centroids for", item['label'])

            cur_label = item['label']
            img = cv2.imread(item['image'])
            img = resize_to_size(img)


            fvs = self.extract_image_features(img)
            kps_all.extend(fvs)

        kmeans, centroids = Quantizer().quantize(kps_all)
        return kmeans, centroids

    def get_feature_vector(self, img, kmeans, centroids):
        return Quantizer().get_feature_vector(img, kmeans, centroids)


def extract_feature_map(input_map, kmeans, centroids):
    feature_map = []

    for item in input_map:
        temp_dict = {}
        temp_dict['label'] = item['label']

        print("Extracting features for", item['image'])
        img = cv2.imread(item['image'])
        img = resize_to_size(img)

        temp_dict['feature_vector'] = FeatureExtractor().get_feature_vector(
            img, kmeans, centroids)

        if temp_dict['feature_vector'] is not None:
            feature_map.append(temp_dict)

    return feature_map



class Quantizer(object):
    def __init__(self, num_clusters=32):
        self.num_dims = 128
        self.extractor = cv2.xfeatures2d.SIFT_create()
        self.num_clusters = num_clusters
        self.num_retries = 10


    def quantize(self, datapoints):
        kmeans = KMeans(self.num_clusters,
                        n_init=max(self.num_retries, 1),
                        max_iter=10, tol=1.0)

        res = kmeans.fit(datapoints)
        centroids = res.cluster_centers_
        return kmeans, centroids


    def normalize(self, input_data):
        sum_input = np.sum(input_data)
        if sum_input > 0:
            return input_data / sum_input
        else:
            return input_data

    #just gets feature descriptors
    def get_feature_vector(self, img, kmeans, centroids):
        D = _keypoints.DenseKeypoints(initFeatureScale=20)
        kps = D(img)
        kps, fvs = self.extractor.compute(img, kps)
        labels = kmeans.predict(fvs)
        fv = np.zeros(self.num_clusters)

        for i, item in enumerate(fvs):
            fv[labels[i]] += 1

        fv_image = np.reshape(fv, ((1, fv.shape[0])))
        return self.normalize(fv_image)



class SIFTExtractor(object):
    def compute(self, image, kps):
        if image is None:
            print("Not a valid image")
            raise TypeError

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        kps, des = cv2.SIFT().compute(gray_image, kps)
        return kps, des



# Resize the shorter dimension to 'new_size'
# while maintaining the aspect ratio
def resize_to_size(input_image):
    h, w = input_image.shape[0], input_image.shape[1]

    ds_factor = _NEW_SIZE / float(h)
    if w < h:
        ds_factor = _NEW_SIZE / float(w)
    tmp = (int(w * ds_factor), int(h * ds_factor))
    return cv2.resize(input_image, tmp)


if __name__ == '__main__':
    args = build_arg_parser().parse_args()

    input_map = []
    for cls in args.cls:
        assert len(cls) >= 2, "Format for classes is `<label> file`"
        label = cls[0]
        input_map += load_input_map(label, cls[1])
    
    _NEW_SIZE = args.scale

    # Building the codebook
    print("===== Building codebook =====")
    kmeans, centroids = FeatureExtractor().get_centroids(input_map)
    if args.codebook_file:
        with open(args.codebook_file, 'wb') as f:
            pickle.dump((kmeans, centroids), f)

    # Input data and labels
    print("===== Building feature map =====")
    feature_map = extract_feature_map(input_map, kmeans, centroids)
    if args.feature_map_file:
        with open(args.feature_map_file, 'wb') as f:
            pickle.dump(feature_map, f)
