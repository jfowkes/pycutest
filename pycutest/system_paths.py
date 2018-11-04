"""
Depending on the platform, find the correct paths to the CUTEst installation
"""

# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

import os, sys

__all__ = ['check_platform', 'get_cutest_path', 'get_sifdecoder_path', 'get_mastsif_path', 'get_cache_path']


base_dir = os.getcwd()

def check_platform():
    if sys.platform not in ['linux', 'linux2', 'darwin']:
        raise ImportError("Unsupported platform: " + sys.platform)
    return


def check_environment_vars_exist(vars):
    # Check environment variables are set
    for env_var in vars:
        if not env_var in os.environ:
            raise ImportError("Environment variable %s not set - have you installed CUTEst correctly?" % env_var)
    return


def get_cutest_path():
    if sys.platform == 'darwin':  # Mac
        # First try environment variables, otherwise use default homebrew location
        if 'CUTEST' in os.environ and 'MYARCH' in os.environ:
            cutest_path = os.path.join(os.environ['CUTEST'], 'objects', os.environ['MYARCH'], 'double', 'libcutest.a')
            if os.path.isfile(cutest_path):
                return cutest_path
        homebrew_path = os.path.join('usr', 'local', 'opt', 'cutest', 'lib', 'libcutest.a')  # /usr/local/opt/cutest/lib/libcutest.a
        if os.path.isfile(homebrew_path):
            return homebrew_path
        else:
            raise RuntimeError('Could not find CUTEST installation - have CUTEST and MYARCH environment variables been set correctly?')
    else:  # Linux
        check_environment_vars_exist(['CUTEST', 'MYARCH'])
        cutest_path = os.path.join(os.environ['CUTEST'], 'objects', os.environ['MYARCH'], 'double', 'libcutest.a')
        if os.path.isfile(cutest_path):
            return cutest_path
        else:
            raise RuntimeError('Could not find CUTEST installation - have CUTEST and MYARCH environment variables been set correctly?')


def get_sifdecoder_path():
    if sys.platform == 'darwin':  # Mac
        # First try environment variables, otherwise use default homebrew location
        if 'SIFDECODE' in os.environ:
            sifdecoder_path = os.path.join(os.environ['SIFDECODE'], 'bin', 'sifdecoder')
            if os.path.isfile(sifdecoder_path):
                return sifdecoder_path
        homebrew_path = os.path.join('usr', 'local', 'opt', 'sifdecode', 'bin', 'sifdecoder')  # /usr/local/opt/sifdecode/bin/sifdecoder
        if os.path.isfile(homebrew_path):
            return homebrew_path
        else:
            raise RuntimeError('Could not find SIFDECODE installation - has SIFDECODE environment variable been set correctly?')
    else:  # Linux
        check_environment_vars_exist(['SIFDECODE'])
        sifdecoder_path = os.path.join(os.environ['SIFDECODE'], 'bin', 'sifdecoder')
        if os.path.isfile(sifdecoder_path):
            return sifdecoder_path
        else:
            raise RuntimeError('Could not find SIFDECODE installation - has SIFDECODE environment variable been set correctly?')


def get_mastsif_path():
    if sys.platform == 'darwin':  # Mac
        # First try environment variables, otherwise use default homebrew location
        if 'MASTSIF' in os.environ:
            mastsif_path = os.environ['MASTSIF']
            if os.path.isdir(mastsif_path):
                return mastsif_path
        homebrew_path = os.path.join('usr', 'local', 'opt', 'mastsif', 'share', 'mastsif')  # /usr/local/opt/mastsif/share/mastsif
        if os.path.isdir(homebrew_path):
            return homebrew_path
        else:
            raise RuntimeError('Could not find MASTSIF folder - has MASTSIF environment variable been set correctly?')
    else:  # Linux
        check_environment_vars_exist(['MASTSIF'])
        mastsif_path = os.environ['MASTSIF']
        if os.path.isdir(mastsif_path):
            return mastsif_path
        else:
            raise RuntimeError('Could not find MASTSIF folder - has MASTSIF environment variable been set correctly?')


def get_cache_path():
    if 'PYCUTEST_CACHE' in os.environ:
        return os.environ['PYCUTEST_CACHE']
    else:
        return base_dir
