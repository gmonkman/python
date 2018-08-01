#This was the jupyter notebook object_detection_tutorial.ipynb
# When come to export to the spreadsheet
#check this script, point_px_bass_processors.py
#THIS IS THE ONE I ACTUALLY USE TO DO THE DETECTIONS

'''Detect bass in images.

Example:
tf_obj_det.py -x -p shore -c fujifilm /
    "C:/images/vgg_body-caudal.json" /
    "C:/model/frozen_inference_graph.pb" /
    "C:/label_map.pbtxt"
'''
import numpy as np
import tensorflow as tf
import os.path as path
import argparse
import random

import cv2

from object_detection.utils import ops as utils_ops
#from object_detection.utils import label_map_util
#from object_detection.utils import visualization_utils as vis_util

from opencvlib import aruco
from funclib import iolib
from opencvlib.view import show
from opencvlib.imgpipes import vgg
from opencvlib.distance import nearestN_euclidean
from opencvlib import roi
from opencvlib import common
from opencvlib import transforms
from opencvlib import geom

VALID_CAMERAS = ['gopro', 'samsung', 'fujifilm']
VALID_PLATFORMS = ['shore', 'charter']

#this is calculated in scripts_vgg\calc_lw.py
BASS_LENGTH_DEPTH_RATIO = 4.319593022146387

def run_inference_for_single_image(image, graph):
    '''(ndarray, tensorflow.graph)
    '''
    with graph.as_default():
        with tf.Session() as sess:
            # Get handles to input and output tensors
            ops = tf.get_default_graph().get_operations()
            all_tensor_names = {output.name for op in ops for output in op.outputs}
            tensor_dict = {}
            for key in ['num_detections', 'detection_boxes', 'detection_scores', 'detection_classes', 'detection_masks']:
                tensor_name = key + ':0'
                if tensor_name in all_tensor_names:
                    tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)

            if 'detection_masks' in tensor_dict:
                # The following processing is only for single image
                detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
                detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
                # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(detection_masks, detection_boxes, image.shape[0], image.shape[1])
                detection_masks_reframed = tf.cast(tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                # Follow the convention by adding back the batch dimension
                tensor_dict['detection_masks'] = tf.expand_dims(detection_masks_reframed, 0)
            image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

            output_dict = sess.run(tensor_dict, feed_dict={image_tensor: np.expand_dims(image, 0)})

            # all outputs are float32 numpy arrays, so convert types as appropriate
            output_dict['num_detections'] = int(output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.uint8)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]
            if 'detection_masks' in output_dict:
                output_dict['detection_masks'] = output_dict['detection_masks'][0]
    return output_dict


def get_log_level(level):
    '''(str) -> int

    Returns int from tf.logging
    '''
    r = tf.logging.INFO
    if isinstance(level, str):
        level = level.lower()
        if level == "debug":
            r = tf.logging.DEBUG
        elif level == "info":
            r = tf.logging.INFO
        elif level == "warn":
            r = tf.logging.WARN
        elif level == "error":
            r = tf.logging.ERROR
        elif level == "fatal":
            r = tf.logging.FATAL
    return r


def get_samplelengthid(platform, camera, filename):
    '''(str, str, str) -> int
    Get the sample_lengthid from textual key.
    Ultimately to patch MV length estimates
    into the excel speadsheet sample_length.mv_lens_correction_mm

    Args:
        platform: in ['shore', 'charter']
        camera: in ['fujifilm', 'samsung', 'gopro']
        filename: the filename (only) of the image. e.g. 123_UND.jpg

    Returns:
        The sample_lengthid
    '''
    #these two lists match by index
    sample_lengthids = [212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524]
    keys = ['charter_fujifilm_444', 'charter_fujifilm_482a', 'charter_fujifilm_542', 'charter_fujifilm_375', 'charter_fujifilm_478', 'charter_fujifilm_441', 'charter_fujifilm_469', 'charter_fujifilm_458', 'charter_fujifilm_565', 'charter_fujifilm_472', 'charter_fujifilm_468a', 'charter_fujifilm_497', 'charter_fujifilm_427', 'charter_fujifilm_433', 'charter_fujifilm_409a', 'charter_fujifilm_361', 'charter_fujifilm_598', 'charter_fujifilm_424', 'charter_fujifilm_405', 'charter_fujifilm_572', 'charter_fujifilm_454', 'charter_fujifilm_430', 'charter_fujifilm_358', 'charter_fujifilm_425', 'charter_fujifilm_527', 'charter_fujifilm_394', 'charter_fujifilm_519', 'charter_fujifilm_421', 'charter_fujifilm_573', 'charter_fujifilm_501', 'charter_fujifilm_482', 'charter_fujifilm_520', 'charter_fujifilm_551', 'charter_fujifilm_459', 'charter_fujifilm_510', 'charter_fujifilm_510a', 'charter_fujifilm_533', 'charter_fujifilm_509', 'charter_fujifilm_583', 'charter_fujifilm_497a', 'charter_fujifilm_468', 'charter_fujifilm_481', 'charter_fujifilm_374', 'charter_fujifilm_595', 'charter_fujifilm_409', 'charter_gopro_472', 'charter_gopro_510a', 'charter_gopro_510', 'charter_gopro_583', 'charter_gopro_454', 'charter_gopro_510b', 'charter_gopro_551', 'charter_gopro_591', 'charter_gopro_526', 'charter_gopro_421', 'charter_gopro_496', 'charter_gopro_509', 'charter_gopro_374', 'charter_gopro_409a', 'charter_gopro_572', 'charter_gopro_358', 'charter_gopro_478', 'charter_gopro_459', 'charter_gopro_565', 'charter_gopro_433', 'charter_gopro_394', 'charter_gopro_598', 'charter_gopro_595', 'charter_gopro_375', 'charter_gopro_458', 'charter_gopro_424', 'charter_gopro_527', 'charter_gopro_444', 'charter_gopro_542', 'charter_gopro_441a', 'charter_gopro_427', 'charter_gopro_409', 'charter_gopro_482a', 'charter_gopro_441', 'charter_gopro_448', 'charter_gopro_442', 'charter_gopro_468a', 'charter_gopro_523a', 'charter_gopro_361', 'charter_gopro_519', 'charter_gopro_430', 'charter_gopro_405', 'charter_gopro_425', 'charter_gopro_523', 'charter_gopro_501', 'charter_gopro_468', 'charter_gopro_497', 'charter_gopro_481', 'charter_gopro_497a', 'charter_samsung_433', 'charter_samsung_458', 'charter_samsung_496', 'charter_samsung_459', 'charter_samsung_444', 'charter_samsung_509', 'charter_samsung_598', 'charter_samsung_573', 'charter_samsung_481', 'charter_samsung_533', 'charter_samsung_454', 'charter_samsung_588', 'charter_samsung_375', 'charter_samsung_482', 'charter_samsung_425', 'charter_samsung_591', 'charter_samsung_430a', 'charter_samsung_478', 'charter_samsung_572', 'charter_samsung_497', 'charter_samsung_394', 'charter_samsung_468a', 'charter_samsung_424', 'charter_samsung_501', 'charter_samsung_510', 'charter_samsung_472', 'charter_samsung_483', 'charter_samsung_421', 'charter_samsung_448', 'charter_samsung_374', 'charter_samsung_358', 'charter_samsung_498', 'charter_samsung_442', 'charter_samsung_542', 'charter_samsung_468', 'charter_samsung_565', 'charter_samsung_583', 'charter_samsung_409', 'charter_samsung_469', 'charter_samsung_510b', 'charter_samsung_409a', 'charter_samsung_405', 'charter_samsung_510a', 'charter_samsung_595', 'charter_samsung_527', 'charter_samsung_523', 'charter_samsung_361', 'charter_samsung_441', 'charter_samsung_551', 'shore_fujifilm_279_2', 'shore_fujifilm_346', 'shore_fujifilm_294', 'shore_fujifilm_325', 'shore_fujifilm_343', 'shore_fujifilm_344', 'shore_fujifilm_309', 'shore_fujifilm_301', 'shore_fujifilm_330', 'shore_fujifilm_537', 'shore_fujifilm_420', 'shore_fujifilm_498', 'shore_fujifilm_339', 'shore_fujifilm_298', 'shore_fujifilm_363', 'shore_fujifilm_319', 'shore_fujifilm_419', 'shore_fujifilm_406', 'shore_fujifilm_618', 'shore_fujifilm_413', 'shore_fujifilm_295_2', 'shore_fujifilm_308', 'shore_fujifilm_285', 'shore_fujifilm_329', 'shore_fujifilm_326', 'shore_fujifilm_520', 'shore_fujifilm_589', 'shore_fujifilm_370', 'shore_fujifilm_381', 'shore_fujifilm_234', 'shore_fujifilm_434', 'shore_fujifilm_448', 'shore_fujifilm_316', 'shore_fujifilm_353', 'shore_fujifilm_364', 'shore_fujifilm_276', 'shore_fujifilm_322_2', 'shore_fujifilm_411', 'shore_fujifilm_292', 'shore_fujifilm_341', 'shore_fujifilm_341_2', 'shore_fujifilm_311', 'shore_fujifilm_404', 'shore_fujifilm_295', 'shore_fujifilm_296', 'shore_fujifilm_503', 'shore_fujifilm_338', 'shore_fujifilm_258', 'shore_fujifilm_555', 'shore_fujifilm_403', 'shore_fujifilm_322', 'shore_gopro_294', 'shore_gopro_589', 'shore_gopro_520', 'shore_gopro_403', 'shore_gopro_555', 'shore_gopro_296', 'shore_gopro_316', 'shore_gopro_381', 'shore_gopro_322_2', 'shore_gopro_339', 'shore_gopro_404', 'shore_gopro_591', 'shore_gopro_285', 'shore_gopro_344', 'shore_gopro_330', 'shore_gopro_295_2', 'shore_gopro_353', 'shore_gopro_292', 'shore_gopro_329_2', 'shore_gopro_338', 'shore_gopro_370', 'shore_gopro_537', 'shore_gopro_346', 'shore_gopro_364', 'shore_gopro_448', 'shore_gopro_326', 'shore_gopro_503', 'shore_gopro_295', 'shore_gopro_413', 'shore_gopro_322', 'shore_gopro_588', 'shore_gopro_341', 'shore_gopro_325', 'shore_gopro_301', 'shore_gopro_319', 'shore_gopro_311', 'shore_gopro_308', 'shore_gopro_434', 'shore_gopro_279_2', 'shore_gopro_498', 'shore_gopro_411', 'shore_gopro_234', 'shore_gopro_309', 'shore_gopro_303', 'shore_gopro_406', 'shore_gopro_354', 'shore_gopro_341_2', 'shore_gopro_279', 'shore_gopro_420', 'shore_gopro_329', 'shore_gopro_600', 'shore_gopro_602', 'shore_gopro_419', 'shore_gopro_343', 'shore_gopro_363', 'shore_gopro_548', 'shore_gopro_382', 'shore_samsung_279', 'shore_samsung_618', 'shore_samsung_498', 'shore_samsung_602', 'shore_samsung_353', 'shore_samsung_419', 'shore_samsung_296', 'shore_samsung_363', 'shore_samsung_292', 'shore_samsung_322', 'shore_samsung_413', 'shore_samsung_329', 'shore_samsung_295_2', 'shore_samsung_338', 'shore_samsung_343', 'shore_samsung_600', 'shore_samsung_339', 'shore_samsung_301', 'shore_samsung_276', 'shore_samsung_262', 'shore_samsung_370', 'shore_samsung_322_2', 'shore_samsung_329_2', 'shore_samsung_434', 'shore_samsung_354', 'shore_samsung_234', 'shore_samsung_344', 'shore_samsung_319', 'shore_samsung_411', 'shore_samsung_364', 'shore_samsung_381', 'shore_samsung_294', 'shore_samsung_448', 'shore_samsung_341_2', 'shore_samsung_309', 'shore_samsung_298', 'shore_samsung_326', 'shore_samsung_308', 'shore_samsung_346', 'shore_samsung_520', 'shore_samsung_403', 'shore_samsung_432', 'shore_samsung_537', 'shore_samsung_404', 'shore_samsung_316', 'shore_samsung_311', 'shore_samsung_295', 'shore_samsung_330', 'shore_samsung_279_2', 'shore_samsung_285', 'shore_samsung_325', 'shore_samsung_406', 'shore_samsung_303', 'shore_samsung_341', 'shore_fujifilm_303', 'shore_fujifilm_279', 'shore_fujifilm_290', 'shore_fujifilm_329_2', 'shore_fujifilm_354', 'shore_fujifilm_548', 'shore_fujifilm_298', 'shore_fujifilm_582', 'shore_gopro_582']
    filename = filename.replace('_FISHUND', '')
    filename = filename.replace('_UND', '')
    filename = filename.replace('r', '')
    filename = filename.replace('.jpg', '')
    filename = filename.replace('.JPG', '')
    key = '%s_%s_%s' % (platform.lower(), camera.lower(), filename)
    ind = keys.index(key)
    return int(sample_lengthids[ind])


def detect(img, imgpath, sample_lengthid, all_points_x, all_points_y, detection_graph, results, errs, platform, camera, transform='None', rotation=0):
    '''(str, str, int, n-list, n-list, tf.Graph, list, list, str) -> n,2-list|None

    Get the detection stats as a list to write to a file.

    results, errs: status lists, ByRef
    transform: string indicating any transform to the image, eg. "hflip", "none"
    Returns:
        detection points on success, else None
    '''
    h = img.shape[0]; w = img.shape[1]
    _, imgname, _ = iolib.get_file_parts2(imgpath)
    groundtruth_xmin = min(all_points_x) / w; groundtruth_xmax = max(all_points_x) / w
    groundtruth_ymin = min(all_points_y) / h; groundtruth_ymax = max(all_points_y) / h

    try:
        output_dict = run_inference_for_single_image(img, detection_graph) # Actual detection.
    except Exception as e:
        errs.append(['Tensorflow error on image %s. Error was %s' % (str(e), imgname)])
        return None

    ymin, xmin, ymax, xmax = output_dict['detection_boxes'][0].tolist() #[0.4146363139152527, 0.3671582341194153, 0.525425910949707, 0.770221471786499] ymin, xmin, ymax, xmax
    detection_pts = roi.points_denormalize([[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]], h, w, asint=True)
    score = float(output_dict['detection_scores'][0]) #0.99999
    detection_box_centroid = roi.centroid(detection_pts)

    #get marker
    D = aruco.Detected(img)
    D.detect()
    marker_centroids = []
    #we my have many markers
    if D.Markers:
        for M in D.Markers:
            assert isinstance(M, aruco.Marker)
            marker_centroids.append(M.centroid)
        ind, _ = nearestN_euclidean(detection_box_centroid, marker_centroids)[0]
        marker = D.Markers[ind]
        assert isinstance(marker, aruco.Marker)
    else:
        errs.append(['No marker found for image %s' % imgname])
        return None

    length_est = abs((detection_pts[1][0] - detection_pts[0][0])) * marker.px_length_mm()
    if rotation != 0:
        a, b, _ = geom.rect_inner_side_length(detection_pts, BASS_LENGTH_DEPTH_RATIO)
        length_est_rotation_adjust = max(a, b) * marker.px_length_mm()
    else:
        length_est_rotation_adjust = length_est

    results.append([sample_lengthid, imgname, w, h, groundtruth_xmin, groundtruth_xmax, groundtruth_ymin, groundtruth_ymax, xmin, xmax, ymin, ymax, score, length_est, length_est_rotation_adjust, platform, camera, transform, rotation])
    return detection_pts


def write_image(img, groundtruth_pts, detection_pts, fname, show_, detection_label='Detection', groundtruth_label='Groundtruth'):
    '''(ndarray, n2-list, str, bool) -> void
    Save the detection to an image and optionally show it.

    img: ndarray image
    groundtruth_pts: n2-list of points, region.all_points is in the correct format
    fname: the filename to save the detections as
    show_: show the image
    '''
    img_with_groundtruth = common.draw_polygon(img, groundtruth_pts, color=(0, 0, 0), thickness=2)
    img_with_detection = common.draw_polygon(img_with_groundtruth, detection_pts, color=(0, 255, 0), thickness=2)
    gt_all_x, gt_all_y = list(zip(*groundtruth_pts))


    #s = 'Prediction: %.3f' % score
    #common.draw_str(img_with_detection, x=25, y=25, s=s, color=(255, 255, 255), box_background=(0, 0, 0), scale=2, box_pad=10)
    try: #this can fail if not enough room to draw the detection box, but isn't critical
        common.draw_str(img_with_detection, detection_pts[0][0], detection_pts[0][1], s=detection_label, color=(255, 255, 255), box_background=(0, 255, 0), scale=1.5, box_pad=10) #top left
        common.draw_str(img_with_detection, min(gt_all_x), max(gt_all_y), s=groundtruth_label, color=(255, 255, 255), box_background=(0, 0, 0), scale=1.5, box_pad=10) #bottom left
    except Exception as _:
        pass
    cv2.imwrite(fname, img_with_detection)

    if show_:
        show(img_with_detection)



def main():
    '''entry'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('-p', '--platform', help='"charter" or "shore"')
    cmdline.add_argument('-f', '--flip', action='store_true', help='also detect on the horizontally flipped image')
    cmdline.add_argument('-c', '--camera', help='"fujifilm" or "gopro" or "samsung"')
    cmdline.add_argument('-r', '--rotate', type=int, help='Do detections over a range of rotations', default=0)
    #You could also try on rotated images
    cmdline.add_argument('-x', '--export_every', type=int, default=0, help='Export  every [x] images to image subdir "detections"')
    cmdline.add_argument('-s', help='Show detections', action='store_true')
    cmdline.add_argument('-v', '--verbosity', help='Set to DEBUG, INFO, WARN, ERROR, or FATAL', default='ERROR')
    cmdline.add_argument('vgg_file', help='The full vgg file name')
    cmdline.add_argument('pb_file', help='Folder with the graph in it')
    cmdline.add_argument('labels_file', help='The labels proto')
    args = cmdline.parse_args()
    tf.logging.set_verbosity(get_log_level(args.verbosity))
    vgg_file = path.normpath(args.vgg_file)
    pb_file = path.normpath(args.pb_file)
    labels_file = path.normpath(args.labels_file)

    assert iolib.file_exists(vgg_file), 'vgg file %s not found' % vgg_file
    assert iolib.file_exists(pb_file), 'pb file %s not found' % pb_file
    assert iolib.file_exists(labels_file), 'Labels file %s not found' % labels_file
    assert args.platform in VALID_PLATFORMS, 'Platform must be in %s' % str(VALID_PLATFORMS)
    assert args.camera in VALID_CAMERAS, 'Camera must be in %s' % str(VALID_CAMERAS)

    fld, _, _ = iolib.get_file_parts2(vgg_file)
    detections_folder = path.normpath(path.join(fld, 'detections'))
    if iolib.folder_has_files(detections_folder):
        print('Detection folder %s must be empty. Clear it manually.' % detections_folder)
        return
    iolib.create_folder(detections_folder)

    #Check all images in the vgg file (with groundtruths) have a valid bass uniquecode and a vgg record
    i = 0
    PP = iolib.PrintProgressFlash(ticks=None, msg='\nRunning prechecks ... ')
    for imgpath, _, Reg in vgg.roiGenerator(vgg_file, skip_imghdr_check=False, shape_type='rect'):
        PP.update()
        i += 1
        imgpath = path.normpath(imgpath)
        imgfld, imgname, _ = iolib.get_file_parts2(imgpath)
        try:
            sample_lengthid = get_samplelengthid(args.platform, args.camera, imgname)
        except ValueError as dummy:
            raise Exception('Could not get the sample length from the image name. First Check the inifile settings.')
        assert sample_lengthid in list(range(212, 525)), 'sample_lengthid %s was invalid' % sample_lengthid #hardcoded ids

    #load graph
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(pb_file, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    #label_map = label_map_util.load_labelmap(labels_file)
    #categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=1, use_display_name=True)
    #category_index = label_map_util.create_category_index(categories)

    #results are normalized
    results = [['sample_lengthid', 'imgname', 'w', 'h', 'groundtruth_xmin', 'groundtruth_xmax', 'groundtruth_ymin', 'groundtruth_ymax', 'xmin', 'xmax', 'ymin', 'ymax', 'accuracy', 'length_est', 'length_est_rotation_adjust', 'platform', 'camera', 'transform', 'rotation']]
    errs = []

    if args.rotate > 0:
        angles = list(range(-1 * args.rotate, args.rotate + 1, 1))
        angles.remove(0)
        i += i * len(angles)

    PP = iolib.PrintProgress(i, init_msg='\nRunning detections ...')

    for imgpath, _, Reg in vgg.roiGenerator(vgg_file, skip_imghdr_check=False, shape_type='rect'):
        assert isinstance(Reg, vgg.Region)

        PP.increment()

        imgpath = path.normpath(imgpath)
        imgfld, imgname, _ = iolib.get_file_parts2(imgpath)
        sample_lengthid = get_samplelengthid(args.platform, args.camera, imgname) #dont need to check this, we did it before in the pretest
        img = cv2.imread(imgpath)

        if not isinstance(img, np.ndarray):
            continue

        #detect as is
        detection_pts = detect(img, imgpath, sample_lengthid, Reg.all_points_x, Reg.all_points_y, detection_graph, results, errs, args.platform, args.camera, 'None', 0)
        if not detection_pts:
            continue

        if args.export_every > 0:
            #Save and optionally show the detection
            detection_image_name = path.normpath(path.join(detections_folder, imgname))
            write_image(img, Reg.all_points, detection_pts, detection_image_name, args.s)

        #detect when flipped
        if args.flip:
            img_hflip = cv2.flip(img, 1)
            pts_flip = roi.flip_points(Reg.all_points, img.shape[0], img.shape[1], hflip=True)
            pts_flip_x, pts_flip_y = list(zip(*pts_flip))
            detection_pts = detect(img_hflip, imgpath, sample_lengthid, pts_flip_x, pts_flip_y, detection_graph, results, errs, args.platform, args.camera, 'hflip', 0)
            all_points_flip = roi.flip_points(Reg.all_points, img_hflip.shape[0], img_hflip.shape[1], hflip=True)
            if not detection_pts:
                continue

            if args.export_every > 0:
                #Save and optionally show the detection
                detection_image_name = path.normpath(path.join(detections_folder, 'flip_' + imgname))
                write_image(img_hflip, all_points_flip, detection_pts, detection_image_name, args.s)

        if args.rotate > 0:
            for angle in angles:
                PP.increment()
                img_rot, trans = transforms.rotate2(img, angle)
                pts_rot = geom.rotate_points(Reg.all_points, angle, (int(img.shape[1]/2), int(img.shape[0]/2)), translate=trans)
                pts_bound = geom.bounding_rect_of_poly2(pts_rot) #this is the bounding polygon
                pts_rot_x, pts_rot_y = list(zip(*pts_bound))
                xform = 'r_%s' % angle
                detection_pts = detect(img_rot, imgpath, sample_lengthid, pts_rot_x, pts_rot_y, detection_graph, results, errs, args.platform, args.camera, xform, angle)
                if not detection_pts:
                    continue

                if  args.export_every > 0:
                    #Save and optionally show the detection
                    if random.randint(1, args.export_every) == 1:
                        detection_image_name = path.normpath(path.join(detections_folder, xform + '_' + imgname))
                        write_image(img_rot, pts_bound, detection_pts, detection_image_name, args.s, groundtruth_label='Bounding Rotated Groundtruth')



    #export any problems to a csv file
    if errs:
        errfile = path.normpath(path.join(imgfld, 'detection_errs.csv'))
        try:
            iolib.writecsv(errfile, errs, inner_as_rows=False)
        except Exception as _:
            pass

    if results:
        resfile = path.normpath(path.join(imgfld, 'detection.csv'))
        #print('resfile was %s' % resfile)
        try:
           #print('Exporting results. There were %s records in results' % len(results))
            iolib.writecsv(resfile, results, inner_as_rows=False)
        except Exception as _:
            pass
    else:
        print('results dic was empty')

if __name__ == "__main__":
    main()
