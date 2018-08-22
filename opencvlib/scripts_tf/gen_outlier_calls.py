# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
''' generate detection dos scripts'''
import pandas as pd
import dblib.mssql as mssql
import funclib.iolib as iolib



def main():
    '''main'''
    sql = "select " \
	" sample_lengthid" \
	" ,imgname" \
	" ,[platform]" \
	" ,camera" \
	" ,cnn" \
	" ,unique_code" \
	" ,transform" \
	" ,tl_mm" \
	" ,lens_correction_mm" \
	" ,manual_error_mm" \
	" ,manual_error_mm_perc" \
	" ,mv_lens_correction_mm_error_perc" \
	" ,mv_persp_corr_iter_profile_tridist_mm_error_perc" \
	" ,abs_mv_persp_corr_iter_profile_tridist_mm_error_perc" \
	" ,accuracy" \
	" ,hw_ratio" \
" from " \
	" v_mv_outliers_corrected_positive" \
" union" \
" select" \
	" sample_lengthid" \
	" ,imgname" \
	" ,[platform]" \
	" ,camera" \
	" ,cnn" \
	" ,unique_code" \
	" ,transform" \
	" ,tl_mm" \
	" ,lens_correction_mm" \
	" ,manual_error_mm" \
	" ,manual_error_mm_perc" \
	" ,mv_lens_correction_mm_error_perc" \
	" ,mv_persp_corr_iter_profile_tridist_mm_error_perc" \
	" ,abs_mv_persp_corr_iter_profile_tridist_mm_error_perc" \
	" ,accuracy" \
	" ,hw_ratio" \
" from " \
	" v_mv_outliers_corrected_negative" \
" order by " \
	" abs_mv_persp_corr_iter_profile_tridist_mm_error_perc desc"
    with mssql.Conn('imagedb') as cnn:
        df = pd.read_sql(sql, cnn)

    scripts = []
    for _, row in df.iterrows():
        fname = row['imgname']
        platform = str(row['platform']).lower()
        platform = 'shore' if platform == 'shore' else 'charter'
        camera = str(row['camera']).lower()
        if camera == 'xp30':
            camera = 'fujifilm'
            camera_fld = camera
        elif camera == 's5690':
            camera = 'samsung'
            camera_fld = 's5690'
        else:
            camera = 'gopro'
            camera_fld = 'gopro_all_undistorted'

        image_root = '"C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/'

        #"C:/Users/Graham Monkman/OneDrive/Documents/PHD/images/bass/fiducial/shore/s5690/rotated/vgg_body-caudal.json"
        vgg_file = '%s%s/%s/%s' % (image_root, platform, camera_fld, 'rotated/vgg_body-caudal.json"')


        if str(row['cnn']).lower() == 'nas':
            model_file = '"C:/tf/pretrained/bass/faster_rcnn_nas/run2/frozen_inference_graph.pb"'
        elif str(row['cnn']).lower() == 'res':
            model_file = '"C:/tf/pretrained/bass/faster_rcnn_resnet101/run2/frozen_inference_graph.pb"'
        else:
            model_file = '"C:/tf/pretrained/bass/ssdlite_mobilenet_v2/run2/frozen_inference_graph.pb"'


        s = 'python tf_obj_det.py -x 1 -n %s -p %s -c %s -o outliers -m APPEND -d /CPU:0 %s %s "C:/tf/bass/bass_label_map.pbtxt"' % (fname, platform, camera, vgg_file, model_file)
        scripts.append([s])


    iolib.writecsv('C:/development/python/opencvlib/scripts_tf/outliers.bat', scripts, inner_as_rows=False)
    iolib.folder_open('C:/development/python/opencvlib/scripts_tf')







if __name__ == "__main__":
    main()
