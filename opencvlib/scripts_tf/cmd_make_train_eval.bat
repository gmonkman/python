@echo off
REM train images
vgg2TFRecord "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/candidate/train" "C:/tf/data/train.record" vgg_body.json

REM eval/test images.
vgg2TFRecord -b 50 "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/candidate/eval" "C:/tf/data/eval.record" vgg_body.json
pause