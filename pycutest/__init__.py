# Set PyCUTEst version number
__version__ = '1.7.1'

# Define submodules to expose on wildcard imports
__all__ = []

from .build_interface import import_problem, clear_cache, all_cached_problems
__all__ += ['import_problem', 'clear_cache', 'all_cached_problems']

from .sifdecode_extras import print_available_sif_params, problem_properties, find_problems
__all__ += ['print_available_sif_params', 'problem_properties', 'find_problems']

from .problem_class import CUTEstProblem
__all__ += ['CUTEstProblem']

# When PyCUTEst is imported, run some basic installation checks
from .system_paths import check_platform, get_cutest_path, get_sifdecoder_path, get_mastsif_path, get_cache_path

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


# Add cache to PYTHONPATH at runtime (avoids need to do this upon package installation)
import sys
try:
    # Don't add to path more than once
    sys.path.index(get_cache_path())
except ValueError:
    sys.path.append(get_cache_path())
