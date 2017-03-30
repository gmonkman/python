# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument

'''Log Processor'''
from .BaseProcessor import BaseProcessor


class LogProcessor(BaseProcessor):
    '''log processor'''
    def before_process(self):
        pass

    def process(self, preview_image_url, original_image_url, search_term):
        print("search term:%s, preview: %s, original: %s" % (search_term, preview_image_url, original_image_url))

    def after_process(self):
        pass
