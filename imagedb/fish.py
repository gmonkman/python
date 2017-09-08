'''stuff to do with the image database'''
from numpy import array as np_array, linalg
from scipy.integrate import quad

from abc import ABC, abstractmethod


class Fish(ABC):
    '''base class to store samples'''

    def __init__(self, length_tl=0):
        '''init class'''
        self.name_latin = ''
        self.name_common = ''
        self.length_tl = length_tl
        self.length_fl = 0
        self.length_sl = 0
        self.max_ventral_dorsal_thickness = 0

    @abstractmethod
    def get_max_depth(self):
        '''(double)->double
        given the total length, get the depth
       '''

    @abstractmethod
    def lalg_length_equals_depth(self, reverse):
        '''get the parameters of the linear equation for the length-depth relationship
        length = depth + c
        Return x,c
        '''

    @abstractmethod
    def function_over_interval(self):
        '''estimate the total length based on the integral mid point depth
        of the fish
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
    '''polymorphic class functions for fish species, aubclassed from Fish'''

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
        return self.species.get_max_depth(reverse)

    def function_over_interval(self):
        '''Given a function which represents the dorsal fish shape
        return the function mean between the bounds x[0,1]
        Each fish will have a different function is dictated by their different dorsal profile
        The function will need to be determined empirically for each fish
        '''
        return self.species.function_over_interval()


class Bass(Fish):
    '''bass'''

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

        return self.length_tl * a + c

    def lalg_length_equals_depth(self, reverse=False):
        '''get the parameters of the linear equation for the length-depth relationship
        length = a*Depth + c
        Return x,c
        If reverse use:
        depth = a*Length + c
        '''
        if reverse:
            # setup the matrix in the form ay + bx = c
            a = np_array([[10, 34.3], [10, 54.3]])
            c = np_array([280, 427.5])
        else:
            a = np_array([[280, 10], [427.5, 10]])
            c = np_array([34.3, 54.3])
        ret = linalg.solve(a, c)
        return (ret[0], ret[1])


# region ENTRY
def main():
    '''execute if script was entry point'''
    pass


# This only executes if this script was the entry point
if __name__ == '__main__':
    # execute my code
    main()
# endregion
