'''base processor'''
from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    '''docstr'''
    @abstractmethod
    def before_process(self):
        '''docs'''
        pass

    @abstractmethod
    def process(self, preview_image_url, original_image_url, search_term):
        '''docs'''
        pass

    @abstractmethod
    def after_process(self):
        '''docs'''
        pass
