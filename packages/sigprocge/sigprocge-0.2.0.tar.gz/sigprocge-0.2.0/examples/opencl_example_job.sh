#!/bin/bash
#
# Submit this script via qsub. IMPORTANT: make sure that the working directory
# is the one containing this script:
#
#   $ cd /path/to/this/job
#   $ qsub opencl_example_job.sh
#
# Specify that this script needs to be run in bash
#$-S /bin/bash
#
# Specify that we want CUDA available
#$-l qp=cuda

# Activate pyenv
echo "Activating pyenv..."
eval "$( pyenv init - )"

# Switch to appropriate python version
echo "Activating python virtualenv..."
pyenv activate venv3.4

# Show Python version
echo "Using python version: $( python --version )"

# Run python script. Note that this requires the wokring directory
# to be set correctly.
echo "Running job"
python "opencl_example.py"

