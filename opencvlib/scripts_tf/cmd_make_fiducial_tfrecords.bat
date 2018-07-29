@echo off
REM Charter
REM vgg2TFRecord.py -x 1.015 "C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\charter\fujifilm\rotated" "C:\tf\tf\bass\tfrecords\charter_xp30_x1.015.record" vgg_body-caudal.json
REM vgg2TFRecord.py -x 1.015 "C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\charter\gopro_all_undistorted\rotated" "C:\tf\tf\bass\tfrecords\charter_gopro_x1.015.record" vgg_body-caudal.json
REM vgg2TFRecord.py -x 1.015 "C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\charter\s5690\rotated" "C:\tf\tf\bass\tfrecords\charter_s5690_x1.015.record" vgg_body-caudal.json


REM Shore
REM vgg2TFRecord.py -x 1.015 "C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\shore\fujifilm\rotated" "C:\tf\tf\bass\tfrecords\shore_xp30_x1.015.record" vgg_body-caudal.json
REM vgg2TFRecord.py -x 1.015 "C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\shore\gopro_all_undistorted\rotated" "C:\tf\tf\bass\tfrecords\shore_gopro_x1.015.record" vgg_body-caudal.json
REM vgg2TFRecord.py -x 1.015 "C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\shore\s5690\rotated" "C:\tf\tf\bass\tfrecords\shore_s5690_x1.015.record" vgg_body-caudal.json


REM Charter with Flip
C:\Python354x64\python.exe vgg2TFRecord.py -f -x 1.015 "C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\charter\fujifilm\rotated" "C:\tf\tf\bass\tfrecords\charter_xp30_flip_x1.015.record" vgg_body-caudal.json
C:\Python354x64\python.exe vgg2TFRecord.py -f -x 1.015 "C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\charter\gopro_all_undistorted\rotated" "C:\tf\tf\bass\tfrecords\charter_gopro_flip_x1.015.record" vgg_body-caudal.json
C:\Python354x64\python.exe vgg2TFRecord.py -f -x 1.015 "C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\charter\s5690\rotated" "C:\tf\tf\bass\tfrecords\charter_s5690_flip_x1.015.record" vgg_body-caudal.json


REM Shore with Flip
C:\Python354x64\python.exe vgg2TFRecord.py -f -x 1.015 "C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\shore\fujifilm\rotated" "C:\tf\tf\bass\tfrecords\shore_xp30_flip_x1.015.record" vgg_body-caudal.json
C:\Python354x64\python.exe vgg2TFRecord.py -f -x 1.015 "C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\shore\gopro_all_undistorted\rotated" "C:\tf\tf\bass\tfrecords\shore_gopro_flip_x1.015.record" vgg_body-caudal.json
C:\Python354x64\python.exe vgg2TFRecord.py -f -x 1.015 "C:\Users\Graham Monkman\OneDrive\Documents\PHD\images\bass\fiducial\shore\s5690\rotated" "C:\tf\tf\bass\tfrecords\shore_s5690_flip_x1.015.record" vgg_body-caudal.json



pause