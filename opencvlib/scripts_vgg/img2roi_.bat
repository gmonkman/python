@echo off

@echo ARE YOU SURE YOU WISH TO RUN THIS BATCH FILE? CTRL-C TO CANCEL
pause
pause

REM charter
C:\development\python\opencvlib\scripts_vgg\img2roi.py -m rename -g 1.2 "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/fujifilm/rotated" "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/candidate_fid" vgg_body-caudal.json
C:\development\python\opencvlib\scripts_vgg\img2roi.py -m rename -g 1.2 "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/gopro_all_undistorted/rotated" "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/candidate_fid" vgg_body-caudal.json
C:\development\python\opencvlib\scripts_vgg\img2roi.py -m rename -g 1.2 "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/charter/s5690/rotated" "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/candidate_fid" vgg_body-caudal.json

REM shore
C:\development\python\opencvlib\scripts_vgg\img2roi.py -m rename -g 1.2 "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/fujifilm/rotated" "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/candidate_fid" vgg_body-caudal.json
C:\development\python\opencvlib\scripts_vgg\img2roi.py -m rename -g 1.2 "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/gopro_all_undistorted/rotated" "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/candidate_fid" vgg_body-caudal.json
C:\development\python\opencvlib\scripts_vgg\img2roi.py -m rename -g 1.2 "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/s5690/rotated" "C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/train/candidate_fid" vgg_body-caudal.json
pause
