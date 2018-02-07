# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''helper utils for visualisations, 
eg stream and image viewing'''
from enum import Enum as _Enum

from funclib.stringslib import Visible as _Vis
import cv2 as _cv2



class eSpecialKeys(_Enum):
    '''noneprintable chars'''
    return_ = 13
    backspace = 8
    escape = 27
    tab = 9
    space = 32
    unknowable = 0
    none = 255


class KeyBoardInput():
    '''user keyboard input

    key_dic is a dictionary containing
    numbers as keys with the ASCII character

    Also includes the special keys:
        'return', 'backspace', 'escape',
        'tab', 'space', 'unknowable', 'none'
    '''
    _key_dic = _Vis.ord_dict()
    
    for _v in eSpecialKeys:
        _key_dic[_v.value] = _v.name


    @staticmethod
    def get_pressed_key(waitkeyval, is_raw=True):
        '''(int, bool) -> str
        Pass in waitkey result, returning
        the string representation of the key.          

        i:
            return value of waitkey
        is_raw:
            if true, is the raw return value
            otherwise assumes already converted
            to the character ord value,
            e.g. from view.show()

        Returns:
            string representation of keypress,
            also:
                'return', 'backspace', 'escape',
                'tab', 'space', 'unknowable', 'none'
        '''
        if is_raw:
            i = waitkeyval & 255
        return KeyBoardInput._key_dic[i]


    @staticmethod
    def check_pressed_key(keyOrSpecial, waitkeyval):
        '''(str|Enum:SpecialKeys, int) -> bool
        Does the character match the
        return value from opencv's waitkey

        keyOrSpecial:
            keyboard character, e.g. 'W', ' ', or
            the SpecialKeys Enum
        waitkeyval:
            return value from waitkey

        Returns:
            true if match, else false

        Example
        >>>checkwaitkey('k', imshow(img))
        >>>checkwaitkey(eSpecialKeys.return, imshow(img))
        '''
        special = [k for k in eSpecialKeys if k.value == waitkeyval]
        if special:
            return keyOrSpecial == special[0].name or keyOrSpecial == special[0]

        return KeyBoardInput.get_pressed_key(waitkeyval) == str(keyOrSpecial)


def draw_str(dst, x, y, s, color=(255, 255, 255), bottom_left_origin=False):
    '''(ndarray, 2:tuple, str) -> void
    Draw text on dst - ByRef

    dst:
        Image to draw text on, byref
    target:
        draw text on dst at these coordinates.
        tuple is (x, y)
    '''
    _cv2.putText(dst, s, (x, y), _cv2.FONT_HERSHEY_PLAIN,
                1.0, color, lineType=_cv2.LINE_AA, bottomLeftOrigin=bottom_left_origin)
