#!/usr/bin/env python

"""
Main routines for building and managing interfaces
"""

# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

import os, shutil, sys
import subprocess
from glob import glob
import warnings

from .system_paths import get_cache_path, get_sifdecoder_path
from .c_interface import itf_c_source
from .install_scripts import get_setup_script
from .python_interface import get_init_script
from .problem_class import CUTEstProblem

__all__ = ['import_problem', 'clear_cache', 'all_cached_problems']

# The cache is treated as its own Python module:
CACHE_SUBFOLDER = 'pycutest_cache_holder'

def params_to_string(params):
    # Convert a dictionary of SIF parameters to a sensible string representation (used for folder names)
    keys = sorted(list(params.keys()))
    param_str = ''
    for k in keys:
        param_str += '%s%g_' % (k, params[k])
    param_str = param_str.rstrip('_')
    return param_str


def get_problem_directory(problemName, sifParams=None, saved_with_param_name=True):
    # Get the folder where a problem is/will be saved
    cache_path = get_cache_path()
    if saved_with_param_name and sifParams is not None:
        return os.path.join(cache_path, CACHE_SUBFOLDER, '%s_%s' % (problemName, params_to_string(sifParams)))
    else:
        return os.path.join(cache_path, CACHE_SUBFOLDER, problemName)


def is_cached(cachedName, sifParams=None):
    """
    Return ``True`` if a problem is in cache.

    Keyword arguments:

    * *cachedName* -- cache entry name
    """
    problemDir = get_problem_directory(cachedName, sifParams=sifParams)
    return os.path.isdir(problemDir)


def clear_cache(problemName, sifParams=None):
    """
    Deletes a saved problem.

    :param problemName: problem name
    :param sifParams: sif parameters used for compilation
    """
    if not is_cached(problemName, sifParams=sifParams):
        return  # nothing to do

    problemDir = get_problem_directory(problemName, sifParams=sifParams)
    # print('Problem dir = %s' % problemDir)

    # See if a directory with problem's name exists
    if os.path.isdir(problemDir):
        # It exists, delete it.
        shutil.rmtree(problemDir, True)
    elif os.path.isfile(problemDir):
        # It is a file, delete it.
        os.remove(problemDir)


def prepare_cache(cachedName, sifParams=None):
    """
    Prepares a cache entry.
    If an entry already exists it is deleted first.

    Keyword arguments:

    * *cachedName* -- cache entry name
    """

    # The directory with test function entries
    pycutestDir = os.path.join(get_cache_path(), CACHE_SUBFOLDER)

    # The problem's cache entry
    problemDir = get_problem_directory(cachedName, sifParams=sifParams)

    # See if a folder named pycutest exists in the cache path.
    if not os.path.isdir(pycutestDir):
        # Create it. If this fails, give up. The user should delete manualy the
        # offending file which prevents the creation of a directory.
        os.mkdir(pycutestDir)

    # See in pycutestDir if there is an __init__.py file.
    initfile=os.path.join(pycutestDir, '__init__.py')
    if not os.path.isfile(initfile):
        # Create it
        f=open(initfile, 'w+')
        f.write("#PyCUTEst cache initialization file\n")
        f.close()

    # Remove old entry
    clear_cache(cachedName)

    # Create folder with problem's name
    os.mkdir(problemDir)
    return


def decode_and_compile_problem(problemName, destination=None, sifParams=None, sifOptions=None, quiet=True):
    """
    Call sifdecode on given problem and compile the resulting .f files.
    Use gfortran with ``-fPIC`` option for compiling.
    Collect the resulting object file names and return them.
    This function is OS dependent. Currently works only for Linux and MacOS.

    Keyword arguments:

    * *problemName* -- CUTEst problem name
    * *destination* -- the name under which the compiled problem interface is stored in the cache
      If not given problemName is used.
    * *sifParams* -- parameters passed to sifdecode using the ``-param`` command line option
      given in the form of a dictionary with parameter name as key. Values
      are converted to strings using :func:`str` and every parameter contributes
      ``-param key=str(value)`` to the sifdecode's command line options.
    * *sifOptions* -- additional options passed to sifdecode given in the form of a list of strings.
    * *quiet* -- supress output (default ``True``)

    *destination* must not contain dots because it is a part of a Python module name.
    """

    # Default destination
    if destination is None:
        destination=problemName

    # The problem's cache entry
    problemDir = get_problem_directory(destination, sifParams=sifParams)

    # Remember current work directory and go to cache
    try:
        fromDir = os.getcwd()
    except FileNotFoundError:
        fromDir = None
    os.chdir(problemDir)

    # Additional args
    args=[]

    # Handle params
    if sifParams is not None:
        for (key, value) in sifParams.items():
            if type(key) is not str and type(key) is not unicode:
                raise Exception("sifParams keys must be strings")
            args+=['-param', key+"="+str(value)]

    # Handle options
    if sifOptions is not None:
        for opt in sifOptions:
            if type(opt) is not str and type(key) is not unicode:
                raise Exception("sifOptions must consist of strings")
            args+=[str(opt)]

    # Call sifdecode
    spawnOK=True
    try:
        # Start sifdecode
        p = subprocess.Popen(
            [get_sifdecoder_path()] + args + [problemName],
            universal_newlines=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        # Collect output
        messages=p.stdout.read()

        # Now wait for the process to finish. If we don't wait p might get garbage-collected before the
        # actual process finishes which can result in a crash of the interpreter.
        retcode=p.wait()

        # Check return code. Nonzero return code means that something has gone bad.
        if retcode!=0:
            spawnOK=False
    except:
        spawnOK=False

    # Print output, check for parameter warnings
    msg_lines = messages.splitlines()
    param_error = None
    for l in msg_lines:
        if 'WARNING' in l:
            param_error = l.replace('WARNING: ', '').replace(' -- skipping', '')
        if not spawnOK or not quiet:
            print(l)
    if not spawnOK:
        clear_cache(problemName, sifParams=sifParams)
        raise RuntimeError('SIFDECODE failed, check output printed above')
    if param_error is not None:
        clear_cache(problemName, sifParams=sifParams)
        raise RuntimeError('SIFDECODE error: %s' % param_error)

    # Collect all .f files
    filelist=glob('*.f')

    # Compile FORTRAN files
    for filename in filelist:
        cmd=['gfortran', '-fPIC', '-c', filename]
        if not quiet:
            for s in cmd:
                print(s, end=' ')
            print()
        if subprocess.call(cmd)!=0:
            raise RuntimeError("gfortran call failed for "+filename)

    # Collect list of all object files (.o)
    objFileList=glob('*.o')

    # Go back to original work directory
    if fromDir is not None:
        os.chdir(fromDir)

    return objFileList


def compile_and_install_interface(problemName, destination=None, sifParams=None, sifOptions=None,
                                efirst=False, lfirst=False, nvfirst=False, quiet=True):
    """
    Compiles and installs the binary interface module.
    Uses distutils to achieve this.
    Assumes :func:`decodeAndCompile` successfully completed its task.
    This function is OS dependent. Currently works only for Linux and MacOS.

    Keyword arguments:

    * *problemName* -- CUTEst problem name
    * *destination* -- the name under which the compiled problem interface is stored in the cache
      If not given problemName is used.
    * *sifParams* -- parameters passed to sifdecode using the ``-param`` command line option
      given in the form of a dictionary with parameter name as key. Values
      are converted to strings using :func:`str` and every parameter contributes::
      ``-param key=str(value)`` to the sifdecode's command line options.
    * *sifOptions* -- additional options passed to sifdecode given in the form of a list of strings.
    * *efirst* -- order equation constraints first (default ``True``)
    * *lfirst* -- order linear constraints first (default ``True``)
    * *nvfirst* -- order nonlinear variables before linear variables
          (default ``False``)
    * *quiet* -- supress output (default ``True``)

    *destination* must not contain dots because it is a part of a Python module name.
    """

    # Default destination
    if destination is None:
        destination=problemName

    # The problem's cache entry
    problemDir = get_problem_directory(destination, sifParams=sifParams)

    # Remember current work directory and go to cache
    fromDir=os.getcwd()
    os.chdir(problemDir)

    # Prepare C source of the interface
    # modulePath = os.path.split(__file__)[0]
    f = open('cutestitf.c', 'w')
    f.write(itf_c_source)
    f.close()

    # Prepare a setup script file
    f = open('setup.py', 'w+')
    f.write(get_setup_script())
    f.close()

    # Prepare -q option for setup.py
    if quiet:
        quietopt=['-q']
    else:
        quietopt=[]

    # Call 'python setup.py build'
    if subprocess.call([sys.executable, 'setup.py']+quietopt+['build'])!=0:
        raise RuntimeError("Failed to build the Python interface module")

    # Call 'python setup.py install --install-lib .'
    if subprocess.call([sys.executable, 'setup.py']+quietopt+['install', '--install-lib', '.'])!=0:
        raise RuntimeError("Failed to install the Python interface module")

    # Create __init__.py
    f=open('__init__.py', 'w+')
    f.write(get_init_script(problemName, efirst, lfirst, nvfirst, sifParams, sifOptions))
    f.close()

    # Go back to original work directory
    os.chdir(fromDir)
    return


def import_problem(problemName, destination=None, sifParams=None, sifOptions=None,
                   efirst=False, lfirst=False, nvfirst=False, quiet=True, drop_fixed_variables=True):
    """
    Prepares a problem interface module, imports and initializes it.

    :param problemName: CUTEst problem name
    :param destination: the name under which the compiled problem interface is stored in the cache (default = ``problemName``)
    :param sifParams: SIF file parameters to use (as dict, keys must be strings)
    :param sifOptions: additional options passed to sifdecode given in the form of a list of strings.
    :param efirst: order equation constraints first (default ``True``)
    :param lfirst: order linear constraints first (default ``True``)
    :param nvfirst: order nonlinear variables before linear variables (default ``False``)
    :param quiet: suppress output (default ``True``)
    :param drop_fixed_variables: in the resulting problem object, are fixed variables hidden from the user (default ``True``)
    :return: a reference to the Python interface class for this problem (class ``pycutest.CUTEstProblem``)
    """

    # Default destination
    if destination is None:
        destination = problemName

    # Build it
    if not is_cached(destination, sifParams=sifParams):
        prepare_cache(destination, sifParams=sifParams)
        objList = decode_and_compile_problem(problemName, destination, sifParams, sifOptions, quiet)
        compile_and_install_interface(problemName, destination, sifParams, sifOptions, efirst, lfirst, nvfirst, quiet)

    if sifParams is not None:
        problemDir = '%s_%s' % (destination, params_to_string(sifParams))
    else:
        problemDir = destination
    # Import the module CACHE_SUBFOLDER.problemDir, and return a wrapper
    return CUTEstProblem(__import__('%s.%s' % (CACHE_SUBFOLDER, problemDir), globals(), locals(), [str(problemDir)]),
                         drop_fixed_variables=drop_fixed_variables)


def all_cached_problems():
    """
    Return a list of all cached problems.

    :return: list of (problemName, sifParams) tuples, where sifParams is a dict
    """
    all_probs = []
    problem_loc = os.path.join(get_cache_path(), CACHE_SUBFOLDER)
    for dir in [name for name in os.listdir(problem_loc) if os.path.isdir(os.path.join(problem_loc, name))]:
        if '__pycache__' in dir:
            continue  # skip
        # Parse folder name (assumes no underscore in problem name)
        if '_' in dir:
            vals = dir.split('_')
            problemName = vals[0]
            sifParams = {}
            for i in range(len(vals)):
                found_value = False
                for split_idx in range(len(vals)):
                    if found_value:
                        break  # end this search
                    var = vals[i][:split_idx]
                    val = vals[i][split_idx:]
                    try:
                        try:
                            val = int(val)
                        except ValueError:
                            val = float(val)
                        sifParams[var] = val
                        found_value = True
                    except ValueError:
                        continue  # next split_idx
            all_probs.append((problemName, sifParams))
        else:
            all_probs.append((dir, None))  # no sifParams
    return all_probs
