"""
Installation scripts for individual problems
"""

import sys

from .system_paths import get_cutest_path

__all__ = ['get_setup_script']

#
# The setup.py script with a placeholder for platform-dependent part.
#
setupScript="""#!/usr/bin/env python
# (C)2011 Arpad Buermen
# (C)2022 Jaroslav Fowkes, Lindon Roberts
# Licensed under GNU GPL V3

#
# Do not edit. This is a computer-generated file.
#

import os

import numpy as np
from glob import glob
from setuptools import setup, Extension, find_packages

#
# OS specific
#

%s

#
# End of OS specific
#

# Module
module = Extension(
    str('_pycutestitf'),
    sources=[str('cutestitf.c')],
    include_dirs=include_dirs,
    define_macros=define_macros,
    extra_objects=objFileList,
    libraries=libraries,
    library_dirs=library_dirs,
    extra_link_args=extra_link_args,
)

# Settings
setup(
    name='PyCUTEst automatic test function interface builder',
    version='1.5.0',
    description='Builds a CUTEst test function interface for Python.',
    long_description='Builds a CUTEst test function interface for Python.',
    author='Arpad Buermen, Jaroslav Fowkes, Lindon Roberts',
    author_email='arpadb@fides.fe.uni-lj.si, fowkes@maths.ox.ac.uk, robertsl@maths.ox.ac.uk',
    url='',
    platforms='Linux',
    license='GNU GPL',
    packages=find_packages(),
    ext_modules=[module],
)
"""

#
# Linux-specific part of setup.py
#
setupScriptLinux="""
define_macros=[('LINUX', None)]
include_dirs=[np.get_include(),os.environ['CUTEST']+'/include/']
objFileList=glob('*.o')
objFileList.append(os.environ['CUTEST']+'/objects/'+os.environ['MYARCH']+'/double/libcutest.a')
libraries=['gfortran']
library_dirs=[]
extra_link_args=[]
"""

#
# Mac-specific part of setup.py
#
setupScriptMac="""
import subprocess
# extract the homebrew prefix
homebrew_prefix = subprocess.check_output(['brew', '--prefix']).decode('utf-8')[:-1]
define_macros=[('LINUX', None)]
include_dirs=[np.get_include(),os.environ['CUTEST']+'/include/']
objFileList=glob('*.o')
objFileList.append('%s')
libraries=['gfortran']
library_dirs=[max(glob(homebrew_prefix + '/Cellar/gcc/*/lib/gcc/*/'),key=os.path.getmtime)]
extra_link_args=['-Wl,-no_compact_unwind']
""" % get_cutest_path()  # will probably get the homebrew location, but may revert to environment variables


def get_setup_script():
    if sys.platform == "linux":
        return setupScript % setupScriptLinux
    else:
        return setupScript % setupScriptMac
