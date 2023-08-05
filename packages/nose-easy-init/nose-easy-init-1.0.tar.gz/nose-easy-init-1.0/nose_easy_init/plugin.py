import os
import imp

from nose.plugins import Plugin

class NoseEasyInit(Plugin):
    name = 'nose_easy_init'
    enabled = True

    def configure(self, options, conf):
        super(NoseEasyInit, self).configure(options, conf)
        self.enabled = True

    def begin(self):
        nose_init_path = os.environ['NOSE_INIT_PATH']
        imp.load_source('nose_init', nose_init_path)

