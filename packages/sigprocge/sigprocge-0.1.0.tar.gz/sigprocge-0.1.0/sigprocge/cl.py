"""Utility functions for using OpenCL on the SigProC grid engine stack.

"""
import logging
import os

import pyopencl as cl

__all__ = [
    'OpenCLContextCreationError',
    'create_opencl_context',
]

log = logging.getLogger(__name__)

class OpenCLContextCreationError(RuntimeError):
    """An error relating to the creation of an OpenCL context."""
    pass

def create_opencl_context():
    """Create an appropriate OpenCL context for accelerated compute on the
    SigProC grid engine GPU cluster.

    Should the PYOPENCL_CTX environment variable be set, the default PyOpenCL
    device creation mechanism is used.

    Should the X_SGE_CUDA_DEVICE environment variable be set, it is used as a
    0-based index into the list of CUDA-based OpenCL devices.

    If none of the above apply, the default PyOpenCL device creation mechanism
    is used.

    Raises *OpenCLContextCreationError* if there is an error creating a
    context, for example due to an invalid value being specified in the
    environment variables above.

    """
    log.info('Creating OpenCL context')

    if 'PYOPENCL_CTX' in os.environ:
        log.info('PYOPENCL_CTX is set to "{0}"'.format(os.environ['PYOPENCL_CTX']))
        log.info('Using default PyOpenCL context selection')
        return cl.create_some_context(interactive=False)

    if 'X_SGE_CUDA_DEVICE' in os.environ:
        cuda_device = int(os.environ['X_SGE_CUDA_DEVICE'])
        log.info('X_SGE_CUDA_DEVICE is set to "{0}"'.format(cuda_device))

        # Find CUDA platforms
        platforms = [p for p in cl.get_platforms() if 'CUDA' in p.name]
        if len(platforms) == 0:
            log.error('No CUDA-based OpenCL platforms found')
            raise OpenCLContextCreationError('No CUDA-based OpenCL platforms found')

        # Find CUDA devices
        devices = []
        for p in platforms:
            devices.extend(p.get_devices())

        log.info('Found {0} CUDA-based OpenCL device(s)'.format(len(devices)))
        return cl.Context(devices=[devices[cuda_device]])

    log.warn('No OpenCL device specified. Using default PyOpenCL strategy')
    return cl.create_some_context(interactive=False)

