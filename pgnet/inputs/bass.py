#pylint: skip-file

"""Generate bass images"""
import os as _os

import tensorflow as _tf
import numpy as _np


import funclib.iolib as iolib
from . import image_processing as _image_processing
from . import pascal_trainval as pascal_trainval


CLASSES = ['bass', 'not_bass']
NUM_CLASSES = len(CLASSES)
BACKGROUND_CLASS_ID = len(CLASSES)

_POS_DIR = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/train/bass'
_NEG_DIR = 'C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/train/bass'

W = 514; H = 120
FRACTION_OF_SAMPLES_IN_QUEUE = 0.8
NUM_EXAMPLES_PER_EPOCH_FOR_EVAL = iolib.file_count([_POS_DIR, _NEG_DIR])
NUM_PREPROCESS_THREADS = 2


def read_csv(queue):
    """ Reads and parses files from the queue.

    Reads a single text line from a pascal text file

    Args:
        queue: A queue of strings in the format: file, width, height, label

    Returns:
        image_path: a tf.string tensor. The absolute path of the image in the dataset
        label: a int64 tensor with the label
        widht: a int64 tensor with the widht
        height: a int64 tensor with the height
    """

    # Reader for text lines
    reader = _tf.TextLineReader(skip_header_lines=0)

    # read a record from the queue
    _, row = reader.read(queue)

    # file,width,height,label
    record_defaults = [[""], [0], [0], [0]]

    image_path, label, width, height,  = _tf.decode_csv(row, record_defaults, field_delim=",")

    label = _tf.cast(label, _tf.int64)
    width = _tf.cast(width, _tf.int64)
    height = _tf.cast(height, _tf.int64)
    return image_path, label, width, height


def _generate_image_and_label_batch(image,
                                    label,
                                    min_queue_examples,
                                    batch_size,
                                    task='train'):
    """Construct a queued batch of images and labels.
    Args:
      image: 3-D Tensor of [input_side, input_side, 3] of type.float32.
      label: 1-D Tensor of type int64
      min_queue_examples: int64, minimum number of samples to retain
        in the queue that provides of batches of examples. The higher the most random (! important)
    batch_size: Number of images per batch.
    task: 'train' or 'validation'. In both cases use a shuffle queue
    Returns:
    images: Images. 4D tensor of [batch_size, input_side, input_side, 3] size.
    labels: Labels. 1D tensor of [batch_size] size.
    """
    assert task == 'train' or task == 'validation'

    # Create a queue that shuffles the examples, and then
    # read 'batch_size' images + labels from the example queue.
    images, sparse_labels = _tf.train.shuffle_batch([image, label],
        batch_size=batch_size,
        num_threads=NUM_PREPROCESS_THREADS,
        capacity=min_queue_examples + 3 * batch_size,
        min_after_dequeue=min_queue_examples)

    # Display the training images in the visualizer.
    # Add a scope to the summary.
    _tf.summary.image(task + '/images', images)

    return images, sparse_labels


def train(cropped_dataset_path,
          batch_size,
          input_side,
          csv_path=_os.path.abspath(_os.getcwd())):
    """Returns a batch of images from the train dataset.
    Applies random distortion to the examples.

    Args:
        cropped_dataset_path: path of the cropped pascal dataset
        batch_size: Number of images per batch.

        csv_path: path of train.csv
    Returns:
        images: Images. 4D tensor of [batch_size, input_side, input_side, 3 size.
        labes: Labels. 1D tensor of [batch_size] size.
    """
    # Create a queue that produces the filenames (and other atrributes) to read
    queue = _tf.train.string_input_producer(['C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/roi/train/file_list.csv'])

    # Read examples from the queue
    image_path, label, width, height = read_csv(queue)

    # read, random distortion, resize to input_side² and scale value between [-1,1]
    #distorted_image = _image_processing.train_image(image_path, width, height, input_side, image_type="jpg")
    distorted_image = _image_processing.read_image(image_path, channel=3, image_type="jpg")

    # Ensure that the random shuffling has good mixing properties.
    min_queue_examples = int(NUM_EXAMPLES_PER_EPOCH_FOR_TRAIN * FRACTION_OF_SAMPLES_IN_QUEUE)

    print('Filling queue with {} images prior to training ...'.format(min_queue_examples))
    return _generate_image_and_label_batch(distorted_image, label, min_queue_examples, batch_size, task='train')


def validation(cropped_dataset_path,
               batch_size,
               input_side,
               csv_path=_os.path.abspath(_os.getcwd())):
    """Returns a batch of images from the validation dataset

    Args:
        cropped_dataset_path: path of the cropped pascal dataset
        batch_size: Number of images per batch.
        input_side: resize images to shape [input_side, input_side, 3]
        csv_path: path of valdation.csv
    Returns:
        images: Images. 4D tensor of [batch_size, input_side, input_side, 3 size.
        labes: Labels. 1D tensor of [batch_size] size.
    """
    csv_path = csv_path.rstrip("/") + "/"

    queue = _tf.train.string_input_producer([csv_path + "validation.csv"])

    # Read examples from files in the filename queue.
    image_path, label, _, _ = read_csv(queue)

    # read, resize, scale between [-1,1]
    image = _image_processing.eval_image(image_path, input_side, image_type="jpg")

    # Ensure that the random shuffling has good mixing properties.
    fraction_of_examples_in_queue = 0.8
    min_queue_examples = int(NUM_EXAMPLES_PER_EPOCH_FOR_EVAL * fraction_of_examples_in_queue)

    # min_after_dequeue defines how big a buffer we will randomly sample
    #   from -- bigger means better shuffling but slower start up and more
    #   memory used.
    # capacity must be larger than min_after_dequeue and the amount larger
    #   determines the maximum we will prefetch.  Recommendation:
    #   min_after_dequeue + (num_threads + a small safety margin) * batch_size
    # Generate a batch of images and labels by building up a queue of examples.
    return _generate_image_and_label_batch(image, label, min_queue_examples, batch_size, task='validation')


def test(test_dataset_path,
         batch_size,
         input_side,
         file_list_path=_os.path.abspath(_os.getcwd())):
    """Returns a batch of images from the test dataset.

    Args:
        test_dataset_path: path of the test dataset
        batch_size: Number of images per batch.
        input_side: resize images to shape [input_side, input_side, 3]
        file_list_path: path (into the test dataset usually) where to find the list of file to read.
                        specify the filename and the path here, eg:
                         ~/data/PASCAL_2012/test/VOCdevkit/VOC2012/ImageSets/Main/test.txt
    Returns:
        images: Images. 4D tensor of [batch_size, input_side, input_side, 3] size.
        filenames: file names. [batch_size] tensor with the fileneme read. (without extension)
    """

    test_dataset_path = _os.path.abspath(_os.path.expanduser(test_dataset_path)).rstrip("/") + "/"

    # read every line in the file, only once
    queue = _tf.train.string_input_producer([file_list_path], num_epochs=1, shuffle=False)

    # Reader for text lines
    reader = _tf.TextLineReader()

    # read a record from the queue
    _, filename = reader.read(queue)

    image_path = test_dataset_path + _tf.constant("/JPEGImages/") + filename + _tf.constant(".jpg")

    # read, resize, scale between [-1,1]
    image = _image_processing.eval_image(image_path, input_side, image_type="jpg")

    # create a batch of images & filenames
    # (using a queue runner, that extracts image from the queue)
    images, filenames = _tf.train.batch([image, filename],
        batch_size,
        shapes=[[input_side, input_side, 3], []],
        num_threads=1,
        capacity=20000,
        enqueue_many=False)
    return images, filenames
