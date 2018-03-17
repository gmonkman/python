# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''mucking around with basic TF stuff'''
import tensorflow as tf
import numpy as np

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
        n = tf.placeholder(dtype=tf.float64, shape=[1])
        m = tf.placeholder(dtype=tf.float64, shape=[1])
      #  ta = tf.get_variable('ta', shape=[1], dtype=tf.float64, initializer=tf.constant_initializer(12, dtype=tf.float64))
       # tb = tf.get_variable('tb', shape=[1], dtype=tf.float64, initializer=tf.constant_initializer(12, dtype=tf.float64))

        init_op = [tf.global_variables_initializer(), tf.local_variables_initializer()]

        #op_ = tf.add(a, b)
        #op2_ = tf.subtract(n, m)
        ta = [10]
        tb = [20]
        with tf.Session() as sess:
            assert isinstance(sess, tf.Session)
            sess.run(init_op)

            print(sess.run([op2(a, b)], feed_dict={a:[10], b:[20]}))


            #print(tf.trainable_variables())
            #print(tf.global_variables())


if __name__ == "__main__":
    main()
