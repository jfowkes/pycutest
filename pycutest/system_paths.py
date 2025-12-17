"""
Depending on the platform, find the correct paths to the CUTEst installation
"""

import os, sys
from glob import glob

__all__ = ['check_platform', 'get_cutest_path', 'get_cutest_include_path', 'get_sifdecoder_path', 'get_mastsif_path', 'get_homebrew_gfortran_path', 'get_cache_path']


base_dir = os.getcwd()

homebrew_prefix = None
if sys.platform == 'darwin':  # Mac
    import subprocess
    homebrew_prefix = subprocess.check_output(['brew', '--prefix']).decode('utf-8')[:-1]


def check_platform():
    if sys.platform not in ['linux', 'darwin']:
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
        # First try environment variables for old build system (library is named libcutest.a)
        if 'CUTEST' in os.environ and 'MYARCH' in os.environ:
            cutest_path = os.path.join(os.environ['CUTEST'], 'objects', os.environ['MYARCH'], 'double', 'libcutest.a')
            if os.path.isfile(cutest_path):
                return cutest_path
        # Then try environment variable for new build system (library is named libcutest_double.a)
        if 'CUTEST' in os.environ:
            cutest_path = os.path.join(os.environ['CUTEST'], 'lib', 'libcutest_double.a')
            if os.path.isfile(cutest_path):
                return cutest_path
        # Then try default homebrew location for new build system (library is named libcutest_double.a)
        homebrew_path = os.path.join(homebrew_prefix, 'opt', 'cutest', 'lib', 'libcutest_double.a')
        if os.path.isfile(homebrew_path):
            return homebrew_path
        # Then try default homebrew location for old build system (library is named libcutest.a)
        homebrew_path = os.path.join(homebrew_prefix, 'opt', 'cutest', 'lib', 'libcutest.a')
        if os.path.isfile(homebrew_path):
            return homebrew_path
        # Otherwise try default meson manual install location (library is named libcutest_double.a)
        homebrew_path = os.path.join(homebrew_prefix, 'lib', 'libcutest_double.a')
        if os.path.isfile(homebrew_path):
            return homebrew_path
        # Raise error if cutest library not found
        raise RuntimeError('Could not find CUTEST installation - have CUTEST and/or MYARCH environment variables been set correctly?')
    else:  # Linux
        # First try environment variables for old build system (library is named libcutest.a)
        if 'CUTEST' in os.environ and 'MYARCH' in os.environ:
            cutest_path = os.path.join(os.environ['CUTEST'], 'objects', os.environ['MYARCH'], 'double', 'libcutest.a')
            if os.path.isfile(cutest_path):
                return cutest_path
        # Then try environment variable for new build system (library is named libcutest_double.a)
        if 'CUTEST' in os.environ:
            cutest_path = os.path.join(os.environ['CUTEST'], 'lib', 'libcutest_double.a')
            if os.path.isfile(cutest_path):
                return cutest_path
        # Otherwise try default meson manual install location (library is named libcutest_double.a)
        local_path = os.path.join(os.path.abspath(os.sep), 'usr', 'local', 'lib', 'libcutest_double.a')
        if os.path.isfile(local_path):
            return local_path
        # Raise error if cutest library not found
        raise RuntimeError('Could not find CUTEST installation - have CUTEST and/or MYARCH environment variables been set correctly?')


def get_cutest_include_path():
    if sys.platform == 'darwin':  # Mac
        # First try environment variable (for old and new build systems)
        if 'CUTEST' in os.environ:
            cutest_include_path = os.path.join(os.environ['CUTEST'], 'include')
            if os.path.isfile(os.path.join(cutest_include_path, 'cutest.h')):
                return cutest_include_path
        # Then try default homebrew location
        cutest_include_path = os.path.join(homebrew_prefix, 'include')
        if os.path.isfile(os.path.join(cutest_include_path, 'cutest.h')):
            return cutest_include_path
        # Raise error if cutest header not found
        raise RuntimeError('Could not find CUTEST installation - has CUTEST environment variable been set correctly?')
    else:  # Linux
        # First try environment variable (for old and new build systems)
        if 'CUTEST' in os.environ:
            cutest_include_path = os.path.join(os.environ['CUTEST'], 'include')
            if os.path.isfile(os.path.join(cutest_include_path, 'cutest.h')):
                return cutest_include_path
        # Otherwise try default meson manual install location
        cutest_include_path = os.path.join(os.path.abspath(os.sep), 'usr', 'local', 'include')
        if os.path.isfile(os.path.join(cutest_include_path, 'cutest.h')):
            return cutest_include_path
        # Raise error if cutest header not found
        raise RuntimeError('Could not find CUTEST installation - has CUTEST environment variable been set correctly?')


def get_sifdecoder_path():
    if sys.platform == 'darwin':  # Mac
        # First try environment variable (for old and new build systems)
        if 'SIFDECODE' in os.environ:
            sifdecoder_path = os.path.join(os.environ['SIFDECODE'], 'bin', 'sifdecoder')
            if os.path.isfile(sifdecoder_path):
                return sifdecoder_path
        # Then try default homebrew location
        homebrew_path = os.path.join(homebrew_prefix, 'opt', 'sifdecode', 'bin', 'sifdecoder')
        if os.path.isfile(homebrew_path):
            return homebrew_path
        # Otherwise try default meson manual install location
        meson_path = os.path.join(homebrew_prefix, 'bin', 'sifdecoder')
        if os.path.isfile(meson_path):
            return meson_path
        # Raise error if sifdecoder not found
        raise RuntimeError('Could not find SIFDECODE installation - has SIFDECODE environment variable been set correctly?')
    else:  # Linux
        # First try environment variable (for old and new build systems)
        if 'SIFDECODE' in os.environ:
            sifdecoder_path = os.path.join(os.environ['SIFDECODE'], 'bin', 'sifdecoder')
            if os.path.isfile(sifdecoder_path):
                return sifdecoder_path
        # Otherwise try default meson manual install location
        meson_path = os.path.join(os.path.abspath(os.sep), 'usr', 'local', 'bin', 'sifdecoder')
        if os.path.isfile(meson_path):
            return meson_path
        # Raise error if sifdecoder not found
        raise RuntimeError('Could not find SIFDECODE installation - has SIFDECODE environment variable been set correctly?')


def get_mastsif_path():
    if sys.platform == 'darwin':  # Mac
        # First try environment variable (for old and new build systems)
        if 'MASTSIF' in os.environ:
            mastsif_path = os.environ['MASTSIF']
            if os.path.isdir(mastsif_path):
                return mastsif_path
        # Otherwise try default homebrew location
        homebrew_path = os.path.join(homebrew_prefix, 'opt', 'mastsif', 'share', 'mastsif')
        if os.path.isdir(homebrew_path):
            return homebrew_path
        # Raise error if mastsif not found
        raise RuntimeError('Could not find MASTSIF folder - has MASTSIF environment variable been set correctly?')
    else:  # Linux
        # Always use environment variable (for old and new build systems)
        check_environment_vars_exist(['MASTSIF'])
        mastsif_path = os.environ['MASTSIF']
        if os.path.isdir(mastsif_path):
            return mastsif_path
        # Raise error if mastsif not found
        raise RuntimeError('Could not find MASTSIF folder - has MASTSIF environment variable been set correctly?')


def get_homebrew_gfortran_path():
    if sys.platform == 'darwin':  # Mac
        gfortran_path = max(glob(homebrew_prefix + '/Cellar/gcc/*/lib/gcc/*/'),key=os.path.getmtime)
        if os.path.isdir(gfortran_path):
            return gfortran_path
        # Raise error if GCC not found
        raise RuntimeError('Could not find gfortran - has gcc been installed and linked with homebrew?')


def get_cache_path():
    # Use environment variable if set, otherwise use current directory
    if 'PYCUTEST_CACHE' in os.environ:
        return os.environ['PYCUTEST_CACHE']
    else:
        return base_dir
