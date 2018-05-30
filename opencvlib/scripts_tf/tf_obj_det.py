#This was the jupyter notebook object_detection_tutorial.ipynb
# When come to export to the spreadsheet
#check this script, point_px_bass_processors.py
'''Detect bass in images.

Example:
tf_obj_det.py "C:/images/vgg_body-caudal.json" /
    "C:/model/frozen_inference_graph.pb" /
    "C:/label_map.pbtxt"
'''
import numpy as np
import tensorflow as tf
import os.path as path
import argparse

import cv2

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

from opencvlib import aruco
from funclib import iolib
from opencvlib.view import show
from opencvlib.imgpipes import vgg
from opencvlib.distance import nearestN_euclidean
from opencvlib import roi
from opencvlib import common


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
            output_dict['num_detections'] = int(output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.uint8)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]
            if 'detection_masks' in output_dict:
                output_dict['detection_masks'] = output_dict['detection_masks'][0]
    return output_dict



def main():
    '''entry'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('-x', help='Export detections as images to image subdir "detections"', action='store_true')
    cmdline.add_argument('vgg_file', help='The full vgg file name')
    cmdline.add_argument('pb_file', help='Folder with the graph in it')
    cmdline.add_argument('labels_file', help='The labels proto')
    args = cmdline.parse_args()

    vgg_file = path.normpath(args.vgg_file)
    pb_file = path.normpath(args.pb_file)
    labels_file = path.normpath(args.labels_file)

    assert iolib.file_exists(vgg_file), 'vgg file %s not found' % vgg_file
    assert iolib.file_exists(pb_file), 'pb file %s not found' % pb_file
    assert iolib.file_exists(labels_file), 'Labels file %s not found' % labels_file

    fld, _, _ = iolib.get_file_parts2(vgg_file)
    detections_folder = path.normpath(path.join(fld, 'detections'))
    if iolib.folder_has_files(detections_folder):
        print('Detection folder %s must be empty. Clear it manually.' % detections_folder)
        return
    iolib.create_folder(detections_folder)

    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(pb_file, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')


    label_map = label_map_util.load_labelmap(labels_file)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=1, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    i = sum([1 for x in vgg.roiGenerator(vgg_file, skip_imghdr_check=False, shape_type='rect')])
    PP = iolib.PrintProgress(i, init_msg='Processing ...')

    results = ['imgname', 'w', 'h', 'groundtruth_xmin', 'groundtruth_xmax', 'groundtruth_ymin', 'groundtruth_ymax', 'xmin', 'xmax', 'ymin', 'ymax', 'accuracy']
    errs = []
    for imgpath, res, Reg in vgg.roiGenerator(vgg_file, skip_imghdr_check=False, shape_type='rect'):
        assert isinstance(Reg, vgg.Region)
        PP.increment()
        w = res[0]; h = res[1]
        imgpath = path.normpath(imgpath)
        imgfld, imgname, _ = iolib.get_file_parts2(imgpath)
        img = cv2.imread(imgpath)
        output_dict = run_inference_for_single_image(img, detection_graph) # Actual detection.
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
            continue

        length_est = abs((detection_pts[1][0] - detection_pts[0][0])) * marker.px_length_mm()

        img_with_groundtruth = common.draw_polygon(img, Reg.all_points, color=(0, 0, 0), thickness=2)
        img_with_detection = common.draw_polygon(img_with_groundtruth, detection_pts, color=(0, 255, 0), thickness=2)
        s = 'Prediction: %.3f' % score
        common.draw_str(img_with_detection, x=25, y=25, s=s, color=(255, 255, 255), box_background=(0, 0, 0), scale=2, box_pad=10)
        common.draw_str(img_with_detection, detection_pts[0][0], detection_pts[0][1], s='Detection', color=(255, 255, 255), box_background=(0, 255, 0), scale=1.5, box_pad=10)
        common.draw_str(img_with_detection, Reg.all_points_x[0], Reg.all_points_y[2], s='Groundtruth', color=(255, 255, 255), box_background=(0, 0, 0), scale=1.5, box_pad=10)

        #vis_util.visualize_boxes_and_labels_on_image_array(img, output_dict['detection_boxes'], output_dict['detection_classes'], output_dict['detection_scores'], category_index, instance_masks=output_dict.get('detection_masks'), use_normalized_coordinates=True, line_thickness=8, max_boxes_to_draw=1) # Visualization of the results of a detection.
        show(img_with_detection)
        if args.x:
            detection_image_name = path.normpath(path.join(detections_folder, imgname))
            cv2.imwrite(detection_image_name, img_with_detection)

    #export any problems to a csv file
    if errs:
        errfile = path.normpath(path.join(imgfld, 'errs.csv'))
        try:
            iolib.writecsv(errfile, errs, inner_as_rows=False)
        except Exception as e:
            pass

if __name__ == "__main__":
    main()
