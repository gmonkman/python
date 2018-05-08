# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
#Adapted from Paolo Galeone <nessuno@nerdz.eu>
'''pgnet train'''
import argparse
import math
import os
from os import path
import sys
from pysimplelog import Logger

import numpy as np
import tensorflow as tf

from funclib.baselib import list_get_unique as _lstunq
from opencvlib.stopwatch import StopWatch
from pgnet import model
from pgnet.inputs import bass
import pgnet.ini as _ini
from funclib.iolib import files_delete2


# graph parameteres
CURRENT_DIR = path.normpath(os.path.dirname(os.path.abspath(__file__)))
SESSION_DIR = path.normpath(CURRENT_DIR + "/session")
SUMMARY_DIR = path.normpath(CURRENT_DIR + "/summary")
MODEL_PATH = path.normpath(CURRENT_DIR + "/model.pb")

if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)
if not os.path.exists(SUMMARY_DIR):
    os.makedirs(SUMMARY_DIR)


BATCH_SIZE = int(_ini.Cfg.tryread('train.py', 'BATCH_SIZE', value_on_create=10))
EPOCHS = int(_ini.Cfg.tryread('train.py', 'EPOCHS', value_on_create=1))
SHUFFLE_QUEUE_BUFFER_SIZE = int(_ini.Cfg.tryread('train.py', 'SHUFFLE_QUEUE_BUFFER_SIZE', value_on_create=100))
SAVE_EVERY_N_STEP = int(_ini.Cfg.tryread('train.py', 'SAVE_EVERY_N_STEP', value_on_create=1))

LOG_FILE = _ini.Cfg.tryread('train.py', 'LOG_FILE', os.path.normpath(os.path.join(CURRENT_DIR, 'train.py.log')))
files_delete2(LOG_FILE)
Log = Logger(name='train', logToStdout=False, logToFile=True, logFileMaxSize=1)
Log.set_log_file(LOG_FILE)


AVG_VALIDATION_ACCURACY_EPOCHS = 1  #stop when
EPOCH_VALIDATION_ACCURACIES = []

#these are placeholders, values assigned in set_params()
STEPS_PER_EPOCH = 0 #number of steps in EPOCH
TOTAL_STEPS = 0
MAX_ITERATIONS = 0
NUM_CLASSES = 2 #bass, not bass



def set_params():
    '''set global params after module bass
    has been initialized so we know
    train pic numbers'''
    global STEPS_PER_EPOCH
    STEPS_PER_EPOCH = math.ceil(bass.BassTrain.image_count/BATCH_SIZE)
    global TOTAL_STEPS
    TOTAL_STEPS = EPOCHS * STEPS_PER_EPOCH


def img_get(filename, label):
    '''(V:str, V:int64, PH:bool) -> V:ndarray, V:int64

    Load image from filename, return corresponding label
    untouched. If placeholder apply_distortion_ is
    True, then distort the image.

    filename:
        a string tensor filepath pointer, e.g. 'C:/myimg.jpg'
    label:
        a tensor of int64, label for filename
    apply_distortion_
        apply a distortion or not
    '''
    #TODO apply stanardiszation using the whole training set
    #https://stats.stackexchange.com/questions/322802/per-image-normalization-vs-overall-dataset-normalization
    #https://www.tensorflow.org/api_docs/python/tf/image/per_image_standardization
    #apply_distortion = tf.placeholder(dtype=tf.bool, shape=[1], name='apply_distortion')
    image_string = tf.read_file(filename)
    image_decoded = tf.image.decode_image(image_string)
    image_decoded.set_shape([bass.H_ORIG, bass.W_ORIG, bass.CH_ORIG])
    #resize image
    image_rsz = tf.expand_dims(image_decoded, 0)
    image_rsz = tf.image.resize_bilinear(image_rsz, [bass.H, bass.W], align_corners=False) # now image is 4-D float32 tensor: [1, side, side, image.depth]
    image_rsz = tf.squeeze(image_rsz, [0])
    img_standardized = img_std(image_rsz/255.0) #-1 to 1, not strictly a standardization
    return img_standardized, label


def log(args, msg):
    '''(argparse.parse, str) -> void
    '''
    if args.log == 'yes':
        Log.info(msg)
    else:
        print(msg)


def img_std(image):
    '''(tensor) -> tensor
    Rescale image to float (-1 to 1)
    '''
    #image = tf.image.per_image_standardization(image)
    # rescale to [-1,1] instead of [0, 1)
    return tf.multiply(tf.subtract(image, 0.5), 2)


def train(args):
    '''train'''
    log(args, '\nInifile settings')
    log(args, 'BATCH_SIZE: %s, EPOCHS: %s, SHUFFLE_QUEUE_BUFFER_SIZE: %s, SAVE_EVERY_N_STEP: %s' % (BATCH_SIZE, EPOCHS, SHUFFLE_QUEUE_BUFFER_SIZE, SAVE_EVERY_N_STEP))

    bass.init_(batch_size=BATCH_SIZE, init=['BassTest', 'BassTrain', 'BassEval'])
    set_params()


    if not os.path.exists(MODEL_PATH):
        graph = tf.Graph()

        with graph.as_default():
            with tf.variable_scope("train_input"): #open new context to share variables (layers)
                dsTrain = tf.data.Dataset.from_tensor_slices((bass.BassTrain.img_paths, bass.BassTrain.labels))
                dsTrain = dsTrain.map(img_get)
                dsTrain = dsTrain.shuffle(buffer_size=SHUFFLE_QUEUE_BUFFER_SIZE, reshuffle_each_iteration=True)
                dsTrain = dsTrain.batch(BATCH_SIZE) #batch
                dsTrain = dsTrain.repeat(EPOCHS) #epochs
                train_iter = dsTrain.make_one_shot_iterator()
                train_images_batch, train_labels_batch = train_iter.get_next()
                train_labels_batch = tf.cast(train_labels_batch, tf.int64)


            with tf.variable_scope("validation_input"):
                dsValidation = tf.data.Dataset.from_tensor_slices((bass.BassTrain.img_paths, bass.BassTrain.labels))
                dsValidation = dsValidation.map(img_get)
                dsValidation = dsValidation.shuffle(buffer_size=SHUFFLE_QUEUE_BUFFER_SIZE, reshuffle_each_iteration=True)
                dsValidation = dsValidation.batch(BATCH_SIZE) #batch
                dsValidation = dsValidation.repeat(EPOCHS) #epochs
                validation_iter = dsValidation.make_one_shot_iterator()
                validation_images_batch, validation_labels_batch = validation_iter.get_next()
                validation_labels_batch = tf.cast(validation_labels_batch, tf.int64)


            global_step = tf.Variable(0, trainable=False, name="global_step") # train global step
            labels_ = tf.placeholder(tf.int64, shape=[None], name="labels_") # model inputs, used in train and validation
            is_training_, keep_prob_, images_, logits = model.define(NUM_CLASSES, train_phase=True)
            loss_op = model.loss(logits, labels_)
            train_op = model.train(loss_op, global_step)

            summary_op = tf.summary.merge_all() # collect summaries for the previous defined variables

            with tf.variable_scope("accuracy"):
                reshaped_logits = tf.squeeze(logits, [1, 2])
                predictions = tf.argmax(reshaped_logits, 1) #index with largest probablity
                correct_predictions = tf.equal(labels_, predictions) #true if prediction was correct, else false, for each item in batch, returns [BATCH_SIZE] vector
                accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32), name="accuracy") #proportion of correct predictions in the batch, ie 5 right of 10 would be 0.5

                # use a separate summary op for the accuracy (that's shared between test and validation
                # attach a summary to the placeholder
                train_accuracy_summary_op = tf.summary.scalar("train_accuracy", accuracy)
                validation_accuracy_summary_op = tf.summary.scalar("validation_accuracy", accuracy)

            # create a saver: to store current computation and restore the graph
            variables_to_save = model.variables_to_save([global_step])
            variables_to_save = _lstunq(variables_to_save) #fudge to remove dups
            saver = tf.train.Saver(variables_to_save)

            with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:
                sess.run([tf.global_variables_initializer(), tf.local_variables_initializer()])

                def validate():
                    '''validation data'''
                    np_validation_imgs = validation_images_batch.eval()
                    np_validation_lbls = validation_labels_batch.eval()
                    validation_accuracy, summary_line = sess.run([accuracy, validation_accuracy_summary_op],
                        feed_dict={keep_prob_: 1.0, images_:np_validation_imgs, labels_:np_validation_lbls, is_training_:False,})
                    return validation_accuracy, summary_line


                #region restore previous session if exists
                checkpoint = tf.train.get_checkpoint_state(SESSION_DIR)
                if checkpoint and checkpoint.model_checkpoint_path:
                    saver.restore(sess, checkpoint.model_checkpoint_path)
                else:
                    log(args, "[I] Unable to restore from checkpoint")
                # endregion

                summary_writer = tf.summary.FileWriter(path.normpath(path.join(SUMMARY_DIR, "train")), graph=sess.graph)

                current_epoch = 1
                max_validation_accuracy = 0.0
                sum_validation_accuracy = 0.0
                watch = StopWatch(qsize=10, event_name='step')
                try:
                    #Main training loop
                    for step in range(1, STEPS_PER_EPOCH * EPOCHS + 1):
                        stop_training = False; save = False
                        nd_train_imgs = train_images_batch.eval()
                        nd_train_lbls = train_labels_batch.eval()

                        _, loss_val, summary_line, gs_value = sess.run([train_op, loss_op, summary_op, global_step], feed_dict={keep_prob_: 0.4, is_training_: True, images_:nd_train_imgs, labels_:nd_train_lbls})
                        summary_writer.add_summary(summary_line, global_step=gs_value)

                        if np.isnan(loss_val):
                            log(args, 'Model diverged with loss = NaN')
                            s = str(sess.run(reshaped_logits, feed_dict={keep_prob_: 1.0, is_training_: False, images_:nd_train_imgs, labels_:nd_train_lbls}, file=sys.stderr))
                            log(args, s)
                            return 1

                        validation_accuracy, summary_line = validate()
                        summary_writer.add_summary(summary_line, global_step=gs_value)
                        train_accuracy, summary_line = sess.run([accuracy, train_accuracy_summary_op], feed_dict={images_:nd_train_imgs, labels_:nd_train_lbls, keep_prob_: 1.0, is_training_: False,})
                        summary_writer.add_summary(summary_line, global_step=gs_value)
                        watch.lap()
                        remain_total_steps = STEPS_PER_EPOCH - step    +  (EPOCHS - current_epoch) * STEPS_PER_EPOCH
                        time_left_seconds = watch.remaining(remain_total_steps)

                        txt_progress = '%s >> Step %s of %s in Epoch %s of %s' % (watch.pretty_now(), step, STEPS_PER_EPOCH, current_epoch, EPOCHS)
                        txt_step = 'A step takes %s' % watch.pretty_time(watch.event_rate_smoothed)
                        txt_epoch = 'An epoch is estimated to take %s' %  watch.pretty_time(watch.remaining(TOTAL_STEPS) / EPOCHS)
                        txt_time_left = 'Maximum time remaining is %s' % watch.pretty_time(time_left_seconds)
                        txt_loss = 'Loss >> %0.3f' % loss_val
                        txt_accuracy = 'Batch accuracy >> train: %0.3f, validation: %0.3f' % (train_accuracy, validation_accuracy)
                        log(args, '\n---------------')
                        log(args, txt_progress)
                        log(args, txt_step)
                        log(args, txt_epoch)
                        log(args, txt_time_left)
                        log(args, '.......')
                        log(args, txt_loss)
                        log(args, txt_accuracy)
                        log(args, '---------------')

                        sum_validation_accuracy += validation_accuracy
                        if validation_accuracy > max_validation_accuracy:
                            max_validation_accuracy = validation_accuracy
                            save = True


                        if step % STEPS_PER_EPOCH == 0 and step > 0: #END OF AN EPOCH
                            mean_validation_accuracy = sum_validation_accuracy / STEPS_PER_EPOCH
                            EPOCH_VALIDATION_ACCURACIES.append(mean_validation_accuracy)
                            log(args, "Epoch {} finised. Mean validation accuracy: {}".format(current_epoch, mean_validation_accuracy))

                            if len(EPOCH_VALIDATION_ACCURACIES) > 1:
                                if mean_validation_accuracy < sum(EPOCH_VALIDATION_ACCURACIES)/len(EPOCH_VALIDATION_ACCURACIES):
                                    log(args, "Last epoch did not increase average validation accuracy. Stopping.")
                                    stop_training = True

                            current_epoch += 1
                            sum_validation_accuracy = 0.0

                        if step % SAVE_EVERY_N_STEP == 0:
                            _ = saver.save(sess, path.normpath(SESSION_DIR + "/model.ckpt"))

                        if save:
                            _ = saver.save(sess, path.normpath(SESSION_DIR + "/model-best.ckpt"))
                            log(args, 'Model with the highest validation accuracy saved.')


                        if stop_training:
                            raise StopIteration

                except (tf.errors.OutOfRangeError, StopIteration) as e:
                    #model.export(NUM_CLASSES, SESSION_DIR, "model-0", MODEL_PATH)
                    #this export creates a transferable file, known as a GraphDef, it wont generally be needed.
                    #See https://www.tensorflow.org/mobile/prepare_models
                    log(args, "Train completed in %s" % watch.pretty_time(watch.run_time))
                except Exception as e:
                    log(args, print(e))
                finally:
                    summary_writer.flush() # save train summaries to disk

    else:
        log(args, "Trained model {} already exits".format(MODEL_PATH))
    return 0


if __name__ == "__main__":
    ARG_PARSER = argparse.ArgumentParser(description="Train the model")
    ARG_PARSER.add_argument("--device", default="/cpu:0")
    ARG_PARSER.add_argument("--log", default="no")
    train(ARG_PARSER.parse_args())

    sys.exit()
