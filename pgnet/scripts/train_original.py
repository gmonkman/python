#pylint: skip-file
#Copyright (C) 2016 Paolo Galeone <nessuno@nerdz.eu>
#
#This Source Code Form is subject to the terms of the Mozilla Public
#License, v. 2.0. If a copy of the MPL was not distributed with this
#file, you can obtain one at http://mozilla.org/MPL/2.0/.
#Exhibit B is not attached; this software is compatible with the
#licenses expressed under Section 1.12 of the MPL v2.
"""train the model"""

import argparse
import math
import os
import sys
import time
from datetime import datetime
import numpy as np
import tensorflow as tf
from pgnet import model
from pgnet.inputs import pascal

# graph parameteres
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = CURRENT_DIR + "/session"
SUMMARY_DIR = CURRENT_DIR + "/summary"
MODEL_PATH = CURRENT_DIR + "/model.pb"

# cropped pascal parameters
CSV_PATH = "~/data/datasets/PASCAL_2012_cropped"

# Number of classes in the dataset plus 1.
# NUM_CLASSES + 1 is reserved for an (unused) background class.
NUM_CLASSES = pascal.NUM_CLASSES + 1

# train & validation parameters
STEP_FOR_EPOCH = math.ceil(pascal.NUM_EXAMPLES_PER_EPOCH_FOR_TRAIN /
                           model.BATCH_SIZE)
DISPLAY_STEP = math.ceil(STEP_FOR_EPOCH / 25)
MEASUREMENT_STEP = DISPLAY_STEP
MAX_ITERATIONS = STEP_FOR_EPOCH * 500

# stop when
AVG_VALIDATION_ACCURACY_EPOCHS = 1
# list of average validation at the end of every epoch
AVG_VALIDATION_ACCURACIES = [0.0 for _ in range(AVG_VALIDATION_ACCURACY_EPOCHS)]

# tensorflow saver constant
SAVE_MODEL_STEP = math.ceil(STEP_FOR_EPOCH / 2)


def train(args):
    """train model"""
    total_start = time.time()

    if not os.path.exists(SESSION_DIR):
        os.makedirs(SESSION_DIR)
    if not os.path.exists(SUMMARY_DIR):
        os.makedirs(SUMMARY_DIR)

    if not os.path.exists(MODEL_PATH):
        graph = tf.Graph()
        with graph.as_default(), tf.device('/cpu:0'):
            with tf.variable_scope("train_input"):
                train_images_queue, train_labels_queue = pascal.train(CSV_PATH,model.BATCH_SIZE,model.INPUT_SIDE, csv_path=CURRENT_DIR)

            with tf.variable_scope("validation_input"):
                validation_images_queue, validation_labels_queue = pascal.validation(CSV_PATH,model.BATCH_SIZE, model.INPUT_SIDE, csv_path=CURRENT_DIR)

            with tf.device(args.device):  #GPU
                global_step = tf.Variable(0, trainable=False, name="global_step")
                labels_ = tf.placeholder(tf.int64, shape=[None], name="labels_")
                is_training_, keep_prob_, images_, logits = model.define(NUM_CLASSES, train_phase=True)
                loss_op = model.loss(logits, labels_)
                train_op = model.train(loss_op, global_step)

            summary_op = tf.summary.merge_all()

            with tf.variable_scope("accuracy"):
                reshaped_logits = tf.squeeze(logits, [1, 2])
                predictions = tf.argmax(reshaped_logits, 1)
                correct_predictions = tf.equal(labels_, predictions)
                accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32), name="accuracy")
                train_accuracy_summary_op = tf.summary.scalar("train_accuracy",accuracy)
                validation_accuracy_summary_op = tf.summary.scalar("validation_accuracy", accuracy)

            variables_to_save = model.variables_to_save([global_step])
            saver = tf.train.Saver(variables_to_save)

            init_op = tf.global_variables_initializer()

            with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:

                def validate():
                    validation_images, validation_labels = sess.run([validation_images_queue, validation_labels_queue])
                    validation_accuracy, summary_line = sess.run([accuracy, validation_accuracy_summary_op], feed_dict={images_: validation_images, labels_: validation_labels, keep_prob_: 1.0,is_training_: False,})
                    return validation_accuracy, summary_line

                sess.run(init_op)

                coord = tf.train.Coordinator()
                threads = tf.train.start_queue_runners(sess=sess, coord=coord)

                checkpoint = tf.train.get_checkpoint_state(SESSION_DIR)
                if checkpoint and checkpoint.model_checkpoint_path:
                    saver.restore(sess, checkpoint.model_checkpoint_path)
                else:
                    print("[I] Unable to restore from checkpoint")

                summary_writer = tf.summary.FileWriter(SUMMARY_DIR + "/train", graph=sess.graph)

                current_epoch = 0
                max_validation_accuracy = 0.0
                sum_validation_accuracy = 0.0
                for step in range(MAX_ITERATIONS):
                    train_images, train_labels = sess.run([train_images_queue, train_labels_queue])

                    start = time.time()

                    _, loss_val, summary_line, gs_value = sess.run([train_op, loss_op, summary_op, global_step],feed_dict={keep_prob_: 0.4,is_training_: True, images_: train_images, labels_: train_labels,})
                    duration = time.time() - start

                    summary_writer.add_summary(summary_line, global_step=gs_value)

                    if np.isnan(loss_val):
                        print('Model diverged with loss = NaN', file=sys.stderr)
                        print(sess.run(reshaped_logits,feed_dict={keep_prob_: 1.0,is_training_: False,images_: train_images,labels_: train_labels}),file=sys.stderr)
                        return 1

                    if step % DISPLAY_STEP == 0 and step > 0:
                        examples_per_sec = model.BATCH_SIZE / duration
                        sec_per_batch = float(duration)
                        print("{} step: {} loss: {} ({} examples/sec; {} batch/sec)".format(datetime.now(), gs_value, loss_val,examples_per_sec, sec_per_batch))

                    stop_training = False
                    save = False

                    if step % MEASUREMENT_STEP == 0 and step > 0:
                        validation_accuracy, summary_line = validate()
                        summary_writer.add_summary(summary_line, global_step=gs_value)

                        test_accuracy, summary_line = sess.run([accuracy, train_accuracy_summary_op],feed_dict={images_: train_images,labels_: train_labels,keep_prob_: 1.0,is_training_: False,})
                        summary_writer.add_summary(summary_line, global_step=gs_value)

                        print("{} step: {} validation accuracy: {} training accuracy: {}".format(datetime.now(), gs_value,validation_accuracy, test_accuracy))

                        sum_validation_accuracy += validation_accuracy

                        if validation_accuracy > max_validation_accuracy:
                            max_validation_accuracy = validation_accuracy
                            save = True

                    if step % STEP_FOR_EPOCH == 0 and step > 0:
                        current_validation_accuracy = sum_validation_accuracy * MEASUREMENT_STEP / STEP_FOR_EPOCH
                        print("Epoch {} finised. Average validation accuracy/epoch: {}".format(current_epoch, current_validation_accuracy))

                        history_avg_accuracy = sum(AVG_VALIDATION_ACCURACIES) / AVG_VALIDATION_ACCURACY_EPOCHS

                        if current_validation_accuracy <= history_avg_accuracy:
                            print("Average validation accuracy not increased after {} epochs. Exit".format(AVG_VALIDATION_ACCURACY_EPOCHS))
                            stop_training = True

                        AVG_VALIDATION_ACCURACIES[current_epoch % AVG_VALIDATION_ACCURACY_EPOCHS] = current_validation_accuracy

                        current_epoch += 1
                        sum_validation_accuracy = 0.0

                    if step % SAVE_MODEL_STEP == 0 or (step + 1) == MAX_ITERATIONS or stop_training:
                        saver.save(sess, SESSION_DIR + "/model", global_step=0)

                    if save:
                        saver.save(sess, SESSION_DIR + "/model-best", global_step=0)
                        print('Model with the highest validation accuracy saved.')

                    if stop_training:
                        break

                summary_writer.flush()
                coord.request_stop()
                coord.join(threads)

        print("Train completed in {}".format(time.time() - total_start))
        model.export(NUM_CLASSES, SESSION_DIR, "model-0", MODEL_PATH)
    else:
        print("Trained model {} already exits".format(MODEL_PATH))
    return 0





if __name__ == "__main__":
    ARG_PARSER = argparse.ArgumentParser(description="Train the model")
    ARG_PARSER.add_argument("--device", default="/gpu:1")
sys.exit(train(ARG_PARSER.parse_args()))