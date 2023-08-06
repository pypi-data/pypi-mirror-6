==============
nose-easy-init
==============

A nose plugin, enabled by default, which executes a user-defined
initialization function prior to nose collecting or running any tests. The
user specifies the python module that contains the initialization function,
``main``, in an environment variable.

Use one of two environment variables to specify the module:

.. code-block:: bash

    NOSE_INIT_MODULE=app.tests.nose_init
    NOSE_INIT_PATH=/path/to/my/app/tests/nose_init.py

Then, run your nose tests as usual.

Example initialization module
-----------------------------

Let's assume that we've named our initialization module ``nose_init.py`` and
saved it in ``/path/to/my/app/tests/nose_init.py``. That file must contain a
``main`` function. For example:

.. code-block:: python

    """
    Initialization script which is imported when ``nosetests`` is run.
    The main function will be executed before any other application code
    is imported.
    """

    def main():
        """nose_easy_init will call this before each ``nosetests`` run."""

        setup_my_test_environment()
        setup_my_test_database()
        etc()

Then, before running ``nosetests``, set one of two environment variables to
specify the module:

.. code-block:: bash

    NOSE_INIT_MODULE=app.tests.nose_init
    NOSE_INIT_PATH=/path/to/my/app/tests/nose_init.py

Note that if both the environment variables are defined, the filesystem path,
``NOSE_INIT_PATH``, will take precedence over ``NOSE_INIT_MODULE``.
