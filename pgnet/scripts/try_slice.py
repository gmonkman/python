# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''test tf slice feed with feed_dict'''
#import os.path as _path


import tensorflow as tf
#import tensorflow.contrib.eager as tfe
#tfe.enable_eager_execution()


import funclib.iolib as iolib
#import opencvlib

import pgnet.inputs.bass as bass

bass.init_(batch_size=10, init='DebugImages')

nd_imgs = bass.DebugImages.ndimages
nd_lbls = bass.DebugImages.ndlabels
#_ = iolib.wait_key('press any key to continue')

with tf.Graph().as_default():
    with tf.name_scope('input'):
        input_images = bass.DebugImages.Timages
        input_labels = bass.DebugImages.Tlabels

    image, label = tf.train.slice_input_producer([input_images, input_labels], num_epochs=100)

    assert isinstance(image, tf.Tensor)
    assert isinstance(label, tf.Tensor)

    image_, label_ = tf.train.shuffle_batch([image, label], batch_size=10, num_threads=2, min_after_dequeue=10, capacity=1000)

    sum_img = tf.reduce_sum(image_)
    sum_lbl = tf.reduce_sum(label_)

    with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:
        assert isinstance(sess, tf.Session)
        sess.run([tf.initialize_all_variables(), tf.initialize_local_variables()])

        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(sess=sess, coord=coord)

        try:
            for step in range(1000):
                if coord.should_stop():
                    break
                sess.run(image_)
                sess.run(label_)
                print(sess.run(sum_img), sess.run(sum_lbl))
                if step % 100 == 0:
                    print('Step %s' % step, end='\r')
        except tf.errors.OutOfRangeError as e:
            #end of queue
            coord.request_stop(e)
        finally:
            coord.join(threads)
            sess.close()
