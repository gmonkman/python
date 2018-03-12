# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument, unused-variable
#Adapted from Paolo Galeone <nessuno@nerdz.eu>
'''train'''
import argparse
import math
import os
from os import path
import sys
import time
from datetime import datetime

import numpy as np
import tensorflow as tf

from pgnet import model
from pgnet.inputs import bass


# graph parameteres
CURRENT_DIR = path.normpath(os.path.dirname(os.path.abspath(__file__)))
SESSION_DIR = path.normpath(CURRENT_DIR + "/session")
SUMMARY_DIR = path.normpath(CURRENT_DIR + "/summary")
MODEL_PATH = path.normpath(CURRENT_DIR + "/model.pb")

if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)
if not os.path.exists(SUMMARY_DIR):
    os.makedirs(SUMMARY_DIR)

BATCH_SIZE = 10

AVG_VALIDATION_ACCURACY_EPOCHS = 1  #stop when
AVG_VALIDATION_ACCURACIES = [0.0 for _ in range(AVG_VALIDATION_ACCURACY_EPOCHS)] # list of average validation at the end of every epoc

EPOCHS = 5
STEP_FOR_EPOCH = math.ceil(bass.BassTrain.image_count/BATCH_SIZE)
DISPLAY_STEP = math.ceil(STEP_FOR_EPOCH / 25)
MAX_ITERATIONS = STEP_FOR_EPOCH * 500
MEASUREMENT_STEP = DISPLAY_STEP
NUM_CLASSES = 2 + 1 # Number of classes in the dataset plus 1
SAVE_MODEL_STEP = math.ceil(STEP_FOR_EPOCH / 2) # tensorflow saver constant


bass.init_(batch_size=BATCH_SIZE, init=['BassTest', 'BassTrain', 'BassEval'])


def train(args):
    '''train'''
    if not os.path.exists(MODEL_PATH):
        graph = tf.Graph()

        with graph.as_default(), tf.device(args.device):

            with tf.variable_scope("train_input"): #open new context to share variables (layers)
                train_input_images = bass.DebugImages.Timages
                train_input_labels = bass.DebugImages.Tlabels
                train_image, train_label = tf.train.slice_input_producer([train_input_images, train_input_labels], num_epochs=EPOCHS) #produces 1 image per session.run
                train_image_batch, train_label_batch = tf.train.shuffle_batch([train_image, train_label], batch_size=BATCH_SIZE, num_threads=1, min_after_dequeue=10, capacity=100) #now _

            with tf.variable_scope("validation_input"):
                validation_images = bass.BassEval.Timages
                validation_labels = bass.BassEval.Tlabels
                validation_image, validation_label = tf.train.slice_input_producer([validation_images, validation_labels], num_epochs=EPOCHS)
                validation_image_batch, validation_label_batch = tf.train.shuffle_batch([validation_image, validation_label], batch_size=BATCH_SIZE, num_threads=1, min_after_dequeue=10, capacity=100)




            with tf.device(args.device):
                global_step = tf.Variable(0, trainable=False, name="global_step") # train global step
                labels_ = tf.placeholder(tf.int64, shape=[None], name="labels_") # model inputs, used in train and validation
                is_training_, keep_prob_, images_, logits = model.define(NUM_CLASSES, train_phase=True)
                loss_op = model.loss(logits, labels_)
                train_op = model.train(loss_op, global_step)

            summary_op = tf.summary.merge_all() # collect summaries for the previous defined variables

            with tf.variable_scope("accuracy"):
                # since pgnet is fully convolutional remove dimensions of size 1
                reshaped_logits = tf.squeeze(logits, [1, 2])

                # returns the label predicted
                # reshaped_logits contains NUM_CLASSES values in NUM_CLASSES
                # positions. Each value is the probability for the position class.
                # Returns the index (thus the label) with highest probability, for each line
                # [BATCH_SIZE] vector
                predictions = tf.argmax(reshaped_logits, 1)

                # correct predictions [BATCH_SIZE] vector
                correct_predictions = tf.equal(labels_, predictions)
                accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32), name="accuracy")

                # use a separate summary op for the accuracy (that's shared between test and validation

                # attach a summary to the placeholder
                train_accuracy_summary_op = tf.summary.scalar("train_accuracy", accuracy)
                validation_accuracy_summary_op = tf.summary.scalar("validation_accuracy", accuracy)

            # create a saver: to store current computation and restore the graph
            variables_to_save = model.variables_to_save([global_step])
            saver = tf.train.Saver(variables_to_save)

            init_op = tf.global_variables_initializer() # tensor flow operator to initialize all the variables in a session

            with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:


                def validate():
                    """get validation inputs and run validation.
                    Returns:
                        validation_accuracy, summary_line
                    """
                    validation_accuracy, summary_line = sess.run(
                        [accuracy, validation_accuracy_summary_op],
                        feed_dict={images_: validation_image_batch, labels_: validation_label_batch, keep_prob_: 1.0, is_training_: False,})
                    return validation_accuracy, summary_line

                sess.run([tf.initialize_all_variables(), tf.initialize_local_variables()])
                coord = tf.train.Coordinator()
                threads = tf.train.start_queue_runners(sess=sess, coord=coord)

                #region restore previous session if exists
                checkpoint = tf.train.get_checkpoint_state(SESSION_DIR)
                if checkpoint and checkpoint.model_checkpoint_path:
                    saver.restore(sess, checkpoint.model_checkpoint_path)
                else:
                    print("[I] Unable to restore from checkpoint")
                # endregion

                summary_writer = tf.summary.FileWriter(SUMMARY_DIR + "/train", graph=sess.graph)
                total_start = time.time()
                current_epoch = 0
                max_validation_accuracy = 0.0
                sum_validation_accuracy = 0.0

                #Main training loop
                for step in range(MAX_ITERATIONS):
                    train_images, train_labels = sess.run([images_ph, labels_ph]) # get train inputs

                    start = time.time()
                    # train, get loss value, get summaries
                    _, loss_val, summary_line, gs_value = sess.run(
                        [train_op, loss_op, summary_op, global_step],
                        feed_dict={keep_prob_: 0.4, is_training_: True, images_: train_images, labels_: train_labels},
                        )

                    duration = time.time() - start
                    summary_writer.add_summary(summary_line, global_step=gs_value) # save summary for current step

                    if np.isnan(loss_val):
                        print('Model diverged with loss = NaN', file=sys.stderr)
                        # print reshaped logits value for debug purposes
                        print(sess.run(reshaped_logits,
                                        feed_dict={keep_prob_: 1.0, is_training_: False, images_: train_images, labels_: train_labels}),
                                        file=sys.stderr
                                )
                        return 1

                    if step % DISPLAY_STEP == 0 and step > 0:
                        examples_per_sec = model.BATCH_SIZE / duration
                        sec_per_batch = float(duration)
                        print("{} step: {} loss: {} ({} examples/sec; {} batch/sec)".format(datetime.now(), gs_value, loss_val, examples_per_sec, sec_per_batch))

                    stop_training = False; save = False

                    if step % MEASUREMENT_STEP == 0 and step > 0:
                        validation_accuracy, summary_line = validate()
                        # save summary for validation_accuracy
                        summary_writer.add_summary(
                            summary_line, global_step=gs_value)

                        # test accuracy
                        test_accuracy, summary_line = sess.run(
                            [accuracy, train_accuracy_summary_op],
                            feed_dict={images_: train_images, labels_: train_labels, keep_prob_: 1.0, is_training_: False,
                            })

                        # save summary for training accuracy
                        summary_writer.add_summary(
                            summary_line, global_step=gs_value)

                        print(
                            "{} step: {} validation accuracy: {} training accuracy: {}".
                            format(datetime.now(), gs_value,
                                   validation_accuracy, test_accuracy))

                        sum_validation_accuracy += validation_accuracy

                        if validation_accuracy > max_validation_accuracy:
                            max_validation_accuracy = validation_accuracy
                            save = True

                    if step % STEP_FOR_EPOCH == 0 and step > 0:
                        # current validation accuracy
                        current_validation_accuracy = sum_validation_accuracy * MEASUREMENT_STEP / STEP_FOR_EPOCH
                        print("Epoch {} finised. Average validation accuracy/epoch: {}".format(current_epoch, current_validation_accuracy))

                        # sum previous avg accuracy
                        history_avg_accuracy = sum(AVG_VALIDATION_ACCURACIES) / AVG_VALIDATION_ACCURACY_EPOCHS

                        # if avg accuracy is not increased, after
                        # AVG_VALIDATION_ACCURACY_NOT_INCREASED_AFTER_EPOCH, exit
                        if current_validation_accuracy <= history_avg_accuracy:
                            print("Average validation accuracy not increased after {} epochs. Exit".format(AVG_VALIDATION_ACCURACY_EPOCHS))
                            # exit using stop_training flag, in order to save current status
                            stop_training = True

                        # save avg validation accuracy in the next slot
                        AVG_VALIDATION_ACCURACIES[current_epoch % AVG_VALIDATION_ACCURACY_EPOCHS] = current_validation_accuracy

                        current_epoch += 1
                        sum_validation_accuracy = 0.0

                    if step % SAVE_MODEL_STEP == 0 or (
                            step + 1) == MAX_ITERATIONS or stop_training:
                        # save the current session (until this step) in the session dir
                        # export a checkpint in the format SESSION_DIR/model-<global_step>.meta
                        # always pass 0 to global step in order to have only one file in the folder
                        saver.save(sess, SESSION_DIR + "/model", global_step=0)

                    if save:
                        # save the current session (until this step) in the session dir
                        # export a checkpint in the format SESSION_DIR/model-<global_step>.meta
                        saver.save(sess, SESSION_DIR + "/model-best", global_step=0)
                        print('Model with the highest validation accuracy saved.')

                    if stop_training:
                        break

                print("Train completed in {}".format(time.time() - total_start))
                summary_writer.flush() # save train summaries to disk
                coord.request_stop() # When done, ask the threads to stop.
                coord.join(threads) # Wait for threads to finish.

        # if here, the summary dir contains the trained model
        # save the model in the project root (parent dir)
        model.export(NUM_CLASSES, SESSION_DIR, "model-0", MODEL_PATH)
    else:
        print("Trained model {} already exits".format(MODEL_PATH))
    return 0


if __name__ == "__main__":
    ARG_PARSER = argparse.ArgumentParser(description="Train the model")
    ARG_PARSER.add_argument("--device", default="/cpu:1")
    sys.exit(train(ARG_PARSER.parse_args()))
