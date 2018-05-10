'''stuff to do with the image database'''
import numpy as _np
from numpy import linalg as _linalg
from scipy.stats import linregress as _linregress

from abc import ABC as _ABC
from abc import abstractmethod as _abstractmethod


class Fish(_ABC):
    '''base class to store samples'''

    def __init__(self, length_tl=0):
        '''init class'''
        self.name_latin = ''
        self.name_common = ''
        self.length_tl = length_tl
        self.length_fl = 0
        self.length_sl = 0
        self.max_ventral_dorsal_thickness = 0

    @_abstractmethod
    def get_max_depth(self):
        '''(double)->double
        given the total length, get the depth
       '''

    @_abstractmethod
    def lalg_length_equals_depth(self, reverse):
        '''get the parameters of the linear equation for the length-depth relationship
        length = depth + c
        Return x,c
        '''


    @staticmethod
    def length_from_depth(measure, coeff, const):
        '''(float, float, float, bool, float)
        Given a known measurement, calculate a linearly related measurement
        based on the linear coefficient and constant
        eg.
        y = 0.1x + 0.01 relates depth to length
        Pass in a length of 100mm, would return 100*0.1 + 0.01 (10.1mm) meaing our fish of 100cm
        is 10.1cm deep.
        '''
        return measure * coeff + const


# define an array of functions which will accept other 'species' classes
class FishActions(object):
    '''polymorphic class functions for fish species, subclassed from Fish'''

    def __init__(self, species):
        '''species is a fish class (polymorphic)
        '''
        self.species = species

    def get_max_depth(self):
        '''get max fish depth based on the length and species
        '''
        return self.species.get_max_depth()

    def lalg_length_equals_depth(self, reverse=False):
        '''get the parameters of the linear equation for the length-depth relationship
        length = depth + c
        Return x,c
        '''
        return self.species.lalg_length_equals_depth(reverse)



class Bass(Fish):
    '''
    Profile mean height is the mean height of the fish profile
    calculated from a binary image of the fish profile in
    scripts_misc/shape_area.py
    '''
    profile_mean_height = 0.598

    def __init__(self, length_tl=0):
        # keep python 2.7 compat, Python 3 only would be
        # super().__init__(length_tl)
        super(Bass, self).__init__(length_tl)

    def get_max_depth(self):
        '''(float)->float
        given a length in mm, get maximum fish depth in mm
        REF: "Quality outline of European sea bass Dicentrarchus labrax reared in Italy: shelf life, edible yield, nutritional and dietetic traits"
        '''
        a, c = self.lalg_length_equals_depth(False)
        if self.length_tl is None:
            return None
        return self.length_tl * a + c



    def lalg_length_equals_depth(self, reverse=False):
        '''() -> float, float
        Get the parameters of the linear equation for the length-depth relationship.

        By default, predicts the parameters to get width from tl
        i.e. width = a*tl + c

        If reverse, predicts the parameters to get tl from width.
        i.e. tl = a*width + c
        '''
        if reverse: #params to predict tl from width
            a = _np.array([[34.3, 10], [54.3, 10]])
            c = _np.array([280, 427.5])
        else: #params to predict width from tl
            a = _np.array([[280, 10], [427.5, 10]])
            c = _np.array([34.3, 54.3])
        ret = _linalg.solve(a, c)
        return (ret[0], ret[1])


class Dab(Fish):
    '''
    Profile mean height is the mean height of the fish profile
    calculated from a binary image of the fish profile in
    scripts_misc/shape_area.py
    '''
    #TODO Sort this for DAB
    profile_mean_height = 0.505
    _tl = [197, 193, 187, 186, 171, 164, 176, 194, 156, 157, 154, 145, 145, 143, 123, 134, 102, 133, 123, 102, 173]
    _width = [15, 13.7, 13, 14.4, 12.1, 10.4, 12, 14.1, 9.7, 10.1, 10, 9.6, 9.5, 9.6, 8, 9, 6.3, 8.9, 7.3, 6.5, 12.4]
    assert len(_tl) == len(_width)

    def __init__(self, length_tl=0):
        # keep python 2.7 compat, Python 3 only would be
        # super().__init__(length_tl)
        super(Dab, self).__init__(length_tl)

    def get_max_depth(self):
        '''(float)->float
        given a length in mm, get maximum fish depth in mm
        REF:
        '''
        a, c = self.lalg_length_equals_depth(False)
        if self.length_tl is None:
            return None
        return self.length_tl * a + c



    def lalg_length_equals_depth(self, reverse=False):
        '''() -> float, float
        get the parameters of the linear equation for the length-depth relationship.

        By default, predicts the parameters to get width from the length.
        i.e. width = a*length + c

        If reverse, predicts the parameters to get length from width.
        i.e. length = a*width + c
        '''

        if reverse: #length = a*width + c
            res = _linregress(Dab._width, Dab._tl)
        else: #width = a*length + c
            res = _linregress(Dab._tl, Dab._width)

        return (res.slope, res.intercept)



# region ENTRY
def main():
    '''execute if script was entry point'''
    pass


# This only executes if this script was the entry point
if __name__ == '__main__':
    # execute my code
    main()
# endregion
