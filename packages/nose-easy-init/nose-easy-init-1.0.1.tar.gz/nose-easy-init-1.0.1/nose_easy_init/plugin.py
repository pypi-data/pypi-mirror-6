import os
import imp

from nose.plugins import Plugin

class NoseEasyInit(Plugin):
    """
    Nose plugin to load an initialization module before nose collects
    or runs any tests.

    Use one of two environment variables to specify the module:
        NOSE_INIT_MODULE=app.tests.nose_init
        NOSE_INIT_PATH=/path/to/my/nose_init.py
    """

    name = 'nose_easy_init'
    enabled = True

    def configure(self, options, conf):
        super(NoseEasyInit, self).configure(options, conf)
        self.enabled = True

    def begin(self):
        nose_init_module = os.environ.get('NOSE_INIT_MODULE')
        if nose_init_module:
            __import__(nose_init_module)

        nose_init_path = os.environ.get('NOSE_INIT_PATH')
        if nose_init_path:
            imp.load_source('nose_init', nose_init_path)

