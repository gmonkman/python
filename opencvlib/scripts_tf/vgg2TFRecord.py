# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-import
'''
Create a TFRecord file from images and their assigned roi. This saves the whole image into the TFRecord file.

    -d: Delete all .record files in the output folder first
    -b: batch size, create multiple .record files with a size specified with the -b argument

    Positional args:
        source_folder, output_folder, vgg_file_name


Example:
    vgg2TFRecord.py -d -b 20 "C:\candidate" "C:\candidate\test.record" vgg_body.json

Comments:
    output_folder will be created if it doesn't exist
'''

import argparse
import os.path as path
import os
from math import ceil

from PIL import Image
import numpy as np
import tensorflow as tf

from object_detection.utils import dataset_util
import funclib.iolib as iolib
import funclib.stringslib as stringslib
import opencvlib.roi as roi
import opencvlib.imgpipes.vgg as vgg
from opencvlib.imgpipes.generators import VGGROI
import opencvlib.transforms as transforms
from opencvlib.view import show

PP = iolib.PrintProgress()
vgg.SILENT = True


def load_image(addr):
    img = Image.open(addr)
    return np.array(img).tostring()


def _bytes_feature(value):
    '''bytes feature'''
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def main():
    '''
    Rotate images

    Example:
    view_images.py part:head "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/angler/bass-angler.json"
    '''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('-d', '--delete', action='store_true', help='Delete tfrecord .record file(s) from the output folder.')
    cmdline.add_argument('-b', '--batch_sz', help='Batch size.', default=1)
    cmdline.add_argument('source_folder', help='The folder containing the images and vgg file')
    cmdline.add_argument('output_file', help='The TFRecord file to create')
    cmdline.add_argument('vgg_file_name', help='The filename of the vgg file, must be in source folder')

    args = cmdline.parse_args()
    batch_sz = int(args.batch_sz)
    assert batch_sz > 0, 'Shard size cannot be 0 or less'

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

    for imgpath, res, Reg in vgg.roiGenerator(skip_imghdr_check=True, shape_type='rect'):
        assert isinstance(Reg, vgg.Region)


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
        dummy, filename, ext = iolib.get_file_parts2(imgpath)
        encoded_image_data = load_image(imgpath)

        width = res[0]
        height = res[1]
        image_format = b'jpg'
        filename = filename.encode()
        xmins = [Reg.x / float(width)]
        xmaxs = [(Reg.x + Reg.w) / float(width)]
        ymins = [Reg.y / float(height)]
        ymaxs = [(Reg.y + Reg.h) / float(width)]
        classes_text = [b'bass']
        classes = [1]
        tf_example = tf.train.Example(features=tf.train.Features(feature={
            'image/height': dataset_util.int64_feature(height),
            'image/width': dataset_util.int64_feature(width),
            'image/filename': dataset_util.bytes_feature(filename),
            'image/source_id': dataset_util.bytes_feature(filename),
            'image/format': dataset_util.bytes_feature(image_format),
            'image/channels': dataset_util.int64_feature(3),
            'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
            'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
            'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
            'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
            'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
            'image/object/class/label': dataset_util.int64_list_feature(classes),
            'image/encoded': _bytes_feature(encoded_image_data)
        }))
        writer.write(tf_example.SerializeToString())

    try:
        writer.close()
    except Exception as e:
        pass




if __name__ == "__main__":
    main()
