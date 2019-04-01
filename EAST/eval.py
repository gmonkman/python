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
import time
import math

import cv2
import numpy as np
import tensorflow as tf

import locality_aware_nms as nms_locality
#import lanms
import model
from icdar import restore_rectangle
from opencvlib  import nms

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


def detect(score_map, geo_map, timer, score_map_thresh=0.8, box_thresh=0.1, nms_thres=0.2):
    '''
    restore text boxes from score map and geo map
    :param score_map:
    :param geo_map:
    :param timer:
    :param score_map_thresh: threshhold for score map
    :param box_thresh: threshhold for boxes
    :param nms_thres: threshold for nms
    :return:
    '''
    if len(score_map.shape) == 4:
        score_map = score_map[0, :, :, 0]
        geo_map = geo_map[0, :, :, ]
    # filter the score map
    xy_text = np.argwhere(score_map > score_map_thresh)
    # sort the text boxes via the y axis
    xy_text = xy_text[np.argsort(xy_text[:, 0])]
    # restore
    start = time.time()
    text_box_restored = restore_rectangle(xy_text[:, ::-1]*4, geo_map[xy_text[:, 0], xy_text[:, 1], :]) # N*4*2
    print('{} text boxes before nms'.format(text_box_restored.shape[0]))
    boxes = np.zeros((text_box_restored.shape[0], 9), dtype=np.float32)
    boxes[:, :8] = text_box_restored.reshape((-1, 8)) #each boxes row is a length 8 box of coord pairs in order topleft, topright, bottomright, bottomleft - final col is confidence scores.
    boxes[:, 8] = score_map[xy_text[:, 0], xy_text[:, 1]]
    timer['restore'] = time.time() - start

    #DO NMS
    start = time.time()
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



    timer['nms'] = time.time() - start

    if boxes.shape[0] == 0:
        return None, timer

    # here we filter some low score boxes by the average score map, this is different from the orginal paper
    for i, box in enumerate(boxes):
        mask = np.zeros_like(score_map, dtype=np.uint8)
        cv2.fillPoly(mask, box[:8].reshape((-1, 4, 2)).astype(np.int32) // 4, 1)
        boxes[i, 8] = cv2.mean(score_map, mask)[0]
    boxes = boxes[boxes[:, 8] > box_thresh]

    return boxes, timer


def sort_poly(p):
    min_axis = np.argmin(np.sum(p, axis=1))
    p = p[[min_axis, (min_axis+1)%4, (min_axis+2)%4, (min_axis+3)%4]]
    if abs(p[0, 0] - p[1, 0]) > abs(p[0, 1] - p[1, 1]):
        return p
    else:
        return p[[0, 3, 2, 1]]


def main():

    cmdline = argparse.ArgumentParser(description=__doc__) #use the module __doc__
    cmdline.add_argument('--checkpoint_path', help='Path to the TF tranined model.', required=True)
    cmdline.add_argument('--images_path', help='Path of images to run detections against.', required=True)
    cmdline.add_argument('--output_dir', help='Path to save detection results.', required=True)
    cmdline.add_argument('--gpu_list', help='List of GPUs to use.', default='0')
    cmdline.add_argument('--text_scale', help='Text scale, used in model', default=512, type=int)
    cmdline.add_argument('-w', '--write_images', help='Write images with detecions', action='store_true')
    cmdline.add_argument('--nms_mode', help='Non-maximum suppression mode. nms_mode in ["none", "simple", "pylanms"]', default='none')
    args = cmdline.parse_args()
    args.nms_mode = args.nms_mode.lower()
    assert args.nms_mode in NMS_MODES, 'Invalid nms_mode %s. nms_mode in %s' % (args.nms_mode, NMS_MODES)

    global FLAGS
    FLAGS.checkpoint_path = os.path.normpath(args.checkpoint_path)
    FLAGS.images_path = os.path.normpath(args.images_path)
    FLAGS.output_dir = os.path.normpath(args.output_dir)
    FLAGS.gpu_list = args.gpu_list
    FLAGS.write_images = args.no_write_images
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
            for im_fn in im_fn_list:
                im = cv2.imread(im_fn)[:, :, ::-1]
                start_time = time.time()
                im_resized, (ratio_h, ratio_w) = resize_image(im)

                timer = {'net': 0, 'restore': 0, 'nms': 0}
                start = time.time()
                score, geometry = sess.run([f_score, f_geometry], feed_dict={input_images: [im_resized]})
                timer['net'] = time.time() - start

                boxes, timer = detect(score_map=score, geo_map=geometry, timer=timer)
                print('{} : net {:.0f}ms, restore {:.0f}ms, nms {:.0f}ms'.format(
                    im_fn, timer['net']*1000, timer['restore']*1000, timer['nms']*1000))

                if boxes is not None: #turn to .shape = n, 4, 2
                    boxes = boxes[:, :8].reshape((-1, 4, 2))
                    boxes[:, :, 0] /= ratio_w
                    boxes[:, :, 1] /= ratio_h

                duration = time.time() - start_time
                print('[timing] {}'.format(duration))

                # save to file
                if not boxes is None:
                    res_file_pickle = os.path.join(FLAGS.output_dir, '{}'.format(os.path.basename(im_fn).split('.')[0]))
                    res_file_text = os.path.join(FLAGS.output_dir, '{}.txt'.format(os.path.basename(im_fn).split('.')[0]))
                    for i, box in enumerate(boxes): #box.shape = (4, 2)
                        # to avoid submitting errors
                        box = sort_poly(box.astype(np.int32))
                        if np.linalg.norm(box[0] - box[1]) < 5 or np.linalg.norm(box[3]-box[0]) < 5:
                            continue

                        box_cv2 = [box.astype(np.int32).reshape((-1, 1, 2))]

                        if i == 0:
                            boxes_out = np.array(box_cv2)
                        else:
                            boxes_out = np.vstack((boxes_out, np.array(box_cv2)))

                        #f.write('{},{},{},{},{},{},{},{}\r\n'.format(box[0, 0], box[0, 1], box[1, 0], box[1, 1], box[2, 0], box[2, 1], box[3, 0], box[3, 1],))
                        if FLAGS.write_images:
                            cv2.polylines(im[:, :, ::-1], box_cv2, True, color=(255, 255, 0), thickness=1)
                    np.save(res_file_pickle, boxes_out)
                else:
                    print('No words detected in %s' % os.path.basename(im_fn))

                if FLAGS.write_images:
                    img_path = os.path.join(FLAGS.output_dir, os.path.basename(im_fn))
                    cv2.imwrite(img_path, im[:, :, ::-1])






if __name__ == "__main__":
    main()

