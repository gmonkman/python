# pylint: skip-file
'''main init for dliblib package'''

__all__ = ['ini', 'vgg2xml']

VALID_LABELS = [str(lbl).zfill(2) for lbl in range(1, 21)]