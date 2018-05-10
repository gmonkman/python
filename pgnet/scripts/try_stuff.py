#pylint: skip-file

'''mucking around with basic TF stuff'''
import os
import tensorflow as tf
import pgnet.inputs.bass as bass
import numpy as np
import funclib.iolib as iolib
import funclib.stringslib as stringslib


CURRENT_DIR = 'c:/temp/tf/'
SESSION_DIR = os.path.normpath('c:/temp/tf/session')
SUMMARY_DIR = os.path.normpath('c:/temp/tf/summary')
MODEL_PATH = os.path.normpath('c:/temp/tf/model.pb')


def img_get(filename, label):
    '''(V:str, V:int64, PH:bool) -> V:ndarray, V:int64'''
    image_string = tf.read_file(filename)
    image_decoded = tf.image.decode_image(image_string)
    image_decoded.set_shape([bass.H_ORIG, bass.W_ORIG, bass.CH_ORIG])
    #resize image
    image_rsz = tf.expand_dims(image_decoded, 0)
    image_rsz = tf.image.resize_bilinear(image_rsz, [bass.H, bass.W], align_corners=False) # now image is 4-D float32 tensor: [1, side, side, image.depth]
    image_rsz = tf.squeeze(image_rsz, [0])
    img_standardized = img_std(image_rsz/255.0) #-1 to 1, not strictly a standardization
    return img_standardized, label


def img_std(image):
    '''(tensor) -> tensor
    Rescale image to float (-1 to 1)
    '''
    return tf.multiply(tf.subtract(image, 0.5), 2)


def try_dataset():
    graph = tf.Graph()
    with graph.as_default():
        labels_ = tf.placeholder(tf.int64, shape=[None], name="labels_")

        img_paths=[r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\train\train\bass\001.jpg',
                   r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\train\train\bass\002.jpg',
                   r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\train\train\bass\003.jpg',
                   r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\train\train\bass\006.jpg',
                   r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\train\train\bass\007.jpg',
                   r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\train\train\bass\008.jpg',
                   r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\train\train\bass\009.jpg',
                   r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\train\train\bass\011.jpg',
                   r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\train\train\bass\016.jpg',
                   r'C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\train\train\bass\017.jpg',
                   'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/train/not_bass/0019.jpg',
                    'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/train/not_bass/0004.jpg',
                    'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/train/not_bass/0005.jpg',
                    'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/train/not_bass/0008.jpg',
                    'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/train/not_bass/0009.jpg',
                    'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/train/not_bass/0010.jpg',
                    'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/train/not_bass/0011.jpg',
                    'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/train/not_bass/0014.jpg',
                    'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/train/not_bass/0017.jpg',
                    'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/train/not_bass/0018.jpg'
                   ]

        labels = [1]* 10
        labels.extend([0] * 10)

        with tf.variable_scope("train_input"): #open new context to share variables (layers)
            dsTrain = tf.data.Dataset.from_tensor_slices((img_paths, labels))
            dsTrain = dsTrain.map(img_get)
            dsTrain = dsTrain.shuffle(buffer_size=1, reshuffle_each_iteration=True)
            dsTrain = dsTrain.batch(1) #batch
            dsTrain = dsTrain.repeat() #epochs
            train_iter = dsTrain.make_one_shot_iterator()
            train_images_batch, train_labels_batch = train_iter.get_next()
            assert isinstance(train_images_batch, tf.Tensor)
            train_labels_batch = tf.cast(train_labels_batch, tf.int64)

        with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:
            writer = tf.summary.FileWriter(SUMMARY_DIR, graph)
            sess.run([tf.global_variables_initializer(), tf.local_variables_initializer()])
            for n in range(20):
                img = np.array(train_images_batch.eval())
                lbl = np.array(train_labels_batch.eval())
                img.dump('C:/temp/tf/input_as_np/img%s.np' % n)
                lbl.dump('C:/temp/tf/input_as_np/lbl%s.np' % n)
            writer.close()


if __name__ == "__main__":
    try_dataset()
    #main()
