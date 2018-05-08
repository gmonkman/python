#pylint: skip-file

'''mucking around with basic TF stuff'''
import tensorflow as tf

import pgnet.inputs.bass as bass
#import numpy as np




def img_std(image):
    '''(tensor)-> tensor
    Rescale image to float (-1 to 1)
    '''
    image = tf.image.per_image_standardization(image)
    # rescale to [-1,1] instead of [0, 1)
    return tf.multiply(tf.subtract(image, 0.5), 2)


def resize_bl(image, side):
    """Returns the image, resized with bilinear interpolation to: side x side x depth
    Input:
        image: 3d tensor width shape [side, side, depth]
    """

    return image


def img_get(filename, label, apply_distortion):
    image_string = tf.read_file(filename)
    image_decoded = tf.image.decode_image(image_string)
    image_decoded.set_shape([bass.H_ORIG, bass.W_ORIG, bass.CH_ORIG])


    #resize image
    image_rsz = tf.expand_dims(image_decoded, 0)
    image_rsz = tf.image.resize_bilinear(image_rsz, [bass.H, bass.W], align_corners=False) # now image is 4-D float32 tensor: [1, side, side, image.depth]
    image_rsz = tf.image_rsz(image, [0])

    if apply_distortion:
        img_distorted = distort_image(image_rsz, bass.H_ORIG, bass.W_ORIG)
    else:
        img_distorted = image_rsz

    img_standardized = img_std(img_distorted) #-1 to 1
    return img_standardized, label


def distort_image(image, input_width, input_height, output_side):
    """Applies random distortion to the image.
    The output image is output_side x output_side x 3
    """

    def random_crop_it():
        """Random crops image, after resizing it to output_side +10 x output_side+10"""
        resized_img = resize_bl(image, output_side + 10)
        return tf.random_crop(resized_img, [output_side, output_side, 3])

    def resize_it():
        """Resize the image using resize_bl"""
        return resize_bl(image, output_side)

    # if input.width >= output.side + 10 and input.heigth >= output.side + 10
    #   resize it to output.side + 10 x output.size + 10 and random crop it
    # else resize it
    increased_output_side = tf.constant(output_side + 10, dtype=tf.int64)
    image = tf.cond(tf.logical_and(tf.greater_equal(input_width, increased_output_side), tf.greater_equal(input_height, increased_output_side)), random_crop_it, resize_it)
    tf.cond


    # randomize the order of the random distortions
    def fn1():
        """Applies random brightness, saturation, hue, contrast"""
        distorted_image = tf.image.random_brightness(
            flipped_image, max_delta=32. / 255.)
        distorted_image = tf.image.random_saturation(
            distorted_image, lower=0.5, upper=1.5)
        distorted_image = tf.image.random_hue(distorted_image, max_delta=0.2)
        distorted_image = tf.image.random_contrast(
            distorted_image, lower=0.5, upper=1.5)
        return distorted_image

    def fn2():
        """Applies random brightness, contrast, saturation, hue"""
        distorted_image = tf.image.random_brightness(
            flipped_image, max_delta=32. / 255.)
        distorted_image = tf.image.random_contrast(
            distorted_image, lower=0.5, upper=1.5)
        distorted_image = tf.image.random_saturation(
            distorted_image, lower=0.5, upper=1.5)
        distorted_image = tf.image.random_hue(distorted_image, max_delta=0.2)

        return distorted_image

    p_order = tf.random_uniform(
        shape=[], minval=0.0, maxval=1.0, dtype=tf.float32)
    distorted_image = tf.cond(tf.less(p_order, 0.5), fn1, fn2)
    distorted_image = tf.clip_by_value(distorted_image, 0.0, 1.0)
    return distorted_image



def try_dataset(apply_distortion):
    bass.init_()
    ds_imglbl = tf.data.Dataset.from_tensor_slices((bass.BassTrain.img_paths, bass.BassTrain.labels))
    ds_imglbl = ds_imglbl.shuffle(buffer_size=100, reshuffle_each_iteration=True)
    ds_imglbl = ds_imglbl.batch(50) #batch
    ds_imglbl = ds_imglbl.repeat(1) #epochs
    iter_ = ds_imglbl.make_one_shot_iterator()
    images_batch, labels_batch = iter_.get_next()
    labels_batch = tf.cast(labels_batch, tf.int64)
    imgs, lbls = iter_.get_next()


    with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:
        sess.run([tf.global_variables_initializer(), tf.local_variables_initializer()])
        for _ in range(100):
            x, y = sess.run([lbls, imgs])




if __name__ == "__main__":
    try_dataset()
    #main()
