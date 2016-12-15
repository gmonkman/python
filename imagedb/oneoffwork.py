#pylint: disable=C0302, too-many-branches, dangerous-default-value, line-too-long, no-member, expression-not-assigned, locally-disabled, not-context-manager
'''one off processing work'''
from sqlalchemy.orm import sessionmaker
import dblib.alchemylib as _alc
import imagedb.model as model

import pandas as pd

import dblib.alchemylib as al
import funclib.pandaslib as pdl
import imagedb
import opencvlib.common as cm

#region init db
_alc.create_engine_mssql(alc.ConnectionString("toshiba", "imagedb", "sa", "GGM290471"))
_DBSession = sessionmaker(bind = alc.ENGINE)
_Session = DBSession()
#endregion


class InitData(object):
    '''read and manipulate data from sql server'''
    def __init__(self, server, database, user, password):
        self.df_lengths = pd.read_sql('SELECT * FROM v_lengths', _alc.ENGINE, 'sampleid')

    @staticmethod
    def _get_fish_depth(total_length):
        '''(float)->float
        '''
        bass = imagedb.Bass(float(total_length)) #bass is subclass of fish
        act = imagedb.FishActions(bass) #fishactions is polymorphic taking multiple species classes
        return act.get_max_depth()

    def perspective_adjust(self):
        '''(pd.df)
        add a new col for the perspective adjusted length
        BYREF
        '''
        assert isinstance(self.df_lengths, pd.DataFrame)
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'lens_subject_distance', 'fish_depth', 'tl_mm')
        pdl.col_calculate_new(self.df_lengths, cm.get_perspective_correction, 'tl_corrected_mm', *colinds)

    def add_depth(self):
        '''add depth col
        '''
        assert isinstance(self.df_lengths, pd.DataFrame)
        colinds = pdl.cols_get_indexes_from_names(self.df_lengths, 'tl_mm')
        pdl.col_calculate_new(self.df_lengths, InitData._get_fish_depth, 'fish_depth', colinds) #1 is the index of the db col 'tl_mm'


    def upsert_cor(self):
        '''upserts records to sql'''
        
        
        for i, row in df.iterrows():
            inds = pdl.cols_get_indexes_from_names('sampleid', 'tl_corrected_m')
            rowval = row[inds[0]]
            sql = 'if not exists (select 1 as one from sample_length where sampleid=%i and perspectie_correction=1 and optical_lens_correction=1) ' /
                    ' in
            al.ENGINE.execute(sql)
        

#region ENTRY
def main():
    '''execute if script was entry point'''
    cls = InitData('toshiba', 'imagedb', 'sa', 'GGM290471')
    cls.add_depth()
    cls.perspective_adjust()

#This only executes if this script was the entry point
if __name__ == '__main__':
    #execute my code
    main()
#endregion
