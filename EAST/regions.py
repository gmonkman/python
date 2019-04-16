#pylint: skip-file
'''Produce rext region proposals using tensorflow, saving the
detection to a pickled numpy array per image and optionally
showing the detections on a new image, saved in folder output_dir.

Non-maximum suppression can be optionaly applied.
'''
from warnings import warn as _warn
from enum import Enum as _enum
import os as _os
from os import path as _path


import cv2 as _cv2
import tensorflow as _tf
import numpy as _np

import funclib.iolib as _iolib
from funclib.iolib import PrintProgress as _PrintProgress
import funclib.baselib as _baselib
from funclib.stopwatch import StopWatch as _StopWatch

from opencvlib import geom as _geom
import opencvlib.view as _view
import opencvlib.roi as _roi
from opencvlib.imgpipes.generators import FromPaths as _ImgGenerator
import EAST as _EAST
import EAST.model as _model
import EAST.icdar as _icdar




class _ProgressStatus():
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

    #print('Initialising ProgressStatus...')

    class eProgressStatus(_enum):
        '''progress status'''
        NotProcessed = 0
        Errored = 1
        Success = 2


    class eListIndex(_enum):
        '''list index for progressstatus list'''
        img_path = 0
        status = 1
        error = 2

    try:
        _progress_status_file_path = _path.normpath(_EAST.ini.Regions_py.PROGRESS_STATUS_FILE)

        if _iolib.file_exists(_progress_status_file_path):
            _progress_status = _baselib.unpickle(_progress_status_file_path)
        else:
            _progress_status = []
    except Exception as e:
        _warn('Failed to load status file %s' % _progress_status_file_path)


    def __init__(self, **kwargs):
        raise Exception('Class use does not require an instance')


    @staticmethod
    def save():
        '''pickle progress'''
        _baselib.pickle(_ProgressStatus._progress_status, _ProgressStatus._progress_status_file_path)


    @staticmethod
    def get_file_status(img_path):
        '''test if a specific image was processed'''
        files = [f[_ProgressStatus.eListIndex.img_path.value] for f in _ProgressStatus._progress_status]
        if _path.normpath(img_path) in files:
            return _ProgressStatus.eProgressStatus(_ProgressStatus._progress_status[files.index(img_path)][_ProgressStatus.eListIndex.status.value])
        return _ProgressStatus.eProgressStatus.NotProcessed


    @staticmethod
    def status_add(img_path, status=eProgressStatus.Success, err='', ignore_item_exists=True, save_=True):
        '''record image file as processed'''
        img_path = _path.normpath(img_path)
        if _ProgressStatus.get_file_status(img_path) == _ProgressStatus.eProgressStatus.NotProcessed:
            _ProgressStatus._progress_status.append([img_path, _ProgressStatus.eProgressStatus.Success.value, err])
            if save_:
                _ProgressStatus.save()
        else:
            if ignore_item_exists:
                pass
            else:
                raise ValueError('Image "%s" is already in the processed list' % img_path)

    @staticmethod
    def status_edit(img_path, status=eProgressStatus.Success, err='', ignore_no_item=True):
        '''record image file as processed'''
        img_path = _path.normpath(img_path)
        files = [f[_ProgressStatus.eListIndex.img_path.value] for f in _ProgressStatus._progress_status]

        if ignore_no_item:
            try:
                i = files.index(img_path)
            except ValueError as _:
                pass
        else:
            i = files.index(img_path)

        files[i] = [img_path, status.value, err]


    @staticmethod
    def status_del(img_path, ignore_no_item=True):
        '''delete a status'''
        img_path = _path.normpath(img_path)
        files = [f[_ProgressStatus.eListIndex.img_path.value] for f in _ProgressStatus._progress_status]
        if ignore_no_item:
            try:
                i = files.index(img_path)
            except ValueError as _:
                pass
        else:
            i = files.index(img_path)
        del _ProgressStatus._progress_status[i]



def _detect(score_map, geo_map, score_map_thresh=0.8, box_thresh=0.1, nms_thres=0.2):
    '''detect'''
    if len(score_map.shape) == 4:
        score_map = score_map[0, :, :, 0]
        geo_map = geo_map[0, :, :, ]

    # filter the score map
    xy_text = _np.argwhere(score_map > score_map_thresh)

    # sort the text boxes via the y axis
    xy_text = xy_text[_np.argsort(xy_text[:, 0])]

    # restore
    text_box_restored = _icdar.restore_rectangle(xy_text[:, ::-1]*4, geo_map[xy_text[:, 0], xy_text[:, 1], :]) # N*4*2
    boxes = _np.zeros((text_box_restored.shape[0], 9), dtype=_np.float32)
    boxes[:, :8] = text_box_restored.reshape((-1, 8)) #each boxes row is a length 8 box of coord pairs in order topleft, topright, bottomright, bottomleft - final col is confidence scores.
    boxes[:, 8] = score_map[xy_text[:, 0], xy_text[:, 1]]

    #DO NMS
    if  _EAST.ini.Regions_py.NMS_MODE == 'simple':
        raise NotImplementedError('Simple nms mode code triggers pylint bug. Not implemented.')
        #TODO Statement below causes pylint to fail. Debug and change to single reshape statement
        #boxes_for_rosebrook_nms = boxes([0, 0, 0, 0, 0], [0, 1, 4, 5, 8])
        #boxes_for_rosebrook_nms = numpy.vstack((boxes[:, 0], boxes[:, 1], boxes[:, 4], boxes[:, 5], boxes[:, 8])) #boxes_for_rosebrook_nms will be n,1,2
        #boxes_for_rosebrook_nms = boxes.T
        #boxes_for_rosebrook_nms = nms.nms_fast(boxes_for_rosebrook_nms)

        #now rebuild ndarray in expected format
        #boxes = numpy.vstack((boxes_for_rosebrook_nms[:, 0], boxes_for_rosebrook_nms[:, 1],
            #               boxes_for_rosebrook_nms[:, 2], boxes_for_rosebrook_nms[:, 1],
           #                boxes_for_rosebrook_nms[:, 2], boxes_for_rosebrook_nms[:, 3],
          #                 boxes_for_rosebrook_nms[:, 0], boxes_for_rosebrook_nms[:, 3], boxes_for_rosebrook_nms[:, 4]))
        #boxes = boxes_for_rosebrook_nms
    elif _EAST.ini.Regions_py.NMS_MODE == 'pylanms':
        #boxes = locality_aware_nms.nms_locality(boxes.astype(_np.float64), nms_thres)
        raise NotImplementedError
    elif _EAST.ini.Regions_py.NMS_MODE == 'cpplanms':
        raise NotImplementedError
        #boxes = lanms.merge_quadrangle_n9(boxes.astype('float32'), nms_thres)

    if boxes.shape[0] == 0:
        return None

    # here we filter some low score boxes by the average score map, this is different from the orginal paper
    for i, box in enumerate(boxes):
        mask = _np.zeros_like(score_map, dtype=_np.uint8)
        _cv2.fillPoly(mask, box[:8].reshape((-1, 4, 2)).astype(_np.int32) // 4, 1)
        boxes[i, 8] = _cv2.mean(score_map, mask)[0]

    boxes = boxes[boxes[:, 8] > box_thresh]

    return boxes




def text_region_generator(images_path, visualisation_dir=None):
    '''(str, str) -> ndarray, n,2-list, str, str
    Do the region detection in a jpg image.

    Parameters:
    images_path: path to the images
    visualisation_dir:save a visualisation of the detected text regions to this dir

    Yields:
        ndarray, i.e.the image cropped to a detected text region,
        Detected region as a rectangle in cv2 points format,
        The path to the image
        A key which groups regions considered to be from the same body of text,


    Example:
    >>>detect_image('C:/temp/images', 'C:/temp/images/vis')
    array([[[..]]]), [[10,0], ...], 'C:/temp/images/IMAGE1.JPG', 'C1'
    '''

    if visualisation_dir:
        visualisation_dir = _path.normpath(visualisation_dir)
        try:
            _os.makedirs(visualisation_dir)
        except OSError as e:
            if e.errno != 17:
                raise

    with _tf.get_default_graph().as_default():
        input_images = _tf.placeholder(_tf.float32, shape=[None, None, None, 3], name='input_images')
        global_step = _tf.get_variable('global_step', [], initializer=_tf.constant_initializer(0), trainable=False)

        f_score, f_geometry = _model.model(input_images, is_training=False)

        variable_averages = _tf.train.ExponentialMovingAverage(0.997, global_step)
        saver = _tf.train.Saver(variable_averages.variables_to_restore())

        with _tf.Session(config=_tf.ConfigProto(allow_soft_placement=True)) as sess:
            ckpt_state = _tf.train.get_checkpoint_state(_EAST.ini.Regions_py.CHECKPOINT_PATH)
            model_path = _os.path.join(_EAST.ini.Regions_py.CHECKPOINT_PATH, _os.path.basename(ckpt_state.model_checkpoint_path))
            #print('Restore from {}'.format(model_path))
            saver.restore(sess, model_path)

            Gen = _ImgGenerator(images_path)
            im_fn_list = [f[1] for f in Gen.generate(pathonly=True)]

            PP1 = _PrintProgress(len(im_fn_list), 20, 'Outer images progress...')
            SW = _StopWatch(event_name='Process Single Image', qsize=20)

            for n, im_fn in enumerate(im_fn_list):
                #have we processed it before
                im_fn = _os.path.normpath(im_fn)
                fs = _ProgressStatus.get_file_status(im_fn)

                if fs == _ProgressStatus.eProgressStatus.Success:
                    SW.lap()
                    PP1.increment(suffix='Remain: %s' % SW.pretty_remaining(len(im_fn_list) - n))
                    continue

                if fs == _ProgressStatus.eProgressStatus.Errored:
                    if _EAST.ini.Regions_py.RETRY_FAILED == 0:
                        SW.lap()
                        PP1.increment(suffix='Remain: %s' % SW.pretty_remaining(len(im_fn_list) - n))
                        continue
                    _ProgressStatus.status_del(im_fn) #remove from ProgressStatus list and retry this image

                im = _cv2.imread(im_fn); img_orig = _np.copy(im) #store orig image as img as we will write detections in im
                h, w, _ = im.shape
                im = im[:, :, ::-1]
                im_resized, (ratio_h, ratio_w) = _resize_image(im) #multiple of 32 px for network

                score, geometry = sess.run([f_score, f_geometry], feed_dict={input_images: [im_resized]})
                boxes = _detect(score_map=score, geo_map=geometry)

                #read all detectionss
                if not boxes is None:
                    boxes = boxes[:, :8].reshape((-1, 4, 2))  #to .shape = n, 4, 2
                    boxes[:, :, 0] /= ratio_w
                    boxes[:, :, 1] /= ratio_h

                    PP2 = _PrintProgress(len(boxes), bar_length=20, init_msg='Processing box detections ...')

                    for i, box in enumerate(boxes): #box.shape = (4, 2)
                        # to avoid submitting errors
                        box = _sort_poly(box.astype(_np.int32)) #order points in cv2 drawing order
                        if _np.linalg.norm(box[0] - box[1]) < 5 or _np.linalg.norm(box[3]-box[0]) < 5:
                            PP2.increment()
                            continue

                        box_cluster = _np.array((box[0, 0]/w, box[0, 1]/h, box[2, 0]/w, box[2, 1]/h, box[2, 1]/h - box[0, 1]/h)) #format is x1, y1, x2, y2, y2-y1
                        height = box[2, 1]/h - box[0, 1]/h
                        centroid = _geom.centroid(box)
                        if i == 0:
                            heights = [height]
                            centroids = [centroid]
                            boxes_cluster = box_cluster.copy()
                            boxes_untransformed = _np.expand_dims(_np.array(box[0:8]), 0)
                        else:
                            heights.append(height)
                            centroids.append(centroid)
                            boxes_cluster = _np.vstack((boxes_cluster, box_cluster))
                            boxes_untransformed = _np.concatenate((boxes_untransformed, _np.expand_dims(_np.array(box[0:8]), 0)))

                        PP2.increment()

                    centroids = _np.array(centroids) #n,2 numpy array of points

                    mask, contours, _ = _roi.polys_to_mask(im, boxes_untransformed, use_bounding_rect=True) #make a mask out of every word detection
                    mask = _roi.mask_join(mask, _get_dilate_kernel(mask), _EAST.ini.Regions_py.MASK_JOIN_ITER) #join nearby word detection masks using dilation
                    contours, _ = _cv2.findContours(mask, _cv2.RETR_CCOMP, _cv2.CHAIN_APPROX_SIMPLE) #reget the contours after merging
                    contours = _roi.contours_to_bounding_rects(contours) #make contours rectangles
                    contours_as_pts = [_roi.contour_to_cvpts(c) for c in contours]
                    mask, contours, _ = _roi.polys_to_mask(im, contours_as_pts, use_bounding_rect=False) #make a new mask from the rectangular contours we just made

                    #build average heights as an extra cluster dimension
                    mean_cluster_box_heights = []
                    heights = _np.array(heights)
                    for c in contours:
                        pt = _roi.rect_xy_to_tlbr(_roi.contour_to_cvpts(c))
                        tl = _np.array(pt[0]); br = _np.array(pt[1])
                        inidx = _np.all(_np.logical_and(tl <= centroids, centroids <= br), axis=1)
                        mean_cluster_box_heights.append([_np.mean(heights[inidx])])

                    #add width as an additional similarity dimension
                    #on the basis that areas of similiar width are likely to
                    #be the same text body in multi column documents
                    for i, c in enumerate(contours):
                        _, _, _, w = _roi.rect_as_rchw(_roi.contour_to_cvpts(c))
                        mean_cluster_box_heights[i].append(w / img_orig.shape[1]) #just tack the width onto the end of each mean_cluster_box_height of each contour

                    contour_clusters, _ = _roi.contours_cluster_by_histo(img_orig, contours, thresh=_EAST.ini.Regions_py.COSINE_DISTANCE_THRESH, additional_obs=mean_cluster_box_heights) #dic {'C1':[cont,cont, ..], 'C2':[cont,cont, ..], ...}, clusterng contours by there RGB histo

                    #Now identify outliers by distance - we put these in their own group and update the contours with the inliers
                    all_outliers = []
                    for key, items in contour_clusters.items(): #if we have 2 contours which are appart, they are both moved to outliers - doesnt really matter
                        if key == 'OUTLIERS': continue
                        inliers, outliers, _ = _roi.contour_cluster_outliers(items, thresh=_EAST.ini.Regions_py.MIN_OUTLIER_DISTANCE_THRESH, plane_size=img_orig.shape)
                        contour_clusters[key] = inliers
                        if outliers:
                            all_outliers.extend(outliers)

                    outlier_cnt = 1
                    for o in all_outliers:
                        contour_clusters['OUTLIERS%s' % outlier_cnt] = [o]
                        outlier_cnt += 1

                    #Export the visualisation if we have asked for it
                    if visualisation_dir:
                        try: #dont halt everything if the visualisation fails
                            viskeys = []; visclusters = []
                            for i, (k, cnts) in enumerate(contour_clusters.items()):
                                for c in cnts:
                                    if isinstance(c, _np.ndarray):
                                        viskeys.append(k)
                                        visclusters.append(c)

                            if visclusters:
                                _iolib.create_folder(visualisation_dir)
                                visimg = _view.contours_show(img_orig, visclusters, viskeys, show_=False)
                                vis_fn = '%s/%s_vis.jpg' % (visualisation_dir, _iolib.get_file_parts(im_fn)[1])
                                _cv2.imwrite(vis_fn, visimg)
                        except Exception as e:
                            pass

                    for key, clusters in contour_clusters.items():
                        if clusters:
                            img_cropped, _, pts_xt = _roi.crop_from_rects(img_orig, clusters, mask_with_boundary_pixels=True)
                            img_cropped = _view.pad_image(img_cropped, (_EAST.ini.Regions_py.PAD_CONTOURS, _EAST.ini.Regions_py.PAD_CONTOURS), pad_mode=_view.ePadColorMode.border)
                            yield img_cropped, pts_xt, im_fn, key
                    _ProgressStatus.status_add(im_fn, _ProgressStatus.eProgressStatus.Success)
                else:
                    _ProgressStatus.status_add(im_fn, _ProgressStatus.eProgressStatus.Success, err='No words detected')

                SW.lap()
                PP1.increment(suffix='Remain: %s' % SW.pretty_remaining(len(im_fn_list) - n))
                _ProgressStatus.save()








#Helper Functions
def _get_dilate_kernel(img):
    '''get kernels size to
    try and merge contours'''
    #this was based on manually checking results on
    #a 700x700 image and taking the "good" kernel ratio
    #which was (5,5)
    r = float(_EAST.ini.Regions_py.MASK_MERGE_KERNEL_RATIO)
    return (int(r * img.shape[0]), int(r * img.shape[0]))



def _resize_image(im, max_side_len=2400):
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
    im = _cv2.resize(im, (int(resize_w), int(resize_h)))

    ratio_h = resize_h / float(h)
    ratio_w = resize_w / float(w)

    return im, (ratio_h, ratio_w)


def _sort_poly(p):
    '''order points in cv2 drawing order'''
    min_axis = _np.argmin(_np.sum(p, axis=1))
    p = p[[min_axis, (min_axis+1)%4, (min_axis+2)%4, (min_axis+3)%4]]
    if abs(p[0, 0] - p[1, 0]) > abs(p[0, 1] - p[1, 1]):
        return p
    return p[[0, 3, 2, 1]]
