"""
Installation scripts for individual problems
"""

# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

import sys

from .system_paths import get_cutest_path

__all__ = ['get_setup_script']

#
# The setup.py script with a placeholder for platform-dependent part.
#
setupScript="""#!/usr/bin/env python
# (C)2011 Arpad Buermen
# (C)2018 Jaroslav Fowkes, Lindon Roberts
# Licensed under GNU GPL V3

#
# Do not edit. This is a computer-generated file.
#

# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import numpy as np
from glob import glob

#
# OS specific
#

%s

#
# End of OS specific
#

def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration(None, parent_package, top_path)
    config.set_options(
        ignore_setup_xxx_py=True,
        assume_default_configuration=True,
        delegate_options_to_subpackages=True,
        quiet=True,
    )

    # Module
    config.add_extension(
        str('_pycutestitf'),
        [str('cutestitf.c')],
        include_dirs=include_dirs,
        define_macros=define_macros,
        extra_objects=objFileList,
        libraries=libraries,
        library_dirs=library_dirs,
        extra_link_args=extra_link_args,
    )

    return config

# Settings
if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(
        name='PyCUTEst automatic test function interface builder',
        version='1.0',
        description='Builds a CUTEst test function interface for Python.',
        long_description='Builds a CUTEst test function interface for Python.',
        author='Arpad Buermen, Jaroslav Fowkes, Lindon Roberts',
        author_email='arpadb@fides.fe.uni-lj.si, fowkes@maths.ox.ac.uk, robertsl@maths.ox.ac.uk',
        url='',
        platforms='Linux',
        license='GNU GPL',
        packages=[],
        configuration=configuration,
    )
"""

#
# Linux-specific part of setup.py
#
setupScriptLinux="""
define_macros=[('LINUX', None)]
include_dirs=[os.path.join(np.get_include(), 'numpy'), os.path.join(os.environ['CUTEST'], 'include')]
objFileList=glob('*.o')
objFileList.append(os.path.join(os.environ['CUTEST'], 'objects', os.environ['MYARCH'], 'double', 'libcutest.a'))
libraries=['gfortran']
library_dirs=[]
extra_link_args=[]
"""

#
# Mac-specific part of setup.py
#
setupScriptMac="""
define_macros=[('LINUX', None)]
include_dirs=[os.path.join(np.get_include(), 'numpy')]
objFileList=glob('*.o')
objFileList.append('%s')
libraries=['gfortran']
library_dirs=[max(glob('/usr/local/Cellar/gcc/*/lib/gcc/*/'),key=os.path.getmtime),'/usr/local/gfortran/lib/']
extra_link_args=['-Wl,-no_compact_unwind']
""" % get_cutest_path()  # will probably get the homebrew location, but may revert to environment variables


def get_setup_script():
    if sys.platform in ["linux", "linux2"]:
        return setupScript % setupScriptLinux
    else:
        return setupScript % setupScriptMac
