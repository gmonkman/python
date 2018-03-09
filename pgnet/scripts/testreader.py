# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''test stuff'''
import tensorflow as tf


filename_queue = tf.train.string_input_producer(["C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/train.csv"])

reader = tf.TextLineReader()
key, value = reader.read(filename_queue)

# Default values, in case of empty columns. Also specifies the type of the
# decoded result.
record_defaults = [[''], [0], [0], [0]]
col1, col2, col3, col4 = tf.decode_csv(value, record_defaults=record_defaults)


with tf.Session() as sess:
  # Start populating the filename queue.
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)

    for i in range(10):
        #Retrieve single instance:
        example, label = sess.run([col1, col2])
        print(example, label)

    coord.request_stop()
    coord.join(threads)
