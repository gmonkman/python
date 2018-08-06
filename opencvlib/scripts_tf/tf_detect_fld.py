#This was the jupyter notebook object_detection_tutorial.ipynb
# When come to export to the spreadsheet
#check this script, point_px_bass_processors.py

#tf_obj_det.py is used for my detection at the moment
'''Detect bass in images on the file system.

Example:
tf_detect_fld.py -x -s -v INFO "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/negs_tf" "C:/tf/pretrained/bass/ssdlite_mobilenet_v2/run2/frozen_inference_graph.pb" "C:/tf/bass/bass_label_map.pbtxt"
'''
import numpy as np
import tensorflow as tf
import os.path as path
import argparse

import cv2

from object_detection.utils import ops as utils_ops
#from object_detection.utils import label_map_util

from funclib import iolib
from opencvlib.view import show
from opencvlib.imgpipes.generators import FromPaths

from opencvlib import roi
from opencvlib import common

SCORE = []


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


def main():
    '''entry'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('-x', help='Export detections as images to image subdir "detections"', action='store_true')
    cmdline.add_argument('-s', help='Show detections', action='store_true')
    cmdline.add_argument('-v', '--verbosity', help='Set to DEBUG, INFO, WARN, ERROR, or FATAL', default='ERROR')
    cmdline.add_argument('imgfolder', help='Folder with the images')
    cmdline.add_argument('pb_file', help='Folder with the graph in it')
    cmdline.add_argument('labels_file', help='The labels proto')
    args = cmdline.parse_args()
    tf.logging.set_verbosity(get_log_level(args.verbosity))
    pb_file = path.normpath(args.pb_file)
    labels_file = path.normpath(args.labels_file)
    imgfolder = path.normpath(args.imgfolder)

    assert iolib.folder_exists(imgfolder), 'Image folder %s not found' % pb_file
    assert iolib.file_exists(pb_file), 'pb file %s not found' % pb_file
    assert iolib.file_exists(labels_file), 'Labels file %s not found' % labels_file

    detections_folder = path.normpath(path.join(imgfolder, 'detections'))
    if iolib.folder_has_files(detections_folder):
        print('Detection folder %s must be empty. Clear it manually.' % detections_folder)
        return
    iolib.create_folder(detections_folder)

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
    FP = FromPaths(imgfolder, wildcards='*.jpg')
    i = sum([1 for x in FP.generate(pathonly=True)])
    PP = iolib.PrintProgress(i, init_msg='\nRunning detections ...')
    global SCORE
    for  img, imgfile, _ in FP.generate():
        assert isinstance(img, np.ndarray)
        PP.increment()
        w = img.shape[1]; h = img.shape[0]
        #img = cv2.flip(img, 1)
        #img = rotate(img, 15)
        output_dict = run_inference_for_single_image(img, detection_graph) # Actual detection.
        ymin, xmin, ymax, xmax = output_dict['detection_boxes'][0].tolist() #[0.4146363139152527, 0.3671582341194153, 0.525425910949707, 0.770221471786499] ymin, xmin, ymax, xmax
        detection_pts = roi.points_denormalize([[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]], h, w, asint=True)
        score_ = float(output_dict['detection_scores'][0]) #0.99999
        if score_ > 0.5:
            SCORE.append([score_])
            if args.x:
                img_with_detection = common.draw_polygon(img, detection_pts, color=(0, 255, 0), thickness=2)
                s = 'Prediction: %.3f' % score
                try:
                    common.draw_str(img_with_detection, x=25, y=25, s=s, color=(255, 255, 255), box_background=(0, 0, 0), scale=2, box_pad=10)
                    common.draw_str(img_with_detection, detection_pts[0][0], detection_pts[0][1], s='Detection', color=(255, 255, 255), box_background=(0, 255, 0), scale=1.5, box_pad=10)
                except:
                    pass
                detection_image_name = path.normpath(path.join(detections_folder, iolib.get_file_parts2(imgfile)[1]))
                cv2.imwrite(detection_image_name, img_with_detection)

            if args.s:
                show(img_with_detection)
        else:
            SCORE.append([score_])
            print('No bass detected in %s' % iolib.get_file_parts2(imgfile)[1])
    resfile = path.join(detections_folder, 'scores.csv')
    iolib.writecsv(resfile, SCORE, ['score'], inner_as_rows=False)


if __name__ == "__main__":
    main()
