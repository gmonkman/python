# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
#Adapted from Paolo Galeone <nessuno@nerdz.eu>
'''pgnet train'''
import argparse
import math
import os
from os import path
import sys
import time
from datetime import timedelta
from datetime import datetime


import numpy as np
import tensorflow as tf

from funclib.baselib import list_get_unique as _lstunq
from pgnet import model
from pgnet.inputs import bass
import pgnet.ini as _ini


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

AVG_VALIDATION_ACCURACY_EPOCHS = 1  #stop when
AVG_VALIDATION_ACCURACIES = [0.0 for _ in range(AVG_VALIDATION_ACCURACY_EPOCHS)] # list of average validation at the end of every epoc

STEP_FOR_EPOCH = 0
DISPLAY_STEP = 0
MAX_ITERATIONS = 0
MEASUREMENT_STEP = DISPLAY_STEP
NUM_CLASSES = 2 #bass, not bass
SAVE_MODEL_STEP = 0



def set_params():
    '''set global params after module bass
    has been initialized so we know
    train pic numbers'''
    global STEP_FOR_EPOCH
    STEP_FOR_EPOCH = math.ceil(bass.BassTrain.image_count/BATCH_SIZE)
    global DISPLAY_STEP
    DISPLAY_STEP = math.ceil(STEP_FOR_EPOCH / 25)
    global MAX_ITERATIONS
    MAX_ITERATIONS = STEP_FOR_EPOCH * 500
    global MEASUREMENT_STEP
    MEASUREMENT_STEP = DISPLAY_STEP
    global SAVE_MODEL_STEP
    SAVE_MODEL_STEP = math.ceil(STEP_FOR_EPOCH / 2) # tensorflow saver constant


def train(args):
    '''train'''
    bass.init_(batch_size=BATCH_SIZE, init=['BassTest', 'BassTrain', 'BassEval'])
    set_params()

    if not os.path.exists(MODEL_PATH):
        graph = tf.Graph()

        with graph.as_default(), tf.device(args.device):

            with tf.variable_scope("train_input"): #open new context to share variables (layers)
                train_input_images = bass.BassTrain.Timages #these are constants
                train_input_labels = bass.BassTrain.Tlabels
                train_image, train_label = tf.train.slice_input_producer([train_input_images, train_input_labels], num_epochs=EPOCHS) #produces 1 image per session.run
                train_images_batch, train_labels_batch = tf.train.shuffle_batch([train_image, train_label], batch_size=BATCH_SIZE, num_threads=1, min_after_dequeue=10, capacity=100)
                train_labels_batch = tf.cast(train_labels_batch, tf.int64)


            with tf.variable_scope("validation_input"):
                validation_images = bass.BassEval.Timages
                validation_labels = bass.BassEval.Tlabels
                validation_image, validation_label = tf.train.slice_input_producer([validation_images, validation_labels], num_epochs=EPOCHS)
                validation_images_batch, validation_labels_batch = tf.train.shuffle_batch([validation_image, validation_label], batch_size=BATCH_SIZE, num_threads=1, min_after_dequeue=10, capacity=100)
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
                coord = tf.train.Coordinator()
                threads = tf.train.start_queue_runners(sess=sess, coord=coord)

                def validate():
                    '''validation data'''
                    np_validation_imgs = validation_images_batch.eval()
                    np_validation_lbls = validation_labels_batch.eval()
                    validation_accuracy, summary_line = sess.run([accuracy, validation_accuracy_summary_op],
                        feed_dict={keep_prob_: 1.0, images_:np_validation_imgs, labels_:np_validation_lbls, is_training_: False,})
                    return validation_accuracy, summary_line


                #region restore previous session if exists
                checkpoint = tf.train.get_checkpoint_state(SESSION_DIR)
                if checkpoint and checkpoint.model_checkpoint_path:
                    saver.restore(sess, checkpoint.model_checkpoint_path)
                else:
                    print("[I] Unable to restore from checkpoint")
                # endregion

                summary_writer = tf.summary.FileWriter(path.normpath(path.join(SUMMARY_DIR, "train")), graph=sess.graph)
                total_start = time.time()
                current_epoch = 0
                max_validation_accuracy = 0.0
                sum_validation_accuracy = 0.0

                try:
                    #Main training loop
                    for step in range(MAX_ITERATIONS):
                        start = time.time()
                        # train, get loss value, get summaries
                        nd_train_imgs = train_images_batch.eval()
                        nd_train_lbls = train_labels_batch.eval()

                        _, loss_val, summary_line, gs_value = sess.run([train_op, loss_op, summary_op, global_step], feed_dict={keep_prob_: 0.4, is_training_: True, images_:nd_train_imgs, labels_:nd_train_lbls})

                        duration = time.time() - start
                        summary_writer.add_summary(summary_line, global_step=gs_value) # save summary for current step

                        if np.isnan(loss_val):
                            print('Model diverged with loss = NaN', file=sys.stderr)
                            # print reshaped logits value for debug purposes
                            print(sess.run(reshaped_logits, feed_dict={keep_prob_: 1.0, is_training_: False, images_:nd_train_imgs, labels_:nd_train_lbls}, file=sys.stderr))
                            return 1

                        if step % DISPLAY_STEP == 0 and step > 0:
                            examples_per_sec = model.BATCH_SIZE / duration
                            sec_per_batch = float(duration)
                            print("{} step: {} loss: {} ({} examples/sec; {} batch/sec)".format(datetime.now(), gs_value, loss_val, examples_per_sec, sec_per_batch))

                        stop_training = False; save = False

                        if step % MEASUREMENT_STEP == 0 and step > 0:
                            validation_accuracy, summary_line = validate()
                            # save summary for validation_accuracy
                            summary_writer.add_summary(summary_line, global_step=gs_value)

                            # test accuracy
                            test_accuracy, summary_line = sess.run([accuracy, train_accuracy_summary_op], feed_dict={images_:nd_train_imgs, labels_:nd_train_lbls, keep_prob_: 1.0, is_training_: False,})
                            # save summary for training accuracy
                            summary_writer.add_summary(summary_line, global_step=gs_value)

                            print("{} step: {} validation accuracy: {} training accuracy: {}".format(datetime.now(), gs_value, validation_accuracy, test_accuracy))

                            sum_validation_accuracy += validation_accuracy
                            if validation_accuracy > max_validation_accuracy:
                                max_validation_accuracy = validation_accuracy
                                save = True

                        if step % STEP_FOR_EPOCH == 0 and step > 0:
                            current_validation_accuracy = sum_validation_accuracy * MEASUREMENT_STEP / STEP_FOR_EPOCH
                            print("Epoch {} finised. Average validation accuracy/epoch: {}".format(current_epoch, current_validation_accuracy))

                            # sum previous avg accuracy
                            history_avg_accuracy = sum(AVG_VALIDATION_ACCURACIES) / AVG_VALIDATION_ACCURACY_EPOCHS

                            if current_validation_accuracy <= history_avg_accuracy:
                                print("Average validation accuracy not increased after {} epochs. Exit".format(AVG_VALIDATION_ACCURACY_EPOCHS))
                                stop_training = True

                            # save avg validation accuracy in the next slot
                            AVG_VALIDATION_ACCURACIES[current_epoch % AVG_VALIDATION_ACCURACY_EPOCHS] = current_validation_accuracy

                            current_epoch += 1
                            sum_validation_accuracy = 0.0

                        if step % SAVE_MODEL_STEP == 0 or (step + 1) == MAX_ITERATIONS or stop_training:
                            _ = saver.save(sess, path.normpath(SESSION_DIR + "/model.ckpt"))

                        if save:
                            _ = saver.save(sess, path.normpath(SESSION_DIR + "/model-best.ckpt"))
                            print('Model with the highest validation accuracy saved.')

                        if stop_training:
                            raise StopIteration

                except (tf.errors.OutOfRangeError, StopIteration) as e:
                    #model.export(NUM_CLASSES, SESSION_DIR, "model-0", MODEL_PATH)
                    #this export creates a transferable file, known as a GraphDef, it wont generally be needed.
                    #See https://www.tensorflow.org/mobile/prepare_models
                    print("Train completed in %s" % str(timedelta(seconds=time.time() - total_start)))
                except Exception as e:
                    print(e)
                finally:
                    summary_writer.flush() # save train summaries to disk
                    coord.request_stop() # When done, ask the threads to stop.
                    coord.join(threads) # Wait for threads to finish.

    else:
        print("Trained model {} already exits".format(MODEL_PATH))
    return 0


if __name__ == "__main__":
    ARG_PARSER = argparse.ArgumentParser(description="Train the model")
    ARG_PARSER.add_argument("--device", default="/cpu:1")
    sys.exit(train(ARG_PARSER.parse_args()))
