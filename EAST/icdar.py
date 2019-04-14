#pylint: skip-file
# coding:utf-8
import glob
import csv
import cv2
import time
import os
import numpy
import scipy.optimize
import matplotlib.pyplot as plt
import matplotlib.patches as Patches
from shapely.geometry import Polygon

import tensorflow as tf

from EAST.data_util import GeneratorEnqueuer

tf.app.flags.DEFINE_string('training_data_path', '/data/ocr/icdar2015/',
                           'training dataset to use')
tf.app.flags.DEFINE_integer('max_image_large_side', 1280,
                            'max image size of training')
tf.app.flags.DEFINE_integer('max_text_size', 800,
                            'if the text in the input image is bigger than this, then we resize'
                            'the image according to this')
tf.app.flags.DEFINE_integer('min_text_size', 10,
                            'if the text size is smaller than this, we ignore it during training')
tf.app.flags.DEFINE_float('min_crop_side_ratio', 0.1,
                          'when doing random crop from input image, the'
                          'min length of min(H, W')
tf.app.flags.DEFINE_string('geometry', 'RBOX',
                           'which geometry to generate, RBOX or QUAD')


ICDAR_FLAGS = tf.app.flags.FLAGS


def get_images():
    files = []
    for ext in ['jpg', 'png', 'jpeg', 'JPG']:
        files.extend(glob.glob(os.path.join(ICDAR_FLAGS.training_data_path, '*.{}'.format(ext))))
    return files


def load_annoataion(p):
    '''
    load annotation from the text file
    :param p:
    :return:
    '''
    text_polys = []
    text_tags = []
    if not os.path.exists(p):
        return numpy.array(text_polys, dtype=numpy.float32)
    with open(p, 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            label = line[-1]
            # strip BOM.  \ufeff for python3, \xef\xbb\bf for python2
            line = [i.strip('\ufeff').strip('\xef\xbb\xbf') for i in line]

            x1, y1, x2, y2, x3, y3, x4, y4 = list(map(float, line[:8]))
            text_polys.append([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
            if label == '*' or label == '###':
                text_tags.append(True)
            else:
                text_tags.append(False)
        return numpy.array(text_polys, dtype=numpy.float32), numpy.array(text_tags, dtype=numpy.bool)


def polygon_area(poly):
    '''
    compute area of a polygon
    :param poly:
    :return:
    '''
    edge = [(poly[1][0] - poly[0][0]) * (poly[1][1] + poly[0][1]),
        (poly[2][0] - poly[1][0]) * (poly[2][1] + poly[1][1]),
        (poly[3][0] - poly[2][0]) * (poly[3][1] + poly[2][1]),
        (poly[0][0] - poly[3][0]) * (poly[0][1] + poly[3][1])]
    return numpy.sum(edge) / 2.


def check_and_validate_polys(polys, tags, xxx_todo_changeme):
    '''
    check so that the text poly is in the same direction,
    and also filter some invalid polygons
    :param polys:
    :param tags:
    :return:
    '''
    (h, w) = xxx_todo_changeme
    if polys.shape[0] == 0:
        return polys
    polys[:, :, 0] = numpy.clip(polys[:, :, 0], 0, w - 1)
    polys[:, :, 1] = numpy.clip(polys[:, :, 1], 0, h - 1)

    validated_polys = []
    validated_tags = []
    for poly, tag in zip(polys, tags):
        p_area = polygon_area(poly)
        if abs(p_area) < 1:
            # print poly
            print('invalid poly')
            continue
        if p_area > 0:
            print('poly in wrong direction')
            poly = poly[(0, 3, 2, 1), :]
        validated_polys.append(poly)
        validated_tags.append(tag)
    return numpy.array(validated_polys), numpy.array(validated_tags)


def crop_area(im, polys, tags, crop_background=False, max_tries=50):
    '''
    make random crop from the input image
    :param im:
    :param polys:
    :param tags:
    :param crop_background:
    :param max_tries:
    :return:
    '''
    h, w, _ = im.shape
    pad_h = h // 10
    pad_w = w // 10
    h_array = numpy.zeros((h + pad_h * 2), dtype=numpy.int32)
    w_array = numpy.zeros((w + pad_w * 2), dtype=numpy.int32)
    for poly in polys:
        poly = numpy.round(poly, decimals=0).astype(numpy.int32)
        minx = numpy.min(poly[:, 0])
        maxx = numpy.max(poly[:, 0])
        w_array[minx + pad_w:maxx + pad_w] = 1
        miny = numpy.min(poly[:, 1])
        maxy = numpy.max(poly[:, 1])
        h_array[miny + pad_h:maxy + pad_h] = 1
    # ensure the cropped area not across a text
    h_axis = numpy.where(h_array == 0)[0]
    w_axis = numpy.where(w_array == 0)[0]
    if len(h_axis) == 0 or len(w_axis) == 0:
        return im, polys, tags
    for i in range(max_tries):
        xx = numpy.random.choice(w_axis, size=2)
        xmin = numpy.min(xx) - pad_w
        xmax = numpy.max(xx) - pad_w
        xmin = numpy.clip(xmin, 0, w - 1)
        xmax = numpy.clip(xmax, 0, w - 1)
        yy = numpy.random.choice(h_axis, size=2)
        ymin = numpy.min(yy) - pad_h
        ymax = numpy.max(yy) - pad_h
        ymin = numpy.clip(ymin, 0, h - 1)
        ymax = numpy.clip(ymax, 0, h - 1)
        if xmax - xmin < ICDAR_FLAGS.min_crop_side_ratio * w or ymax - ymin < ICDAR_FLAGS.min_crop_side_ratio * h:
            # area too small
            continue
        if polys.shape[0] != 0:
            poly_axis_in_area = (polys[:, :, 0] >= xmin) & (polys[:, :, 0] <= xmax) \
                                & (polys[:, :, 1] >= ymin) & (polys[:, :, 1] <= ymax)
            selected_polys = numpy.where(numpy.sum(poly_axis_in_area, axis=1) == 4)[0]
        else:
            selected_polys = []
        if len(selected_polys) == 0:
            # no text in this area
            if crop_background:
                return im[ymin:ymax + 1, xmin:xmax + 1, :], polys[selected_polys], tags[selected_polys]
            else:
                continue
        im = im[ymin:ymax + 1, xmin:xmax + 1, :]
        polys = polys[selected_polys]
        tags = tags[selected_polys]
        polys[:, :, 0] -= xmin
        polys[:, :, 1] -= ymin
        return im, polys, tags

    return im, polys, tags


def shrink_poly(poly, r):
    '''
    fit a poly inside the origin poly, maybe bugs here...
    used for generate the score map
    :param poly: the text poly
    :param r: r in the paper
    :return: the shrinked poly
    '''
    # shrink ratio
    R = 0.3
    # find the longer pair
    if numpy.linalg.norm(poly[0] - poly[1]) + numpy.linalg.norm(poly[2] - poly[3]) > \
                    numpy.linalg.norm(poly[0] - poly[3]) + numpy.linalg.norm(poly[1] - poly[2]):
        # first move (p0, p1), (p2, p3), then (p0, p3), (p1, p2)
        ## p0, p1
        theta = numpy.arctan2((poly[1][1] - poly[0][1]), (poly[1][0] - poly[0][0]))
        poly[0][0] += R * r[0] * numpy.cos(theta)
        poly[0][1] += R * r[0] * numpy.sin(theta)
        poly[1][0] -= R * r[1] * numpy.cos(theta)
        poly[1][1] -= R * r[1] * numpy.sin(theta)
        ## p2, p3
        theta = numpy.arctan2((poly[2][1] - poly[3][1]), (poly[2][0] - poly[3][0]))
        poly[3][0] += R * r[3] * numpy.cos(theta)
        poly[3][1] += R * r[3] * numpy.sin(theta)
        poly[2][0] -= R * r[2] * numpy.cos(theta)
        poly[2][1] -= R * r[2] * numpy.sin(theta)
        ## p0, p3
        theta = numpy.arctan2((poly[3][0] - poly[0][0]), (poly[3][1] - poly[0][1]))
        poly[0][0] += R * r[0] * numpy.sin(theta)
        poly[0][1] += R * r[0] * numpy.cos(theta)
        poly[3][0] -= R * r[3] * numpy.sin(theta)
        poly[3][1] -= R * r[3] * numpy.cos(theta)
        ## p1, p2
        theta = numpy.arctan2((poly[2][0] - poly[1][0]), (poly[2][1] - poly[1][1]))
        poly[1][0] += R * r[1] * numpy.sin(theta)
        poly[1][1] += R * r[1] * numpy.cos(theta)
        poly[2][0] -= R * r[2] * numpy.sin(theta)
        poly[2][1] -= R * r[2] * numpy.cos(theta)
    else:
        ## p0, p3
        # print poly
        theta = numpy.arctan2((poly[3][0] - poly[0][0]), (poly[3][1] - poly[0][1]))
        poly[0][0] += R * r[0] * numpy.sin(theta)
        poly[0][1] += R * r[0] * numpy.cos(theta)
        poly[3][0] -= R * r[3] * numpy.sin(theta)
        poly[3][1] -= R * r[3] * numpy.cos(theta)
        ## p1, p2
        theta = numpy.arctan2((poly[2][0] - poly[1][0]), (poly[2][1] - poly[1][1]))
        poly[1][0] += R * r[1] * numpy.sin(theta)
        poly[1][1] += R * r[1] * numpy.cos(theta)
        poly[2][0] -= R * r[2] * numpy.sin(theta)
        poly[2][1] -= R * r[2] * numpy.cos(theta)
        ## p0, p1
        theta = numpy.arctan2((poly[1][1] - poly[0][1]), (poly[1][0] - poly[0][0]))
        poly[0][0] += R * r[0] * numpy.cos(theta)
        poly[0][1] += R * r[0] * numpy.sin(theta)
        poly[1][0] -= R * r[1] * numpy.cos(theta)
        poly[1][1] -= R * r[1] * numpy.sin(theta)
        ## p2, p3
        theta = numpy.arctan2((poly[2][1] - poly[3][1]), (poly[2][0] - poly[3][0]))
        poly[3][0] += R * r[3] * numpy.cos(theta)
        poly[3][1] += R * r[3] * numpy.sin(theta)
        poly[2][0] -= R * r[2] * numpy.cos(theta)
        poly[2][1] -= R * r[2] * numpy.sin(theta)
    return poly


def point_dist_to_line(p1, p2, p3):
    # compute the distance from p3 to p1-p2
    return numpy.linalg.norm(numpy.cross(p2 - p1, p1 - p3)) / numpy.linalg.norm(p2 - p1)


def fit_line(p1, p2):
    # fit a line ax+by+c = 0
    if p1[0] == p1[1]:
        return [1., 0., -p1[0]]
    else:
        [k, b] = numpy.polyfit(p1, p2, deg=1)
        return [k, -1., b]


def line_cross_point(line1, line2):
    # line1 0= ax+by+c, compute the cross point of line1 and line2
    if line1[0] != 0 and line1[0] == line2[0]:
        print('Cross point does not exist')
        return None
    if line1[0] == 0 and line2[0] == 0:
        print('Cross point does not exist')
        return None
    if line1[1] == 0:
        x = -line1[2]
        y = line2[0] * x + line2[2]
    elif line2[1] == 0:
        x = -line2[2]
        y = line1[0] * x + line1[2]
    else:
        k1, _, b1 = line1
        k2, _, b2 = line2
        x = -(b1 - b2) / (k1 - k2)
        y = k1 * x + b1
    return numpy.array([x, y], dtype=numpy.float32)


def line_verticle(line, point):
    # get the verticle line from line across point
    if line[1] == 0:
        verticle = [0, -1, point[1]]
    else:
        if line[0] == 0:
            verticle = [1, 0, -point[0]]
        else:
            verticle = [-1. / line[0], -1, point[1] - (-1 / line[0] * point[0])]
    return verticle


def rectangle_from_parallelogram(poly):
    '''
    fit a rectangle from a parallelogram
    :param poly:
    :return:
    '''
    p0, p1, p2, p3 = poly
    angle_p0 = numpy.arccos(numpy.dot(p1 - p0, p3 - p0) / (numpy.linalg.norm(p0 - p1) * numpy.linalg.norm(p3 - p0)))
    if angle_p0 < 0.5 * numpy.pi:
        if numpy.linalg.norm(p0 - p1) > numpy.linalg.norm(p0 - p3):
            # p0 and p2
            ## p0
            p2p3 = fit_line([p2[0], p3[0]], [p2[1], p3[1]])
            p2p3_verticle = line_verticle(p2p3, p0)

            new_p3 = line_cross_point(p2p3, p2p3_verticle)
            ## p2
            p0p1 = fit_line([p0[0], p1[0]], [p0[1], p1[1]])
            p0p1_verticle = line_verticle(p0p1, p2)

            new_p1 = line_cross_point(p0p1, p0p1_verticle)
            return numpy.array([p0, new_p1, p2, new_p3], dtype=numpy.float32)
        else:
            p1p2 = fit_line([p1[0], p2[0]], [p1[1], p2[1]])
            p1p2_verticle = line_verticle(p1p2, p0)

            new_p1 = line_cross_point(p1p2, p1p2_verticle)
            p0p3 = fit_line([p0[0], p3[0]], [p0[1], p3[1]])
            p0p3_verticle = line_verticle(p0p3, p2)

            new_p3 = line_cross_point(p0p3, p0p3_verticle)
            return numpy.array([p0, new_p1, p2, new_p3], dtype=numpy.float32)
    else:
        if numpy.linalg.norm(p0 - p1) > numpy.linalg.norm(p0 - p3):
            # p1 and p3
            ## p1
            p2p3 = fit_line([p2[0], p3[0]], [p2[1], p3[1]])
            p2p3_verticle = line_verticle(p2p3, p1)

            new_p2 = line_cross_point(p2p3, p2p3_verticle)
            ## p3
            p0p1 = fit_line([p0[0], p1[0]], [p0[1], p1[1]])
            p0p1_verticle = line_verticle(p0p1, p3)

            new_p0 = line_cross_point(p0p1, p0p1_verticle)
            return numpy.array([new_p0, p1, new_p2, p3], dtype=numpy.float32)
        else:
            p0p3 = fit_line([p0[0], p3[0]], [p0[1], p3[1]])
            p0p3_verticle = line_verticle(p0p3, p1)

            new_p0 = line_cross_point(p0p3, p0p3_verticle)
            p1p2 = fit_line([p1[0], p2[0]], [p1[1], p2[1]])
            p1p2_verticle = line_verticle(p1p2, p3)

            new_p2 = line_cross_point(p1p2, p1p2_verticle)
            return numpy.array([new_p0, p1, new_p2, p3], dtype=numpy.float32)


def sort_rectangle(poly):
    # sort the four coordinates of the polygon, points in poly should be sorted
    # clockwise
    # First find the lowest point
    p_lowest = numpy.argmax(poly[:, 1])
    if numpy.count_nonzero(poly[:, 1] == poly[p_lowest, 1]) == 2:
        # 底边平行于X轴, 那么p0为左上角 - if the bottom line is parallel to x-axis, then p0
        # must be the upper-left corner
        p0_index = numpy.argmin(numpy.sum(poly, axis=1))
        p1_index = (p0_index + 1) % 4
        p2_index = (p0_index + 2) % 4
        p3_index = (p0_index + 3) % 4
        return poly[[p0_index, p1_index, p2_index, p3_index]], 0.
    else:
        # 找到最低点右边的点 - find the point that sits right to the lowest point
        p_lowest_right = (p_lowest - 1) % 4
        p_lowest_left = (p_lowest + 1) % 4
        angle = numpy.arctan(-(poly[p_lowest][1] - poly[p_lowest_right][1]) / (poly[p_lowest][0] - poly[p_lowest_right][0]))
        # assert angle > 0
        if angle <= 0:
            print(angle, poly[p_lowest], poly[p_lowest_right])
        if angle / numpy.pi * 180 > 45:
            # 这个点为p2 - this point is p2
            p2_index = p_lowest
            p1_index = (p2_index - 1) % 4
            p0_index = (p2_index - 2) % 4
            p3_index = (p2_index + 1) % 4
            return poly[[p0_index, p1_index, p2_index, p3_index]], -(numpy.pi / 2 - angle)
        else:
            # 这个点为p3 - this point is p3
            p3_index = p_lowest
            p0_index = (p3_index + 1) % 4
            p1_index = (p3_index + 2) % 4
            p2_index = (p3_index + 3) % 4
            return poly[[p0_index, p1_index, p2_index, p3_index]], angle


def restore_rectangle_rbox(origin, geometry):
    d = geometry[:, :4]
    angle = geometry[:, 4]
    # for angle > 0
    origin_0 = origin[angle >= 0]
    d_0 = d[angle >= 0]
    angle_0 = angle[angle >= 0]
    if origin_0.shape[0] > 0:
        p = numpy.array([numpy.zeros(d_0.shape[0]), -d_0[:, 0] - d_0[:, 2],
                      d_0[:, 1] + d_0[:, 3], -d_0[:, 0] - d_0[:, 2],
                      d_0[:, 1] + d_0[:, 3], numpy.zeros(d_0.shape[0]),
                      numpy.zeros(d_0.shape[0]), numpy.zeros(d_0.shape[0]),
                      d_0[:, 3], -d_0[:, 2]])
        p = p.transpose((1, 0)).reshape((-1, 5, 2))  # N*5*2

        rotate_matrix_x = numpy.array([numpy.cos(angle_0), numpy.sin(angle_0)]).transpose((1, 0))
        rotate_matrix_x = numpy.repeat(rotate_matrix_x, 5, axis=1).reshape(-1, 2, 5).transpose((0, 2, 1))  # N*5*2

        rotate_matrix_y = numpy.array([-numpy.sin(angle_0), numpy.cos(angle_0)]).transpose((1, 0))
        rotate_matrix_y = numpy.repeat(rotate_matrix_y, 5, axis=1).reshape(-1, 2, 5).transpose((0, 2, 1))

        p_rotate_x = numpy.sum(rotate_matrix_x * p, axis=2)[:, :, numpy.newaxis]  # N*5*1
        p_rotate_y = numpy.sum(rotate_matrix_y * p, axis=2)[:, :, numpy.newaxis]  # N*5*1

        p_rotate = numpy.concatenate([p_rotate_x, p_rotate_y], axis=2)  # N*5*2

        p3_in_origin = origin_0 - p_rotate[:, 4, :]
        new_p0 = p_rotate[:, 0, :] + p3_in_origin  # N*2
        new_p1 = p_rotate[:, 1, :] + p3_in_origin
        new_p2 = p_rotate[:, 2, :] + p3_in_origin
        new_p3 = p_rotate[:, 3, :] + p3_in_origin

        new_p_0 = numpy.concatenate([new_p0[:, numpy.newaxis, :], new_p1[:, numpy.newaxis, :],
                                  new_p2[:, numpy.newaxis, :], new_p3[:, numpy.newaxis, :]], axis=1)  # N*4*2
    else:
        new_p_0 = numpy.zeros((0, 4, 2))
    # for angle < 0
    origin_1 = origin[angle < 0]
    d_1 = d[angle < 0]
    angle_1 = angle[angle < 0]
    if origin_1.shape[0] > 0:
        p = numpy.array([-d_1[:, 1] - d_1[:, 3], -d_1[:, 0] - d_1[:, 2],
                      numpy.zeros(d_1.shape[0]), -d_1[:, 0] - d_1[:, 2],
                      numpy.zeros(d_1.shape[0]), numpy.zeros(d_1.shape[0]),
                      -d_1[:, 1] - d_1[:, 3], numpy.zeros(d_1.shape[0]),
                      -d_1[:, 1], -d_1[:, 2]])
        p = p.transpose((1, 0)).reshape((-1, 5, 2))  # N*5*2

        rotate_matrix_x = numpy.array([numpy.cos(-angle_1), -numpy.sin(-angle_1)]).transpose((1, 0))
        rotate_matrix_x = numpy.repeat(rotate_matrix_x, 5, axis=1).reshape(-1, 2, 5).transpose((0, 2, 1))  # N*5*2

        rotate_matrix_y = numpy.array([numpy.sin(-angle_1), numpy.cos(-angle_1)]).transpose((1, 0))
        rotate_matrix_y = numpy.repeat(rotate_matrix_y, 5, axis=1).reshape(-1, 2, 5).transpose((0, 2, 1))

        p_rotate_x = numpy.sum(rotate_matrix_x * p, axis=2)[:, :, numpy.newaxis]  # N*5*1
        p_rotate_y = numpy.sum(rotate_matrix_y * p, axis=2)[:, :, numpy.newaxis]  # N*5*1

        p_rotate = numpy.concatenate([p_rotate_x, p_rotate_y], axis=2)  # N*5*2

        p3_in_origin = origin_1 - p_rotate[:, 4, :]
        new_p0 = p_rotate[:, 0, :] + p3_in_origin  # N*2
        new_p1 = p_rotate[:, 1, :] + p3_in_origin
        new_p2 = p_rotate[:, 2, :] + p3_in_origin
        new_p3 = p_rotate[:, 3, :] + p3_in_origin

        new_p_1 = numpy.concatenate([new_p0[:, numpy.newaxis, :], new_p1[:, numpy.newaxis, :],
                                  new_p2[:, numpy.newaxis, :], new_p3[:, numpy.newaxis, :]], axis=1)  # N*4*2
    else:
        new_p_1 = numpy.zeros((0, 4, 2))
    return numpy.concatenate([new_p_0, new_p_1])


def restore_rectangle(origin, geometry):
    return restore_rectangle_rbox(origin, geometry)


def generate_rbox(im_size, polys, tags):
    h, w = im_size
    poly_mask = numpy.zeros((h, w), dtype=numpy.uint8)
    score_map = numpy.zeros((h, w), dtype=numpy.uint8)
    geo_map = numpy.zeros((h, w, 5), dtype=numpy.float32)
    # mask used during traning, to ignore some hard areas
    training_mask = numpy.ones((h, w), dtype=numpy.uint8)
    for poly_idx, poly_tag in enumerate(zip(polys, tags)):
        poly = poly_tag[0]
        tag = poly_tag[1]

        r = [None, None, None, None]
        for i in range(4):
            r[i] = min(numpy.linalg.norm(poly[i] - poly[(i + 1) % 4]),
                       numpy.linalg.norm(poly[i] - poly[(i - 1) % 4]))
        # score map
        shrinked_poly = shrink_poly(poly.copy(), r).astype(numpy.int32)[numpy.newaxis, :, :]
        cv2.fillPoly(score_map, shrinked_poly, 1)
        cv2.fillPoly(poly_mask, shrinked_poly, poly_idx + 1)
        # if the poly is too small, then ignore it during training
        poly_h = min(numpy.linalg.norm(poly[0] - poly[3]), numpy.linalg.norm(poly[1] - poly[2]))
        poly_w = min(numpy.linalg.norm(poly[0] - poly[1]), numpy.linalg.norm(poly[2] - poly[3]))
        if min(poly_h, poly_w) < ICDAR_FLAGS.min_text_size:
            cv2.fillPoly(training_mask, poly.astype(numpy.int32)[numpy.newaxis, :, :], 0)
        if tag:
            cv2.fillPoly(training_mask, poly.astype(numpy.int32)[numpy.newaxis, :, :], 0)

        xy_in_poly = numpy.argwhere(poly_mask == (poly_idx + 1))
        # if geometry == 'RBOX':
        # 对任意两个顶点的组合生成一个平行四边形 - generate a parallelogram for any combination of
        # two vertices
        fitted_parallelograms = []
        for i in range(4):
            p0 = poly[i]
            p1 = poly[(i + 1) % 4]
            p2 = poly[(i + 2) % 4]
            p3 = poly[(i + 3) % 4]
            edge = fit_line([p0[0], p1[0]], [p0[1], p1[1]])
            backward_edge = fit_line([p0[0], p3[0]], [p0[1], p3[1]])
            forward_edge = fit_line([p1[0], p2[0]], [p1[1], p2[1]])
            if point_dist_to_line(p0, p1, p2) > point_dist_to_line(p0, p1, p3):
                # 平行线经过p2 - parallel lines through p2
                if edge[1] == 0:
                    edge_opposite = [1, 0, -p2[0]]
                else:
                    edge_opposite = [edge[0], -1, p2[1] - edge[0] * p2[0]]
            else:
                # 经过p3 - after p3
                if edge[1] == 0:
                    edge_opposite = [1, 0, -p3[0]]
                else:
                    edge_opposite = [edge[0], -1, p3[1] - edge[0] * p3[0]]
            # move forward edge
            new_p0 = p0
            new_p1 = p1
            new_p2 = p2
            new_p3 = p3
            new_p2 = line_cross_point(forward_edge, edge_opposite)
            if point_dist_to_line(p1, new_p2, p0) > point_dist_to_line(p1, new_p2, p3):
                # across p0
                if forward_edge[1] == 0:
                    forward_opposite = [1, 0, -p0[0]]
                else:
                    forward_opposite = [forward_edge[0], -1, p0[1] - forward_edge[0] * p0[0]]
            else:
                # across p3
                if forward_edge[1] == 0:
                    forward_opposite = [1, 0, -p3[0]]
                else:
                    forward_opposite = [forward_edge[0], -1, p3[1] - forward_edge[0] * p3[0]]
            new_p0 = line_cross_point(forward_opposite, edge)
            new_p3 = line_cross_point(forward_opposite, edge_opposite)
            fitted_parallelograms.append([new_p0, new_p1, new_p2, new_p3, new_p0])
            # or move backward edge
            new_p0 = p0
            new_p1 = p1
            new_p2 = p2
            new_p3 = p3
            new_p3 = line_cross_point(backward_edge, edge_opposite)
            if point_dist_to_line(p0, p3, p1) > point_dist_to_line(p0, p3, p2):
                # across p1
                if backward_edge[1] == 0:
                    backward_opposite = [1, 0, -p1[0]]
                else:
                    backward_opposite = [backward_edge[0], -1, p1[1] - backward_edge[0] * p1[0]]
            else:
                # across p2
                if backward_edge[1] == 0:
                    backward_opposite = [1, 0, -p2[0]]
                else:
                    backward_opposite = [backward_edge[0], -1, p2[1] - backward_edge[0] * p2[0]]
            new_p1 = line_cross_point(backward_opposite, edge)
            new_p2 = line_cross_point(backward_opposite, edge_opposite)
            fitted_parallelograms.append([new_p0, new_p1, new_p2, new_p3, new_p0])
        areas = [Polygon(t).area for t in fitted_parallelograms]
        parallelogram = numpy.array(fitted_parallelograms[numpy.argmin(areas)][:-1], dtype=numpy.float32)
        # sort thie polygon
        parallelogram_coord_sum = numpy.sum(parallelogram, axis=1)
        min_coord_idx = numpy.argmin(parallelogram_coord_sum)
        parallelogram = parallelogram[[min_coord_idx, (min_coord_idx + 1) % 4, (min_coord_idx + 2) % 4, (min_coord_idx + 3) % 4]]

        rectange = rectangle_from_parallelogram(parallelogram)
        rectange, rotate_angle = sort_rectangle(rectange)

        p0_rect, p1_rect, p2_rect, p3_rect = rectange
        for y, x in xy_in_poly:
            point = numpy.array([x, y], dtype=numpy.float32)
            # top
            geo_map[y, x, 0] = point_dist_to_line(p0_rect, p1_rect, point)
            # right
            geo_map[y, x, 1] = point_dist_to_line(p1_rect, p2_rect, point)
            # down
            geo_map[y, x, 2] = point_dist_to_line(p2_rect, p3_rect, point)
            # left
            geo_map[y, x, 3] = point_dist_to_line(p3_rect, p0_rect, point)
            # angle
            geo_map[y, x, 4] = rotate_angle
    return score_map, geo_map, training_mask


def generator(input_size=512, batch_size=32,
              background_ratio=3. / 8,
              random_scale=numpy.array([0.5, 1, 2.0, 3.0]),
              vis=False):
    image_list = numpy.array(get_images())
    print('{} training images in {}'.format(image_list.shape[0], ICDAR_FLAGS.training_data_path))
    index = numpy.arange(0, image_list.shape[0])
    while True:
        numpy.random.shuffle(index)
        images = []
        image_fns = []
        score_maps = []
        geo_maps = []
        training_masks = []
        for i in index:
            try:
                im_fn = image_list[i]
                im = cv2.imread(im_fn)
                # print im_fn
                h, w, _ = im.shape
                txt_fn = im_fn.replace(os.path.basename(im_fn).split('.')[1], 'txt')
                if not os.path.exists(txt_fn):
                    print('text file {} does not exists'.format(txt_fn))
                    continue

                text_polys, text_tags = load_annoataion(txt_fn)

                text_polys, text_tags = check_and_validate_polys(text_polys, text_tags, (h, w))
                # if text_polys.shape[0] == 0:
                #     continue
                # random scale this image
                rd_scale = numpy.random.choice(random_scale)
                im = cv2.resize(im, dsize=None, fx=rd_scale, fy=rd_scale)
                text_polys *= rd_scale
                # print rd_scale
                # random crop a area from image
                if numpy.random.rand() < background_ratio:
                    # crop background
                    im, text_polys, text_tags = crop_area(im, text_polys, text_tags, crop_background=True)
                    if text_polys.shape[0] > 0:
                        # cannot find background
                        continue
                    # pad and resize image
                    new_h, new_w, _ = im.shape
                    max_h_w_i = numpy.max([new_h, new_w, input_size])
                    im_padded = numpy.zeros((max_h_w_i, max_h_w_i, 3), dtype=numpy.uint8)
                    im_padded[:new_h, :new_w, :] = im.copy()
                    im = cv2.resize(im_padded, dsize=(input_size, input_size))
                    score_map = numpy.zeros((input_size, input_size), dtype=numpy.uint8)
                    geo_map_channels = 5 if ICDAR_FLAGS.geometry == 'RBOX' else 8
                    geo_map = numpy.zeros((input_size, input_size, geo_map_channels), dtype=numpy.float32)
                    training_mask = numpy.ones((input_size, input_size), dtype=numpy.uint8)
                else:
                    im, text_polys, text_tags = crop_area(im, text_polys, text_tags, crop_background=False)
                    if text_polys.shape[0] == 0:
                        continue
                    h, w, _ = im.shape

                    # pad the image to the training input size or the longer
                    # side of image
                    new_h, new_w, _ = im.shape
                    max_h_w_i = numpy.max([new_h, new_w, input_size])
                    im_padded = numpy.zeros((max_h_w_i, max_h_w_i, 3), dtype=numpy.uint8)
                    im_padded[:new_h, :new_w, :] = im.copy()
                    im = im_padded
                    # resize the image to input size
                    new_h, new_w, _ = im.shape
                    resize_h = input_size
                    resize_w = input_size
                    im = cv2.resize(im, dsize=(resize_w, resize_h))
                    resize_ratio_3_x = resize_w / float(new_w)
                    resize_ratio_3_y = resize_h / float(new_h)
                    text_polys[:, :, 0] *= resize_ratio_3_x
                    text_polys[:, :, 1] *= resize_ratio_3_y
                    new_h, new_w, _ = im.shape
                    score_map, geo_map, training_mask = generate_rbox((new_h, new_w), text_polys, text_tags)

                if vis:
                    fig, axs = plt.subplots(3, 2, figsize=(20, 30))
                    # axs[0].imshow(im[:, :, ::-1])
                    # axs[0].set_xticks([])
                    # axs[0].set_yticks([])
                    # for poly in text_polys:
                    #     poly_h = min(abs(poly[3, 1] - poly[0, 1]),
                    #     abs(poly[2, 1] - poly[1, 1]))
                    #     poly_w = min(abs(poly[1, 0] - poly[0, 0]),
                    #     abs(poly[2, 0] - poly[3, 0]))
                    #     axs[0].add_artist(Patches.Polygon(
                    #         poly * 4, facecolor='none', edgecolor='green',
                    #         linewidth=2, linestyle='-', fill=True))
                    #     axs[0].text(poly[0, 0] * 4, poly[0, 1] * 4,
                    #     '{:.0f}-{:.0f}'.format(poly_h * 4, poly_w * 4),
                    #                    color='purple')
                    # axs[1].imshow(score_map)
                    # axs[1].set_xticks([])
                    # axs[1].set_yticks([])
                    axs[0, 0].imshow(im[:, :, ::-1])
                    axs[0, 0].set_xticks([])
                    axs[0, 0].set_yticks([])
                    for poly in text_polys:
                        poly_h = min(abs(poly[3, 1] - poly[0, 1]), abs(poly[2, 1] - poly[1, 1]))
                        poly_w = min(abs(poly[1, 0] - poly[0, 0]), abs(poly[2, 0] - poly[3, 0]))
                        axs[0, 0].add_artist(Patches.Polygon(poly, facecolor='none', edgecolor='green', linewidth=2, linestyle='-', fill=True))
                        axs[0, 0].text(poly[0, 0], poly[0, 1], '{:.0f}-{:.0f}'.format(poly_h, poly_w), color='purple')
                    axs[0, 1].imshow(score_map[::, ::])
                    axs[0, 1].set_xticks([])
                    axs[0, 1].set_yticks([])
                    axs[1, 0].imshow(geo_map[::, ::, 0])
                    axs[1, 0].set_xticks([])
                    axs[1, 0].set_yticks([])
                    axs[1, 1].imshow(geo_map[::, ::, 1])
                    axs[1, 1].set_xticks([])
                    axs[1, 1].set_yticks([])
                    axs[2, 0].imshow(geo_map[::, ::, 2])
                    axs[2, 0].set_xticks([])
                    axs[2, 0].set_yticks([])
                    axs[2, 1].imshow(training_mask[::, ::])
                    axs[2, 1].set_xticks([])
                    axs[2, 1].set_yticks([])
                    plt.tight_layout()
                    plt.show()
                    plt.close()

                images.append(im[:, :, ::-1].astype(numpy.float32))
                image_fns.append(im_fn)
                score_maps.append(score_map[::4, ::4, numpy.newaxis].astype(numpy.float32))
                geo_maps.append(geo_map[::4, ::4, :].astype(numpy.float32))
                training_masks.append(training_mask[::4, ::4, numpy.newaxis].astype(numpy.float32))

                if len(images) == batch_size:
                    yield images, image_fns, score_maps, geo_maps, training_masks
                    images = []
                    image_fns = []
                    score_maps = []
                    geo_maps = []
                    training_masks = []
            except Exception as e:
                import traceback
                traceback.print_exc()
                continue


def get_batch(num_workers, **kwargs):
    try:
        enqueuer = GeneratorEnqueuer(generator(**kwargs), use_multiprocessing=True)
        print('Generator use 10 batches for buffering, this may take a while, you can tune this yourself.')
        enqueuer.start(max_queue_size=10, workers=num_workers)
        generator_output = None
        while True:
            while enqueuer.is_running():
                if not enqueuer.queue.empty():
                    generator_output = enqueuer.queue.get()
                    break
                else:
                    time.sleep(0.01)
            yield generator_output
            generator_output = None
    finally:
        if enqueuer is not None:
            enqueuer.stop()



if __name__ == '__main__':
    pass
