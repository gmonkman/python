#pylint: disable=C0302, too-many-branches, dangerous-default-value, line-too-long, no-member, expression-not-assigned, locally-disabled, not-context-manager
'''one off processing work'''
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import session

import dblib.alchemylib as _alc
import funclib.pandaslib as pdl
import fish
import opencvlib.common as cm
from imagedb.model import SampleLength


#region init db
CONNECTION_STRING = _alc.ConnectionString("toshiba", "imagedb", "sa", "GGM290471")
_alc.create_engine_mssql(CONNECTION_STRING.mssql_connection_string())
_DBSESSION = sessionmaker(bind=_alc.ENGINE, autoflush=True, autocommit=True, expire_on_commit=True)
_SESSION = _DBSESSION()
assert isinstance(_SESSION, session.Session)
#endregion


class InitData(object):
    '''read and manipulate data from sql server'''
    def __init__(self):
        '''init'''

        sql = '' \
        'select' \
	        ' sample_length.sample_lengthid' \
            ',sample.tl_mm' \
	        ',sample.board_board_length_mm + housing_mount.subject_to_lens_conversion_mm as lens_subject_distance' \
	        ',sample_length.lens_correction_mm' \
            ',sample_length.estimate_mm' \
        ' from' \
	        ' sample' \
	        ' inner join sample_length on sample.sampleid=sample_length.sampleid' \
	        ' inner join housing_mount on housing_mount.housing_mountid=sample.housing_mountid'

        self.df_lengths = pd.read_sql(sql, _alc.ENGINE, 'sample_lengthid')

    @staticmethod
    def _get_fish_depth(total_length):
        '''(float)->float
        '''
        bass = fish.Bass(float(total_length)) #bass is subclass of fish
        act = fish.FishActions(bass) #fishactions is polymorphic taking multiple species classes
        return act.get_max_depth()

    def perspective_adjust(self):
        '''(pd.df)
        add a new col for the perspective adjusted length
        BYREF
        '''
        assert isinstance(self.df_lengths, pd.DataFrame)

        #create new col in dataframe and fill with perspective corrections based on the actual fish length
        #fish_depth_from_actual is added to the df in add_depths
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'lens_subject_distance', 'fish_depth_from_actual', 'lens_correction_mm')
        pdl.col_calculate_new(self.df_lengths, cm.get_perspective_correction, 'tl_corrected_mm', *colinds)

        #create new col in dataframe and fill with perspective corrections based on the estimated fish length
        #fish_depth_from_estimate is added to the df in add_depths
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'lens_subject_distance', 'fish_depth_from_estimate', 'lens_correction_mm')
        pdl.col_calculate_new(self.df_lengths, cm.get_perspective_correction, 'estimate_corrected_mm', *colinds)

        #create new col in dataframe and fill with perspective corrections based on the estimated fish length
        self._add_linear() #add 2 cols - coeff,const to be used to calculate depth on the fly in get_perspective_correction_iter_linear
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'coeff', 'const', 'lens_subject_distance', 'lens_correction_mm')
        pdl.col_calculate_new(self.df_lengths, cm.get_perspective_correction_iter_linear, 'perspective_corrected_estimate_iter_mm', *colinds)

    def _add_linear(self):
        '''add the linear coefficients relating depth to length
        used to do perspective adjust calculations
        '''
        assert isinstance(self.df_lengths, pd.DataFrame)
        obass = fish.Bass()
        coeff, const = obass.lalg_length_equals_depth()
        pdl.col_append_fill(self.df_lengths, 'coeff', coeff)
        pdl.col_append_fill(self.df_lengths, 'const', const)

    def add_depths(self):
        '''add depth col to be used in perspective_adjust
        '''
        assert isinstance(self.df_lengths, pd.DataFrame)
        #first add the fish depth estimate using the actual measured length
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'tl_mm')
        pdl.col_calculate_new(self.df_lengths, InitData._get_fish_depth, 'fish_depth_from_actual', colinds)

        #add fish depth based on the estimated length
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'estimate_mm')
        pdl.col_calculate_new(self.df_lengths, InitData._get_fish_depth, 'fish_depth_from_estimate', colinds)

    def update_length(self):
        '''updates the corrected records to sql'''

        #first do
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

def _read_range_int(v):
    '''(pandas.Range)->int|None
    read v for writing
    '''
    if pd.isnull(v[0]):
        return None
    else:
        return int(round(v[0]))

#region ENTRY
def main():
    '''execute if script was entry point'''
    cls = InitData()
    cls.add_depths()
    cls.perspective_adjust()
    cls.update_length()

#This only executes if this script was the entry point
if __name__ == '__main__':
    #execute my code
    main()
#endregion
