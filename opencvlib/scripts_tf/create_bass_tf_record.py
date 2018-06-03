# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''
Create a TFRecord file from images and their assigned roi. This saves the whole image into the TFRecord file.

    -d: Delete all .record files in the output folder first
    -b: batch size, create multiple .record files with a size specified with the -b argument

    Positional args:
        source_folder, output_folder, vgg_file_name


Example:
    create_bass_tf_record.py -d -b 20 "C:/candidate" "C:/candidate/test.record" vgg_body.json

Comments:
    output_folder will be created if it doesn't exist
'''
import argparse
import hashlib
import io
import os
import random
import re
import os.path as path


from lxml import etree
import numpy as np
import PIL.Image
import tensorflow as tf
import cv2

from object_detection.utils import dataset_util
from object_detection.utils import label_map_util

import funclib.iolib as iolib
import funclib.stringslib as stringslib
import opencvlib.roi as roi
import opencvlib.imgpipes.vgg as vgg
from opencvlib.imgpipes.generators import VGGROI
import opencvlib.transforms as transforms
from opencvlib.view import show
from opencvlib import common

PP = iolib.PrintProgress()
vgg.SILENT = True

BAD_LIST = []



def _check_image(imgpath):
    '''(str) -> bool, int, int
    Load an image and run some validation tests.
    Append errors to global BAD_LIST.

    Returns: True if image is valid else False, width, height

    '''
    global BAD_LIST

    img = PIL.Image.open(imgpath)
    valid = True
    errs = ['%s: ' % imgpath]
    w = 0; h = 0
    if img.format != 'JPEG':
        valid = False
        errs.append('Format was %s. Expected jpeg' % img.format)

    np_im = np.array(img)
    if len(np_im.shape) != 3:
        valid = False
        errs.append('Image had %s channels. Expected 3.' % len(np_im.shape))
    else:
        if np_im.shape[2] != 3:
            valid = False
            errs.append('Image had %s channels. Expected 3.' % len(np_im.shape[2]))
        else:
            h = np_im.shape[0]
            w = np_im.shape[1]

    if not valid:
        errs.append('\n')
        BAD_LIST.append(' | '.join(errs))

    return valid, w, h


def get_tf_example(img_path, xmin, ymin, xmax, ymax, width, height):
    """(str, int, int, int, int, int, int)
    Returns:
      example: The converted tf.Example.
    """
    img_path = os.path.normpath(img_path)
    with tf.gfile.GFile(img_path, 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    key = hashlib.sha256(encoded_jpg).hexdigest()

    xmins = []
    ymins = []
    xmaxs = []
    ymaxs = []
    classes = []
    classes_text = []
    truncated = []
    poses = []
    difficult_obj = []
    masks = []

    xmin = float(xmin)
    xmax = float(xmax)
    ymin = float(ymin)
    ymax = float(ymax)
    xmins.append(xmin / width)
    ymins.append(ymin / height)
    xmaxs.append(xmax / width)
    ymaxs.append(ymax / height)

    classes_text.append('bass'.encode('utf8'))
    classes.append(1)
    truncated.append(0)
    poses.append('Frontal'.encode('utf8'))
    difficult_obj.append(0)
    _, filename, _ = iolib.get_file_parts2(img_path)
    feature_dict = {
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename.encode('utf8')),
        'image/source_id': dataset_util.bytes_feature(filename.encode('utf8')),
        'image/key/sha256': dataset_util.bytes_feature(key.encode('utf8')),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature('jpeg'.encode('utf8')),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
        'image/object/difficult': dataset_util.int64_list_feature(difficult_obj),
        'image/object/truncated': dataset_util.int64_list_feature(truncated),
        'image/object/view': dataset_util.bytes_list_feature(poses),
    }
    example = tf.train.Example(features=tf.train.Features(feature=feature_dict))
    return example


# TODO(derekjchow): Add test for pet/PASCAL main files.
def main():
    '''entry'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('-d', '--delete', action='store_true', help='Delete tfrecord .record file(s) from the output folder.')
    cmdline.add_argument('-b', '--batch_sz', help='Batch size.', default=1)
    cmdline.add_argument('source_folder', help='The folder containing the images and vgg file')
    cmdline.add_argument('output_file', help='The TFRecord file to create')
    cmdline.add_argument('vgg_file_name', help='The filename of the vgg file, must be in source folder')

    args = cmdline.parse_args()
    batch_sz = int(args.batch_sz)
    assert batch_sz > 0, 'Batch size cannot be 0 or less'

    src = path.normpath(args.source_folder)
    out = path.normpath(args.output_file)
    fld, _, _ = iolib.get_file_parts(out)
    if args.delete:
        for f in iolib.file_list_generator1(fld, '*.record'):
            iolib.files_delete2(f)

    vgg_file = path.normpath(src + '/' + args.vgg_file_name)
    vgg.load_json(vgg_file)
    print('Loaded vgg file %s' % vgg_file)

    fld, _, _ = iolib.get_file_parts2(out)
    iolib.create_folder(fld)
    errout = path.normpath(path.join(fld, 'bad_image_files.csv'))

    if iolib.file_exists(out):
        print('Output TFRecord %s already exists. Delete it manually.' % out)
        return

    filecnt = sum(1 for x in vgg.roiGenerator(skip_imghdr_check=True, shape_type='rect'))
    PP.max = filecnt

    if batch_sz <= 1:
        nr_parts = 1
        writer = tf.python_io.TFRecordWriter(out)
    else:
        nr_parts = ceil(filecnt / batch_sz)
    first = True
    has_errs = False

    for imgpath, res, Reg in vgg.roiGenerator(skip_imghdr_check=True, shape_type='rect'):
        assert isinstance(Reg, vgg.Region)

        good, w, h = _check_image(imgpath)
        if not good:
            PP.increment()
            continue

        if nr_parts > 1:
            suffix = str(ceil(PP.iteration / batch_sz)).zfill(len(str(nr_parts)))
            fld, fname, ext = iolib.get_file_parts(out)
            fname = '%s-%s%s' % (fname, suffix, ext)
            batch_name = path.normpath(path.join(fld, fname))

            if PP.iteration % batch_sz == 1 and PP.iteration > 1:
                writer.close()
                writer = tf.python_io.TFRecordWriter(batch_name)
            elif first:
                writer = tf.python_io.TFRecordWriter(batch_name)
                first = False
        PP.increment()
        tf_example = get_tf_example(imgpath, Reg.x, Reg.y, Reg.x + Reg.w, Reg.y + Reg.h, w, h)


        #img = cv2.imread(imgpath)
        #pts = ((Reg.x, Reg.y), (Reg.x + Reg.w, Reg.y), (Reg.x, Reg.y + Reg.h), (Reg.x + Reg.w, Reg.y + Reg.h))
        #img = common.draw_points(pts, img)
        #show(img)

        if tf_example:
            writer.write(tf_example.SerializeToString())

    try:
        writer.close()
    except Exception as e:
        pass


    if has_errs:
        print('%s images had problems. See %s.' % (len(BAD_LIST), errout))
        iolib.writecsv(errout, BAD_LIST, inner_as_rows=False)

    # Test images are not included in the downloaded data set, so we shall
    # perform
    # our own split.



if __name__ == '__main__':
    main()
