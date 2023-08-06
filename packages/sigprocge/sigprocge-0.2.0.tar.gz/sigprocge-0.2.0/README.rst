Python utilities for the SigProC cluster
========================================

Installation
------------

Installation is via pip:

.. code:: console

    $ pip install sigprocge

Or, for the latest development version:

.. code:: console

    $ pip install git+http://github.com/sigproc/python-sigprocge

OpenCL
------

The ``sigproc.cl`` module contains functions allowing automatic selection of an
appropriate OpenCL context for the Grid Engine queue your job has been
scheduled in. See the ``examples/opencl_example_job.sh`` and
``examples/opencl_example.py`` files.
