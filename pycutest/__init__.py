# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = []

from .version import __version__
__all__ += ['__version__']

from .build_interface import import_problem, clear_cache, all_cached_problems
__all__ += ['import_problem', 'clear_cache', 'all_cached_problems']

from .sifdecode_extras import print_available_sif_params, problem_properties, find_problems
__all__ += ['print_available_sif_params', 'problem_properties', 'find_problems']

from .problem_class import CUTEstProblem
__all__ += ['CUTEstProblem']

# When PyCUTEst is imported, run some basic installation checks
from .system_paths import check_platform, get_cutest_path, get_sifdecoder_path, get_mastsif_path

check_platform()
get_cutest_path()  # don't care about the output for now, just want to see if it raises errors
get_sifdecoder_path()  # don't care about the output for now, just want to see if it raises errors
get_mastsif_path()  # don't care about the output for now, just want to see if it raises errors

import os, warnings
if not 'PYCUTEST_CACHE' in os.environ:
    warnings.warn("the PYCUTEST_CACHE environment variable is not set; current folder will be used for caching.", RuntimeWarning)
else:
    if not os.path.isdir(os.environ['PYCUTEST_CACHE']):
        raise ImportError("Cache directory %s does not exist" % os.environ['PYCUTEST_CACHE'])
