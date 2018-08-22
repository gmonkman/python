# pylint: disable=C0302, too-many-branches, dangerous-default-value, line-too-long, no-member, expression-not-assigned, locally-disabled, not-context-manager, global-statement, protected-access, invalid-name, broad-except
'''one off processing work

THIS WAS NEVER RUN AS WONT CORRECT PROPERLY
'''
#If calculating a new field do this
#Add it to excel sheet (this is currently the master dataset)
#use excel to create the database and add the data
#Alter the sql select here to include calculation fields
#Calculate the column you want
#Recreate the model in imagedb by running C:\development\python\imagedb\generate_model.cmd
#Rename the generated model, to model.py
#Ammend method write_sql to write the calculated column to the sql database

from warnings import warn

import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import session

import dblib.alchemylib as _alc
import funclib.pandaslib as pdl
from funclib.iolib import PrintProgress
import fish
import opencvlib.perspective as perspective
from imagedb.model import SampleLength
from opencvlib import geom
from opencvlib import roi

SPECIES = 'bass' #actually set from a command line arg.
PROFILE_FACTOR = 1 #profile factor set differently if it is bass rather than dab, this is set globally in a routine call during init.

# region init db
CONNECTION_STRING = _alc.ConnectionString(
    "toshiba", "imagedb", "sa", "GGM290471")
_alc.create_engine_mssql(CONNECTION_STRING.mssql_connection_string())
_DBSESSION = sessionmaker(
    bind=_alc.ENGINE,
    autoflush=True,
    autocommit=True,
    expire_on_commit=True)
_SESSION = _DBSESSION()
assert isinstance(_SESSION, session.Session)
# endregion


class InitData(object):
    '''read and manipulate data from sql server'''

    def __init__(self):
        '''init'''

        sql = "" \
            "select" \
            "sample_length.ref_length_mm" \
            ",sample_length.ref_length_px" \
            ",sample_length.sample_lengthid" \
            ",lens_subj_triangle_est" \
            ",sample_length.w" \
            ",sample_length.h" \
            ",sample_length.nas_xmin" \
            ",sample_length.nas_xmax" \
            ",sample_length.nas_ymin" \
            ",sample_length.nas_ymax" \
            ",sample_length.ssd_xmin" \
            ",sample_length.ssd_xmax" \
            ",sample_length.ssd_ymin" \
            ",sample_length.ssd_ymax" \
            ",sample_length.res_xmin" \
            ",sample_length.res_xmax" \
            ",sample_length.res_ymin" \
            ",sample_length.res_ymax" \
            " from" \
            " sample" \
            " inner join sample_length on sample.sampleid=sample_length.sampleid" \
            " inner join sample_header on sample_header.sample_headerid=sample.sample_headerid" \
            " inner join camera on camera.cameraid=sample.cameraid" \
            " left join housing_mount on housing_mount.housing_mountid=sample.housing_mountid"

        where = " where sample.species='bass'"

        sql += where

        self.df_lengths = pd.read_sql(sql, _alc.ENGINE, 'sample_lengthid')


    @staticmethod
    def _get_fish_depth(total_length):
        '''(float)->float
        '''
        if total_length is None:
            return None
        if SPECIES == 'bass':
            bass = fish.Bass(float(total_length))  # bass is subclass of fish
            # fishactions is polymorphic taking multiple species classes
            act = fish.FishActions(bass)
        else:
            dab = fish.Dab(float(total_length))
            act = fish.FishActions(dab)
        return act.get_max_depth()


    @staticmethod
    def _get_unadjusted_length(ref_length_mm, ref_length_px, xmin, xmax, ymin, ymax, h, w):
        '''(float) -> float
        estimate fish length without profile adjustment
        '''
        try:
            pts_normal = [[xmin, ymin], [xmax, ymax], [xmin, ymax], [xmax, ymin]]
            pts = roi.points_denormalize(pts_normal, h, w)
            _, _, diag = geom.rect_side_lengths2(pts)
            out = (ref_length_mm / ref_length_px) * diag
        except ZeroDivisionError as _:
            out = None
            warn('ref_length_px was 0. None was returned')
        except Exception as _:
            out = None
            warn('An error occured in _get_unadjusted_length. None was returned')
        return out



    def calc_unadjusted_lengths(self):
        '''(pd.df) -> void
        add new cols
        '''
        assert isinstance(self.df_lengths, pd.DataFrame)

        #NAS
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'ref_length_mm', 'ref_length_px', 'nas_xmin', 'nas_xmax', 'nas_ymin', 'nas_ymax', 'h', 'w')
        pdl.col_calculate_new(self.df_lengths, InitData._get_unadjusted_length, 'nas_length_est_rotation_adjust3', *colinds, progress_init_msg='Calculating nas_length_est_rotation_adjust3')

        #RES
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'ref_length_mm', 'ref_length_px', 'res_xmin', 'res_xmax', 'res_ymin', 'res_ymax', 'h', 'w')
        pdl.col_calculate_new(self.df_lengths, InitData._get_unadjusted_length, 'res_length_est_rotation_adjust3', *colinds, progress_init_msg='Calculating res_length_est_rotation_adjust3')

        #SSD
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'ref_length_mm', 'ref_length_px', 'ssd_xmin', 'ssd_xmax', 'ssd_ymin', 'ssd_ymax', 'h', 'w')
        pdl.col_calculate_new(self.df_lengths, InitData._get_unadjusted_length, 'ssd_length_est_rotation_adjust3', *colinds, progress_init_msg='Calculating ssd_length_est_rotation_adjust3')



    def calc_adjusted_lengths(self):
        '''(pd.df) -> void
        add a new col for the perspective adjusted length
        '''
        assert isinstance(self.df_lengths, pd.DataFrame)

        #create new col in dataframe and fill with iterative perspective correction adjusted for the fish profile USING the nas_rcnn estimated length
        #based on triangles estimate of subj-lens distance using a calibration shot, BUT this uses the model 1 length corrected for the rotation
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'coeff', 'const', 'lens_subj_triangle_est', 'nas_length_est_rotation_adjust3', 'profile_factor')
        pdl.col_calculate_new(self.df_lengths, perspective.get_perspective_correction_iter_linear, 'nas_all_corr_rot_adj3_mm', *colinds, progress_init_msg='Calculating nas_all_corr_rot_adj3_mm')

        #create new col in dataframe and fill with iterative perspective correction adjusted for the fish profile USING the res_rcnn estimated length
        #based on triangles estimate of subj-lens distance using a calibration shot, BUT this uses the model 1 length corrected for the rotation
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'coeff', 'const', 'lens_subj_triangle_est', 'res_length_est_rotation_adjust3', 'profile_factor')
        pdl.col_calculate_new(self.df_lengths, perspective.get_perspective_correction_iter_linear, 'res_all_corr_rot_adj3_mm', *colinds, progress_init_msg='Calculating res_all_corr_rot_adj3_mm')

        #create new col in dataframe and fill with iterative perspective correction adjusted for the fish profile USING the res_rcnn estimated length
        #based on triangles estimate of subj-lens distance using a calibration shot, BUT this uses the model 1 length corrected for the rotation
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'coeff', 'const', 'lens_subj_triangle_est', 'ssd_length_est_rotation_adjust3', 'profile_factor')
        pdl.col_calculate_new(self.df_lengths, perspective.get_perspective_correction_iter_linear, 'ssd_all_corr_rot_adj3_mm', *colinds, progress_init_msg='Calculating ssd_all_corr_rot_adj3_mm')


    def _add_linear(self):
        '''add the linear coefficients relating depth to length
        used to do perspective adjust calculations
        '''
        assert isinstance(self.df_lengths, pd.DataFrame)
        global PROFILE_FACTOR
        if SPECIES == 'bass':
            oFish = fish.Bass()
        elif SPECIES == 'dab':
            oFish = fish.Dab()
        else:
            raise ValueError('Unknown species %s' % SPECIES)
        PROFILE_FACTOR = oFish.profile_mean_height
        coeff, const = oFish.lalg_length_equals_depth()
        pdl.col_append_fill(self.df_lengths, 'coeff', coeff)
        pdl.col_append_fill(self.df_lengths, 'const', const)
        pdl.col_append_fill(self.df_lengths, 'profile_factor', PROFILE_FACTOR)


    def _add_depths(self):
        '''add depth col to be used in perspective_adjust
        '''
        assert isinstance(self.df_lengths, pd.DataFrame)
        # first add the fish depth estimate using the actual measured length
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'tl_mm')
        pdl.col_calculate_new(self.df_lengths, InitData._get_fish_depth, 'fish_depth_from_actual', colinds, progress_init_msg='Calculating fish_depth_from_actual')

        # add fish depth based on the estimated length
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'estimate_mm')
        pdl.col_calculate_new(self.df_lengths, InitData._get_fish_depth, 'fish_depth_from_estimate', colinds, progress_init_msg='Calculating fish_depth_from_estimate')


    def write_to_sql(self):
        '''updates the corrected records to sql'''
        COLCNT = 19
        rw_cnt = len(self.df_lengths.index) * COLCNT
        PP = PrintProgress(rw_cnt, init_msg='Writing data back to SQL Server')

        #first writing back the non-profile adjusted lengths
        est_cor_ind = pdl.cols_get_indexes_from_names(self.df_lengths, 'nas_length_est_rotation_adjust3') #1
        for i, row in self.df_lengths.iterrows():
            PP.increment()
            tl_cor = row[est_cor_ind]
            sam_len = _SESSION.query(SampleLength).filter_by(sample_lengthid=int(i)).first()
            assert isinstance(sam_len, SampleLength)
            sam_len.nas_length_est_rotation_adjust3 = _read_range_int(tl_cor)


        est_cor_ind = pdl.cols_get_indexes_from_names(self.df_lengths, 'res_length_est_rotation_adjust3') #2
        for i, row in self.df_lengths.iterrows():
            PP.increment()
            tl_cor = row[est_cor_ind]
            sam_len = _SESSION.query(SampleLength).filter_by(sample_lengthid=int(i)).first()
            assert isinstance(sam_len, SampleLength)
            sam_len.res_length_est_rotation_adjust3 = _read_range_int(tl_cor)

        est_cor_ind = pdl.cols_get_indexes_from_names(self.df_lengths, 'ssd_length_est_rotation_adjust3') #3
        for i, row in self.df_lengths.iterrows():
            PP.increment()
            tl_cor = row[est_cor_ind]
            sam_len = _SESSION.query(SampleLength).filter_by(sample_lengthid=int(i)).first()
            assert isinstance(sam_len, SampleLength)
            sam_len.ssd_length_est_rotation_adjust3 = _read_range_int(tl_cor)


        est_cor_ind = pdl.cols_get_indexes_from_names(self.df_lengths, 'nas_all_corr_rot_adj3_mm') #4
        for i, row in self.df_lengths.iterrows():
            PP.increment()
            tl_cor = row[est_cor_ind]
            sam_len = _SESSION.query(SampleLength).filter_by(sample_lengthid=int(i)).first()
            assert isinstance(sam_len, SampleLength)
            sam_len.nas_all_corr_rot_adj3_mm = _read_range_int(tl_cor)

        est_cor_ind = pdl.cols_get_indexes_from_names(self.df_lengths, 'res_all_corr_rot_adj3_mm') #5
        for i, row in self.df_lengths.iterrows():
            PP.increment()
            tl_cor = row[est_cor_ind]
            sam_len = _SESSION.query(SampleLength).filter_by(sample_lengthid=int(i)).first()
            assert isinstance(sam_len, SampleLength)
            sam_len.res_all_corr_rot_adj3_mm = _read_range_int(tl_cor)

        est_cor_ind = pdl.cols_get_indexes_from_names(self.df_lengths, 'ssd_all_corr_rot_adj3_mm') #6
        for i, row in self.df_lengths.iterrows():
            PP.increment()
            tl_cor = row[est_cor_ind]
            sam_len = _SESSION.query(SampleLength).filter_by(sample_lengthid=int(i)).first()
            assert isinstance(sam_len, SampleLength)
            sam_len.ssd_all_corr_rot_adj3_mm = _read_range_int(tl_cor)



def _read_range_int(v):
    '''(pandas.Range)->int|None
    read v for writing
    '''
    if pd.isnull(v[0]):
        return None

    return int(round(v[0]))


def _read_range_float(v):
    '''(pandas.Range)->float|None
    read v for writing
    '''
    if pd.isnull(v[0]):
        return None

    return float(v[0])


# region ENTRY
def main():
    '''execute if script was entry point'''
    print('\nWorking on it....')
    cls = InitData()

    print('Calculating fish widths....')
    cls._add_depths() #add depth estimates based on manual and estimated fish lengths

    print('Calculatng lens-subj estimates....')
    cls._add_lens_subj_estimates() #add the lens-subject distance estimates from the two methods

    print('Calculating l/w coefficients....')
    cls._add_linear() # add 2 cols - coeff,const to be used to calculate depth on the fly in get_perspective_correction_iter_linear

    print('Calculating length with perspective adjustment....')
    cls.calc_unadjusted_lengths()

    print('Calculating lengths with perspective adjustment')
    cls.calc_adjusted_lengths()

    print('Writing data to SQL Server....')
    cls.write_to_sql()

    print('Done')







# This only executes if this script was the entry point
if __name__ == '__main__':
    # execute my code
    main()
# endregion
