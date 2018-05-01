# pylint: disable=C0302, too-many-branches, dangerous-default-value, line-too-long, no-member, expression-not-assigned, locally-disabled, not-context-manager
'''one off processing work
Uses opencvlib.perspective.

'''
import argparse

import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import session

import dblib.alchemylib as _alc
import funclib.pandaslib as pdl
import fish
import opencvlib.perspective as perspective
from imagedb.model import SampleLength

SPECIES = 'bass'
PROFILE_FACTOR = 1 #profile factor set differently if it is bass rather than dab

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
            " sample_length.sample_lengthid" \
            ",sample.tl_mm" \
            ",sample.board_board_length_mm + housing_mount.subject_to_lens_conversion_mm as lens_subject_distance" \
            ",sample.rotated_resolution_x" \
            ",sample.rotated_resolution_y" \
            ",sample_length.lens_correction_mm" \
            ",sample_length.estimate_mm" \
            ",camera.focal_distance_mm" \
            ",camera.cmos_height_mm" \
            ",camera.cmos_width_mm" \
            ",calib_lens_subj_distance_mm" \
            ",camera.calib_res_x" \
            ",camera.calib_res_y" \
            ",camera.calib_marker_length_mm" \
            ",camera.calib_marker_length_px" \
            " from" \
            " sample" \
            " inner join sample_length on sample.sampleid=sample_length.sampleid" \
            " inner join sample_header on sample_header.sample_headerid=sample.sample_headerid" \
            " inner join camera on camera.cameraid=sample.cameraid" \
            " left join housing_mount on housing_mount.housing_mountid=sample.housing_mountid"
        if False:
            where = " where "
            if SPECIES == 'bass':
                where += " sample.species='bass'"
            else:
                where += " sample.species='dab'"
            sql += where

            #WHERE = " sample.species='bass' and sample_header.sample_headerid <= 3"
            #<= 3 for sample header is just bass from processors
            #sample.species can also = 'dab', sample_headerid for dab = 3
            #sample headerid = 4 is shore fid markers
            #sample headerid = 5 is charter fid markers

        self.df_lengths = pd.read_sql(sql, _alc.ENGINE, 'sample_lengthid')


    @staticmethod
    def _get_fish_depth(total_length):
        '''(float)->float
        '''
        if SPECIES == 'bass':
            bass = fish.Bass(float(total_length))  # bass is subclass of fish
            # fishactions is polymorphic taking multiple species classes
            act = fish.FishActions(bass)
        else:
            pass
        return act.get_max_depth()


    def perspective_adjust(self):
        '''(pd.df) -> void
        add a new col for the perspective adjusted length
        '''
        assert isinstance(self.df_lengths, pd.DataFrame)

        # create new col in dataframe and fill with perspective corrections based on the actual fish length
        # fish_depth_from_actual is added to the df in add_depths THIS IS REALLY FOR SANITY CHECK
        colinds = pdl.cols_get_indexes_from_names( self.df_lengths, 'lens_subject_distance', 'fish_depth_from_actual', 'lens_correction_mm')
        pdl.col_calculate_new(self.df_lengths, perspective.get_perspective_correction, 'tl_corrected_mm', *colinds)

        # create new col in dataframe and fill with perspective corrections based on the estimated fish length
        # fish_depth_from_estimate is added to the df in add_depths
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'lens_subject_distance', 'fish_depth_from_estimate', 'lens_correction_mm')
        pdl.col_calculate_new(self.df_lengths, perspective.get_perspective_correction, 'estimate_corrected_mm', *colinds)

        # create new col in dataframe and fill with perspective corrections
        # based on the estimated fish length. Uses the measured lens-subject distance
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'coeff', 'const', 'lens_subject_distance', 'lens_correction_mm')
        pdl.col_calculate_new(self.df_lengths, perspective.get_perspective_correction_iter_linear, 'perspective_corrected_estimate_iter_mm', *colinds)

        # create new col in dataframe and fill with iterative perspective correction adjusted for the fish profile based on actual subj-lens distance
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'coeff', 'const', 'lens_subject_distance', 'lens_correction_mm')
        colinds.extend(PROFILE_FACTOR)
        pdl.col_calculate_new(self.df_lengths, perspective.get_perspective_correction_iter_linear, 'persp_corr_iter_profile_mm', *colinds)

        #create new col in dataframe and fill with iterative perspective correction adjusted for the fish profile
        #based on camera profile estimate subj-lens distance
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'coeff', 'const', 'lens_subj_camprop_est', 'lens_correction_mm')
        colinds.extend(PROFILE_FACTOR)
        pdl.col_calculate_new(self.df_lengths, perspective.get_perspective_correction_iter_linear, 'persp_corr_iter_profile_camdist_mm', *colinds)

        #create new col in dataframe and fill with iterative perspective correction adjusted for the fish profile
        #based on triangles estimate of subj-lens distance using a calibration shot
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'coeff', 'const', 'lens_subj_triangle_est', 'lens_correction_mm')
        colinds.extend(PROFILE_FACTOR)
        pdl.col_calculate_new(self.df_lengths, perspective.get_perspective_correction_iter_linear, 'persp_corr_iter_profile_tridist_mm', *colinds)



    def _add_lens_subj_estimates(self):
        '''() -> void
        For the mermaid and morrisons we have a real
        measure of the subj-lens distance, but we
        won't have this in the general case.

        So add two columns which estimate the lens-subj distance
        using similiar triangles and using the camera lens and
        sensor properties.
        '''
        assert isinstance(self.df_lengths, pd.DataFrame)

        def _from_cam(f, px_x=None, x_mm=None, marker_length_mm=None, marker_length_px=None):
            '''(float, float, float, float, float)->float
            Estimate lens-subj distance using camera lens and sensor properties.

            f: focal length from camera properties
            px_x: image resolution in pixels (this will be read from the rotated image, or could be from the camera specs)
            x_mm: camera sensor width in mm
            marker_length_mm: length of fid marker
            marker_length_px: marker size in pixels in image

            Returns: estimate of subj-lens distance in mm
            '''
            return perspective.subjdist_camera(perspective.Camera(f, px_x=px_x, x_mm=x_mm), perspective.Measure(marker_length_mm=marker_length_mm, marker_length_px=marker_length_px))


        def _from_triangles(cal_lens_subj_dist, cal_marker_length_mm, cal_marker_length_px, marker_length_mm, marker_length_px):
            '''(float, float, float, float, float)->float
            Lens-subj distance estimate using a calibration image where
            lens-subj distance is known

            '''
            return perspective.subjdist_knowndist(perspective.Measure(lens_subj_dist=cal_lens_subj_dist, marker_length_mm=cal_marker_length_mm, marker_length_px=cal_marker_length_px),
                                                  perspective.Measure(marker_length_mm=marker_length_mm, marker_length_px=marker_length_px))

        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'focal_distance_mm', 'rotated_resolution_x', 'cmos_width_mm', 'ref_length_mm', 'ref_length_px')
        pdl.col_calculate_new(self.df_lengths, _from_cam, 'lens_subj_camprop_est', *colinds)

        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'calib_lens_subj_distance', 'calib_marker_length_mm', 'calib_marker_length_px', 'ref_length_mm', 'ref_length_px')
        pdl.col_calculate_new(self.df_lengths, _from_triangles, 'lens_subj_triangle_est', *colinds)


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


    def _add_depths(self):
        '''add depth col to be used in perspective_adjust
        '''
        assert isinstance(self.df_lengths, pd.DataFrame)
        # first add the fish depth estimate using the actual measured length
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'tl_mm')
        pdl.col_calculate_new(self.df_lengths, InitData._get_fish_depth, 'fish_depth_from_actual', colinds)

        # add fish depth based on the estimated length
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'estimate_mm')
        pdl.col_calculate_new(self.df_lengths, InitData._get_fish_depth, 'fish_depth_from_estimate', colinds)


    def update_length(self):
        '''updates the corrected records to sql'''
        # first do
        tl_cor_ind = pdl.cols_get_indexes_from_names(self.df_lengths, 'tl_corrected_mm')
        for i, row in self.df_lengths.iterrows():
            tl_cor = row[tl_cor_ind]
            sam_len = _SESSION.query(SampleLength).filter_by(sample_lengthid=int(i)).first()
            assert isinstance(sam_len, SampleLength)
            sam_len.perspective_corrected_actual_mm = _read_range_int(tl_cor)

        est_cor_ind = pdl.cols_get_indexes_from_names(self.df_lengths, 'estimate_corrected_mm')
        for i, row in self.df_lengths.iterrows():
            tl_cor = row[est_cor_ind]
            sam_len = _SESSION.query(SampleLength).filter_by(sample_lengthid=int(i)).first()
            assert isinstance(sam_len, SampleLength)
            sam_len.perspective_corrected_estimate_mm = _read_range_int(tl_cor)

        est_cor_ind = pdl.cols_get_indexes_from_names(self.df_lengths, 'perspective_corrected_estimate_iter_mm')
        for i, row in self.df_lengths.iterrows():
            tl_cor = row[est_cor_ind]
            sam_len = _SESSION.query(SampleLength).filter_by(sample_lengthid=int(i)).first()
            assert isinstance(sam_len, SampleLength)
            sam_len.perspective_corrected_estimate_iter_mm = _read_range_int(tl_cor)

        est_cor_ind = pdl.cols_get_indexes_from_names(self.df_lengths, 'persp_corr_iter_profile_mm')
        for i, row in self.df_lengths.iterrows():
            tl_cor = row[est_cor_ind]
            sam_len = _SESSION.query(SampleLength).filter_by(sample_lengthid=int(i)).first()
            assert isinstance(sam_len, SampleLength)
            sam_len.persp_corr_iter_profile_mm = _read_range_int(tl_cor)

        est_cor_ind = pdl.cols_get_indexes_from_names(self.df_lengths, 'persp_corr_iter_profile_camdist_mm')
        for i, row in self.df_lengths.iterrows():
            tl_cor = row[est_cor_ind]
            sam_len = _SESSION.query(SampleLength).filter_by(sample_lengthid=int(i)).first()
            assert isinstance(sam_len, SampleLength)
            sam_len.persp_corr_iter_profile_camdist_mm = _read_range_int(tl_cor)

        est_cor_ind = pdl.cols_get_indexes_from_names(self.df_lengths, 'persp_corr_iter_profile_tridist_mm')
        for i, row in self.df_lengths.iterrows():
            tl_cor = row[est_cor_ind]
            sam_len = _SESSION.query(SampleLength).filter_by(sample_lengthid=int(i)).first()
            assert isinstance(sam_len, SampleLength)
            sam_len.persp_corr_iter_profile_tridist_mm = _read_range_int(tl_cor)


def _read_range_int(v):
    '''(pandas.Range)->int|None
    read v for writing
    '''
    if pd.isnull(v[0]):
        return None
    else:
        return int(round(v[0]))



# region ENTRY
def main():
    '''execute if script was entry point'''
    cmdline = argparse.ArgumentParser(description=__doc__)
    cmdline.add_argument('-s', '--species', help='The where')
    args = cmdline.parse_args()
    global SPECIES
    SPECIES = args.species
    assert SPECIES in ['dab', 'bass'], 'Species should be "dab" or "bass"'
    cls = InitData()
    cls._add_depths() #add depth estimates based on manual and estimated fish lengths
    cls._add_lens_subj_estimates() #add the lens-subject distance estimates from the two methods
    cls._add_linear() # add 2 cols - coeff,const to be used to calculate depth on the fly in get_perspective_correction_iter_linear
    cls.perspective_adjust()
    cls.update_length()


# This only executes if this script was the entry point
if __name__ == '__main__':
    # execute my code
    main()
# endregion
