#!/usr/bin/env python3

"""

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

from setuptools import setup

# Get package version without "import pycutest" (which requires dependencies to already be installed)
import os
version = {}
with open(os.path.join('pycutest', 'version.py')) as fp:
    exec(fp.read(), version)
__version__ = version['__version__']

setup(
    name='pycutest',
    version=__version__,
    description='A Python wrapper to the CUTEst optimization test environment',
    long_description=open('README.rst').read(),
    author='Jaroslav Fowkes and Lindon Roberts',
    author_email='jaroslav.fowkes@maths.ox.ac.uk',
    url="https://github.com/jfowkes/pycutest/",
    #download_url="https://github.com/jfowkes/pycutest/archive/v0.2.tar.gz",
    packages=['pycutest'],
    license='GNU GPL',
    keywords = "mathematics optimization",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Framework :: IPython',
        'Framework :: Jupyter',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
    install_requires = ['numpy >= 1.11', 'scipy >= 0.17'],
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe = True,
    )

