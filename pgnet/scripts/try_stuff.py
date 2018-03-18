# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, missing-docstring
'''mucking around with basic TF stuff'''
import tensorflow as tf

import pgnet.inputs.bass as bass
#import numpy as np

def op1(n, m):
    '''mul'''
    #op1_var = tf.get_variable('op1_var', shape=[1], dtype=tf.float64, initializer=tf.constant_initializer(5, dtype=tf.float64))
    return tf.subtract(n, m)


def op2(a, b):
    '''add'''
    #op2_var = tf.get_variable('op2_var', shape=[1], dtype=tf.float64, initializer=tf.constant_initializer(12, dtype=tf.float64))
    return tf.add(a, b)




def main():
    '''start'''
    graph = tf.Graph()
    with  graph.as_default(), tf.device("/cpu:0"):
        a = tf.placeholder(dtype=tf.float64, shape=[1])
        b = tf.placeholder(dtype=tf.float64, shape=[1])
       # n = tf.placeholder(dtype=tf.float64, shape=[1])
       # m = tf.placeholder(dtype=tf.float64, shape=[1])
      #  ta = tf.get_variable('ta', shape=[1], dtype=tf.float64, initializer=tf.constant_initializer(12, dtype=tf.float64))
       # tb = tf.get_variable('tb', shape=[1], dtype=tf.float64, initializer=tf.constant_initializer(12, dtype=tf.float64))

        init_op = [tf.global_variables_initializer(), tf.local_variables_initializer()]

        #op_ = tf.add(a, b)
        #op2_ = tf.subtract(n, m)
       # ta = [10]
       # tb = [20]
        with tf.Session() as sess:
            assert isinstance(sess, tf.Session)
            sess.run(init_op)
            print(sess.run([op2(a, b)], feed_dict={a:[10], b:[20]}))
            #print(tf.trainable_variables())
            #print(tf.global_variables())


def image_decode(filename, label):
    image_string = tf.read_file(filename)
    image_decoded = tf.image.decode_image(image_string)
    image_resized = tf.image.resize_images(image_decoded, [200, 200])
    return image_resized, label


def try_dataset():
    ds_imglbl = tf.data.Dataset.from_tensor_slices((bass.BassTrain.img_paths, bass.BassTrain.labels))
    ds_imglbl = ds_imglbl.map(image_decode)
    ds_imglbl = ds_imglbl.shuffle(buffer_size=100, reshuffle_each_iteration=True)
    ds_imglbl = ds_imglbl.batch(3) #batch
    ds_imglbl = ds_imglbl.repeat(1) #epochs
    iter_ = ds_imglbl.make_one_shot_iterator()

    imgs, lbls = iter_.get_next()


    with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:
        sess.run([tf.global_variables_initializer(), tf.local_variables_initializer()])
        for _ in range(100):
            print(sess.run(lbls, type(imgs)))



if __name__ == "__main__":
    try_dataset()
    #main()
