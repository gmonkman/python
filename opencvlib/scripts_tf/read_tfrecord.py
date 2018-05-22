'''testing reading a tf record'''

import tensorflow as tf
import numpy as np

from opencvlib.view import show
from opencvlib.transforms import chswap

reader = tf.TFRecordReader()


#record_iterator = tf.python_io.tf_record_iterator(path='C:/development/python/opencvlib/scripts_tf/bin/test.record')

record_iterator = tf.python_io.tf_record_iterator(path='C:/tf/data/train-01.record')
for string_record in record_iterator:
    example = tf.train.Example()
    example.ParseFromString(string_record)

    height = int(example.features.feature['image/height'].int64_list.value[0])
    width = int(example.features.feature['image/width'].int64_list.value[0])
    img_string = (example.features.feature['image/encoded'].bytes_list.value[0])

    img_1d = np.fromstring(img_string, dtype=np.uint8)
    reconstructed_img = img_1d.reshape((height, width, 3))

    #loaded as rgb, but show uses cv2, expects BGR
    reconstructed_img = chswap(reconstructed_img, (2, 1, 0))
    show(reconstructed_img)
