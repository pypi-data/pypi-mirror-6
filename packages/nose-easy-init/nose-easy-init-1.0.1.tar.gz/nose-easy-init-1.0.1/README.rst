==============
nose-easy-init
==============

A nose plugin, enabled by default, which imports an initialization script given
by an environment variable. This script will be imported before nose collects
or runs any tests.

Use one of two environment variables to specify the module:

.. code-block:: bash

        NOSE_INIT_MODULE=app.tests.nose_init
        NOSE_INIT_PATH=/path/to/my/nose_init.py

