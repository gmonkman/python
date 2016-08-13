#pylint: skip-file
'''test stuff focalpermute'''

import numpy as np

import mediandistance as md
import funclib.statslib as statslib

#region mediandistance
def median_distance():
    a = np.arange(25).reshape(5,5).astype(float)
    a[0][0] = np.nan
    a[0][1] = 0
    a = md.bin_array_quartile(a)
    print a
    z=1

def md_get_results():
    md.get_results()
    z = 1
#endregion

def kappas():
    md.kappas()

def contingency():
    tbl = md.get_matrix_data(md.EnumResultsType.contingency, md.EnumSurvey.fmm, md.EnumKeys.crispDirected_crispMine)
    #x = statslib.contingency_conditional(tbl, bycol=True)
    y = statslib.contingency_conditional(tbl, bycol=False)

#region Module Level Calls
#md_get_results()
#kappas()
contingency()
#endregion