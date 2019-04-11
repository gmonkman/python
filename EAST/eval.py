# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Produce rext region proposals using tensorflow, saving the
detection to a pickled numpy array per image and optionally
showing the detections on a new image, saved in folder output_dir.

Non-maximum suppression can be optionall applied.

Example:
eval.py
    --images_path=C:/development/python/EAST/test/bin
    --checkpoint_path=C:/development/python/EAST/model/east_icdar2015_resnet_v1_50_rbox
    --output_dir=C:/development/python/EAST/test/bin/detections
    --nms_mode=none
    -w
'''
import os
import argparse
import math
from warnings import warn
from enum import Enum as _enum

import cv2
import numpy as np
import tensorflow as tf
import scipy.ndimage as ndimage

from sklearn.cluster import DBSCAN as _DBSCAN
import opencvlib.view as view
import opencvlib.roi as _roi
#import funclib.arraylib as arraylib

import locality_aware_nms as nms_locality
#import lanms
import model
from icdar import restore_rectangle
from opencvlib  import nms
from opencvlib import roi
from opencvlib import geom
from opencvlib.histo import histo_rgb as _histo_rgb
import opencvlib.view as _view
from opencvlib.view import show
from plotlib.qplot import bar_ as _bar

import funclib.iolib as iolib
from funclib.iolib import PrintProgress
from funclib.baselib import list_most_common as _lmc
import funclib.baselib as _baselib
from funclib.stopwatch import StopWatch
import EAST

os.environ['TF_CPP_MIN_LOG_LEVEL']='2'




class Flags():
    images_path = ''
    gpu_list = '0'
    checkpoint_path =  ''
    output_dir = ''
    write_images = False
    text_scale = 512
    nms_mode = 'none'

FLAGS = Flags()

NMS_MODES = ['none', 'simple', 'pylanms', 'cpplanms']

#'cpplanms' not implemented yet

os.environ['CUDA_VISIBLE_DEVICES'] = FLAGS.gpu_list


class ProgressStatus():
    '''Manages recording of the processing status
    of each individual image on the path. This
    allows continuation in the event of an
    unrecoverable error.

    All methods are static, no need to
    instantiate an instance of the class.

    A single status record is a 3-list:
        list[0] = image path
        list[1] = status (eProgressStatus value)
        list[2] = error message (if relevant)
    '''

    print('Initialising ProgressStatus...')

    class eProgressStatus(_enum):
        NotProcessed = 0
        Errored = 1
        Success = 2


    class eListIndex(_enum):
        img_path = 0
        status = 1
        error = 2

    try:
        _progress_status_file_path = os.path.normpath(EAST.ini.Eval_py.PROGRESS_STATUS_FILE)

        if iolib.file_exists(_progress_status_file_path):
            _progress_status = _baselib.unpickle(_progress_status_file_path)
        else:
            _progress_status = []
    except Exception as e:
        warn('Failed to load status file %s' % _progress_status_file_path)


    def __init__(self, **kwargs):
        raise Exception('Class use does not require an instance')


    @staticmethod
    def save():
        _baselib.pickle(ProgressStatus._progress_status, ProgressStatus._progress_status_file_path)

    @staticmethod
    def get_file_status(img_path):
        '''test if a specific image was processed'''
        files = [f[eListIndex.img_path] for f in ProgressStatus._progress_status]
        if os.path.normpath(img_path) in files:
            return ProgressStatus[files.index(img_path)][ProgressStatus.eListIndex.status.value]
        else:
            return ProgressStatus.eProgressStatus.NotProcessed


    @staticmethod
    def status_add(img_path, status=eProgressStatus.Success, err='', ignore_item_exists=True, save_=True):
        '''record image file as processed'''
        img_path = os.path.normpath(img_path)
        if ProgressStatus.get_file_status(img_path) == ProgressStatus.eProgressStatus.NotProcessed:
            ProgressStatus._progress_status.append([img_path, ProgressStatus.eProgressStatus.Success.value, err])
            if save_:
                ProgressStatus.save()
        else:
            if ignore_item_exists:
                pass
            else:
                raise ValueError('Image "%s" is already in the processed list' % img_path)

    @staticmethod
    def status_edit(img_path, status=eProgressStatus.Success, err='', ignore_no_item=True):
        '''record image file as processed'''
        img_path = os.path.normpath(img_path)
        files = [f[eListIndex.img_path] for f in ProgressStatus._progress_status]

        if ignore_no_item:
            try:
                i = files.index(img_path)
            except ValueError as _:
                pass
        else:
            i = files.index(img_path)

        files[i] = [img_path, status.value, err]


    @staticmethod
    def save():
        _baselib.pickle(_progress_status, ProgressStatus._progress_status_file_path)


    @staticmethod
    def status_del(img_path, ignore_no_item=True):
        img_path = os.path.normpath(img_path)
        files = [f[eListIndex.img_path] for f in ProgressStatus._progress_status]
        if ignore_no_item:
            try:
                i = files.index(img_path)
            except ValueError as _:
                pass
        else:
            i = files.index(img_path)
        del _progress_status[i]




def get_images():
    '''
    find image files in test data path
    :return: list of files found
    '''
    files = []
    exts = ['jpg', 'png', 'jpeg', 'JPG']
    for parent, dirnames, filenames in os.walk(FLAGS.images_path):
        for filename in filenames:
            for ext in exts:
                if filename.endswith(ext):
                    files.append(os.path.join(parent, filename))
                    break
    print('Found {} images'.format(len(files)))
    return files


def resize_image(im, max_side_len=2400):
    '''
    resize image to a size multiple of 32 which is required by the network
    :param im: the resized image
    :param max_side_len: limit of max image size to avoid out of memory in gpu
    :return: the resized image and the resize ratio
    '''
    h, w, _ = im.shape

    resize_w = w
    resize_h = h

    # limit the max side
    if max(resize_h, resize_w) > max_side_len:
        ratio = float(max_side_len) / resize_h if resize_h > resize_w else float(max_side_len) / resize_w
    else:
        ratio = 1.
    resize_h = int(resize_h * ratio)
    resize_w = int(resize_w * ratio)

    resize_h = resize_h if resize_h % 32 == 0 else (resize_h // 32 - 1) * 32
    resize_w = resize_w if resize_w % 32 == 0 else (resize_w // 32 - 1) * 32
    resize_h = max(32, resize_h)
    resize_w = max(32, resize_w)
    im = cv2.resize(im, (int(resize_w), int(resize_h)))

    ratio_h = resize_h / float(h)
    ratio_w = resize_w / float(w)

    return im, (ratio_h, ratio_w)


def detect(score_map, geo_map, score_map_thresh=0.8, box_thresh=0.1, nms_thres=0.2):
    '''detect'''
    if len(score_map.shape) == 4:
        score_map = score_map[0, :, :, 0]
        geo_map = geo_map[0, :, :, ]

    # filter the score map
    xy_text = np.argwhere(score_map > score_map_thresh)

    # sort the text boxes via the y axis
    xy_text = xy_text[np.argsort(xy_text[:, 0])]

    # restore
    text_box_restored = restore_rectangle(xy_text[:, ::-1]*4, geo_map[xy_text[:, 0], xy_text[:, 1], :]) # N*4*2
    print('{} text boxes before nms'.format(text_box_restored.shape[0]))
    boxes = np.zeros((text_box_restored.shape[0], 9), dtype=np.float32)
    boxes[:, :8] = text_box_restored.reshape((-1, 8)) #each boxes row is a length 8 box of coord pairs in order topleft, topright, bottomright, bottomleft - final col is confidence scores.
    boxes[:, 8] = score_map[xy_text[:, 0], xy_text[:, 1]]

    #DO NMS
    if FLAGS.nms_mode == 'simple':
        boxes_for_rosebrook_nms = np.vstack((boxes[:, 0], boxes[:, 1], boxes[:, 4], boxes[:, 5], boxes[:, 8])).T
        boxes_for_rosebrook_nms = nms.nms_fast(boxes_for_rosebrook_nms)

        #now rebuild ndarray in expected format
        boxes = np.vstack((boxes_for_rosebrook_nms[:, 0], boxes_for_rosebrook_nms[:, 1],
                           boxes_for_rosebrook_nms[:, 2], boxes_for_rosebrook_nms[:, 1],
                           boxes_for_rosebrook_nms[:, 2], boxes_for_rosebrook_nms[:, 3],
                           boxes_for_rosebrook_nms[:, 0], boxes_for_rosebrook_nms[:, 3], boxes_for_rosebrook_nms[:, 4])).T
    elif FLAGS.nms_mode == 'pylanms':
        boxes = nms_locality.nms_locality(boxes.astype(np.float64), nms_thres)
    elif FLAGS.nms_mode == 'cpplanms':
        raise NotImplementedError
        #boxes = lanms.merge_quadrangle_n9(boxes.astype('float32'), nms_thres)

    if boxes.shape[0] == 0:
        return None

    # here we filter some low score boxes by the average score map, this is different from the orginal paper
    for i, box in enumerate(boxes):
        mask = np.zeros_like(score_map, dtype=np.uint8)
        cv2.fillPoly(mask, box[:8].reshape((-1, 4, 2)).astype(np.int32) // 4, 1)
        boxes[i, 8] = cv2.mean(score_map, mask)[0]

    boxes = boxes[boxes[:, 8] > box_thresh]

    return boxes


def sort_poly(p):
    '''order points in cv2 drawing order'''
    min_axis = np.argmin(np.sum(p, axis=1))
    p = p[[min_axis, (min_axis+1)%4, (min_axis+2)%4, (min_axis+3)%4]]
    if abs(p[0, 0] - p[1, 0]) > abs(p[0, 1] - p[1, 1]):
        return p
    else:
        return p[[0, 3, 2, 1]]


def main():
    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    cmdline.add_argument('--images_path', help='Path of images to run detections against.', required=True)
    cmdline.add_argument('--output_dir', help='Path to save detection results.', required=True)
    cmdline.add_argument('--gpu_list', help='List of GPUs to use.', default='0')
    cmdline.add_argument('--text_scale', help='Text scale, used in model', default=512, type=int)
    cmdline.add_argument('--nms_mode', help='Non-maximum suppression mode. nms_mode in ["none", "simple", "pylanms"]', default='none')
    args = cmdline.parse_args()
    args.nms_mode = args.nms_mode.lower()
    assert args.nms_mode in NMS_MODES, 'Invalid nms_mode %s. nms_mode in %s' % (args.nms_mode, NMS_MODES)

    global FLAGS
    FLAGS.checkpoint_path = os.path.normpath(EAST.ini.Eval_py.CHECKPOINT_PATH)
    FLAGS.images_path = os.path.normpath(args.images_path)
    FLAGS.output_dir = os.path.normpath(args.output_dir)
    FLAGS.gpu_list = args.gpu_list
    FLAGS.text_scale = args.text_scale
    FLAGS.nms_mode = args.nms_mode
    model.FLAGS = FLAGS

    try:
        os.makedirs(FLAGS.output_dir)
    except OSError as e:
        if e.errno != 17:
            raise

    with tf.get_default_graph().as_default():
        input_images = tf.placeholder(tf.float32, shape=[None, None, None, 3], name='input_images')
        global_step = tf.get_variable('global_step', [], initializer=tf.constant_initializer(0), trainable=False)

        f_score, f_geometry = model.model(input_images, is_training=False)

        variable_averages = tf.train.ExponentialMovingAverage(0.997, global_step)
        saver = tf.train.Saver(variable_averages.variables_to_restore())

        with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:
            ckpt_state = tf.train.get_checkpoint_state(FLAGS.checkpoint_path)
            model_path = os.path.join(FLAGS.checkpoint_path, os.path.basename(ckpt_state.model_checkpoint_path))
            print('Restore from {}'.format(model_path))
            saver.restore(sess, model_path)

            im_fn_list = get_images()
            PP1 = PrintProgress(len(im_fn_list), 20, 'Outer images progress...')
            for im_fn in im_fn_list:
                #have we processed it before
                im_fn = os.path.normpath(im_fn)
                fs = ProgressStatus.get_file_status(im_fn)

                if fs == ProgressStatus.eProgressStatus.Success:
                    PP1.increment()
                    continue

                if fs == ProgressStatus.eProgressStatus.Errored:
                    if EAST.ini.Eval_py.RETRY_FAILED == 0:
                        PP1.increment()
                        continue
                    ProgressStatus.status_del(im_fn) #remove from ProgressStatus list and retry this image

                im = cv2.imread(im_fn); img_orig = np.copy(im) #store orig image as img as we will write detections in im
                h, w, _ = im.shape
                im = im[:, :, ::-1]
                im_resized, (ratio_h, ratio_w) = resize_image(im) #multiple of 32 px for network

                score, geometry = sess.run([f_score, f_geometry], feed_dict={input_images: [im_resized]})
                boxes = detect(score_map=score, geo_map=geometry)

                #read all detectionss
                if not boxes is None:
                    boxes = boxes[:, :8].reshape((-1, 4, 2))  #to .shape = n, 4, 2
                    boxes[:, :, 0] /= ratio_w
                    boxes[:, :, 1] /= ratio_h

                    PP2 = PrintProgress(len(boxes), bar_length=20, init_msg='Processing box detections ...')

                    for i, box in enumerate(boxes): #box.shape = (4, 2)
                        # to avoid submitting errors
                        box = sort_poly(box.astype(np.int32)) #order points in cv2 drawing order
                        if np.linalg.norm(box[0] - box[1]) < 5 or np.linalg.norm(box[3]-box[0]) < 5:
                            PP2.increment()
                            continue

                        box_cluster = np.array((box[0, 0]/w, box[0, 1]/h, box[2, 0]/w, box[2, 1]/h, box[2, 1]/h - box[0, 1]/h)) #format is x1, y1, x2, y2, y2-y1
                        box_for_cluster_untransformed = np.array((box[0, 0], box[0, 1], box[2, 0], box[2, 1], box[2, 1] - box[0, 1])) #format is x1, y1, x2, y2, y2-y1
                        height = box[2, 1]/h - box[0, 1]/h
                        centroid = geom.centroid(box)
                        if i == 0:
                            heights = [height]
                            centroids = [centroid]
                            boxes_cluster = box_cluster.copy()
                            boxes_untransformed = np.expand_dims(np.array(box[0:8]), 0)
                        else:
                            heights.append(height)
                            centroids.append(centroid)
                            boxes_cluster = np.vstack((boxes_cluster, box_cluster))
                            boxes_untransformed = np.concatenate((boxes_untransformed, np.expand_dims(np.array(box[0:8]), 0)))

                        PP2.increment()

                    centroids = np.array(centroids) #n,2 numpy array of points

                    mask, contours, _ = roi.polys_to_mask(im, boxes_untransformed, use_bounding_rect=True) #make a mask out of every word detection
                    mask = roi.mask_join(mask, _get_dilate_kernel(mask), EAST.ini.Eval_py.MASK_JOIN_ITER) #join nearby word detection masks using dilation
                    contours, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE) #reget the contours after merging
                    contours = roi.contours_to_bounding_rects(contours) #make contours rectangles
                    contours_as_pts = [roi.contour_to_cvpts(c) for c in contours]
                    mask, contours, _ = roi.polys_to_mask(im, contours_as_pts, use_bounding_rect=False) #make a new mask from the rectangular contours we just made

                    #build average heights as an extra cluster dimension
                    mean_cluster_box_heights = []
                    heights = np.array(heights)
                    for c in contours:
                        pt = roi.rect_xy_to_tlbr(roi.contour_to_cvpts(c))
                        tl = np.array(pt[0]); br = np.array(pt[1])
                        inidx = np.all(np.logical_and(tl <= centroids, centroids <= br), axis=1)
                        mean_cluster_box_heights.append([np.mean(heights[inidx])])

                    #add width as an additional similarity dimension
                    #on the basis that areas of similiar width are likely to
                    #be the same text body in multi column documents
                    for i, obs in enumerate(mean_cluster_box_heights):
                        _, _, _, w = roi.rect_as_rchw(roi.contour_to_cvpts(c))
                        mean_cluster_box_heights[i].append(w / img_orig.shape[1])

                    contour_clusters, contour_groups_list = roi.contours_cluster_by_histo(img_orig, contours, thresh=EAST.ini.Eval_py.COSINE_DISTANCE_THRESH, additional_obs=mean_cluster_box_heights) #dic {'C1':[cont,cont, ..], 'C2':[cont,cont, ..], ...}, clusterng contours by there RGB histo
                    _view.contours_show(img_orig, contours, contour_groups_list)

                    #Now identify outliers by distance - we put these in their own group and update the contours with the inliers
                    all_outliers = []
                    for key, items in contour_clusters.items(): #if we have 2 contours which are appart, they are both moved to outliers - doesnt really matter
                        if key == 'OUTLIERS': continue
                        inliers, outliers, _ = roi.contour_cluster_outliers(items, thresh=EAST.ini.Eval_py.MIN_OUTLIER_DISTANCE_THRESH, plane_size=img_orig.shape)
                        contour_clusters[key] = inliers
                        if outliers:
                            all_outliers.extend(outliers)

                    outlier_cnt = 1
                    for o in all_outliers:
                        contour_clusters['OUTLIERS%s' % outlier_cnt] = [o]
                        outlier_cnt += 1

                    for key, clusters in contour_clusters.items():
                        if clusters:
                            img_cropped, _, pts_xt = _roi.crop_from_rects(img_orig, clusters)

                    ProgressStatus.status_add(im_fn, ProgressStatus.eProgressStatus.Success)
                    PP1.increment()
                else:
                    #print('No words detected in %s' % os.path.basename(im_fn))
                    ProgressStatus.status_add(im_fn, ProgressStatus.eProgressStatus.Success, err='No words detected')
                    PP1.increment()







def _get_dilate_kernel(img):
    '''get kernels size to
    try and merge contours'''
    #this was based on manually checking results on
    #a 700x700 image and taking the "good" kernel ratio
    #which was (5,5)
    r = float(EAST.ini.Eval_py.MASK_MERGE_KERNEL_RATIO)
    return (int(r * img.shape[0]), int(r * img.shape[0]))





if __name__ == "__main__":
    main()

