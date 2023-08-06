import os
import imp
import sys

from nose.plugins import Plugin


class NoseEasyInit(Plugin):
    """
    Nose plugin to load an initialization module before nose collects
    or runs any tests.

    Use one of two environment variables to specify the module:
        NOSE_INIT_MODULE=app.tests.nose_init
        NOSE_INIT_PATH=/path/to/my/nose_init.py

    Note that if both the environment variables are defined, the filesystem
    path, ``NOSE_INIT_PATH``, will take precedence over ``NOSE_INIT_MODULE``.
    """

    name = 'nose_easy_init'
    enabled = True

    def configure(self, options, conf):
        super(NoseEasyInit, self).configure(options, conf)
        self.enabled = True

    def begin(self):
        """Run the user-defined initialization function ``main``"""
        nose_init_module = os.environ.get('NOSE_INIT_MODULE')
        if nose_init_module:
            # Import the user's module from a python dotted-notation module
            __import__(nose_init_module)

        nose_init_path = os.environ.get('NOSE_INIT_PATH')
        if nose_init_path:
            # Import the user's module from a filesystem path
            imp.load_source('nose_init', nose_init_path)

        # Run the user's ``main`` function
        sys.modules[nose_init_module].main()
